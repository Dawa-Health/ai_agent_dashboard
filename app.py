import traceback
import os
import json
import re
import time
from threading import Lock
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from urllib.parse import quote, urlencode
from urllib import request as urllib_request
from urllib.error import HTTPError, URLError
try:
    import requests
except ModuleNotFoundError:
    class SimpleResponse:
        def __init__(self, status_code, text):
            self.status_code = status_code
            self.text = text
            self.ok = 200 <= status_code < 300

        def json(self):
            return json.loads(self.text or "{}")

        def raise_for_status(self):
            if not self.ok:
                raise RuntimeError(f"HTTP request failed with status {self.status_code}: {self.text}")

    class RequestsFallback:
        @staticmethod
        def get(url, params=None, headers=None, timeout=None):
            if params:
                separator = "&" if "?" in url else "?"
                url = f"{url}{separator}{urlencode(params)}"
            return RequestsFallback._request("GET", url, headers=headers, timeout=timeout)

        @staticmethod
        def post(url, headers=None, json=None, timeout=None):
            body = None
            request_headers = dict(headers or {})
            if json is not None:
                body = globals()["json"].dumps(json).encode("utf-8")
                request_headers.setdefault("Content-Type", "application/json")
            return RequestsFallback._request("POST", url, headers=request_headers, data=body, timeout=timeout)

        @staticmethod
        def _request(method, url, headers=None, data=None, timeout=None):
            req = urllib_request.Request(url, data=data, headers=headers or {}, method=method)
            try:
                with urllib_request.urlopen(req, timeout=timeout) as response:
                    return SimpleResponse(response.status, response.read().decode("utf-8"))
            except HTTPError as exc:
                return SimpleResponse(exc.code, exc.read().decode("utf-8"))
            except URLError as exc:
                raise RuntimeError(str(exc)) from exc

    requests = RequestsFallback()
from flask import Flask, request, jsonify, send_from_directory, abort

app = Flask(__name__)

# ------------------------------------------------
# 🔑 WhatsApp Cloud API credentials

WHATSAPP_TOKEN = "********************"
PHONE_NUMBER_ID = "********************"  # from Meta dashboard
VERIFY_TOKEN = "BOT"  
# ------------------------------------------------

UPSTASH_REDIS_URL = os.environ.get("UPSTASH_REDIS_URL", "********************")
UPSTASH_REDIS_TOKEN = os.environ.get("UPSTASH_REDIS_TOKEN", "********************")

QR_CLINICS = [
    {"name": "Mandebvu Clinic", "color": "#09f128"},
    {"name": "Avondale Clinic", "color": "#0000FF"},
    {"name": "Mandebvu Pharmacy", "color": "#FFFF00"},
    {"name": "N'gombe Clinic", "color": "#FF5F15"},
    {"name": "Chelstone Clinic", "color": "#D3D3D3"},
]

QR_SOURCES = ["Poster 1", "Poster 2", "Flyer"]
QR_SOURCE_PATTERNS = {
    "Poster 1": re.compile(r"poster\s*1", re.IGNORECASE),
    "Poster 2": re.compile(r"poster\s*2", re.IGNORECASE),
    "Flyer": re.compile(r"flyer", re.IGNORECASE),
}

QR_CACHE_TTL_SECONDS = int(os.environ.get("QR_CACHE_TTL_SECONDS", "45"))
QR_CACHE = {"payload": None, "expires_at": 0}
QR_CACHE_LOCK = Lock()


def upstash_headers():
    return {"Authorization": f"Bearer {UPSTASH_REDIS_TOKEN}"}


def scan_redis_keys(pattern):
    keys = []
    cursor = "0"

    while True:
        response = requests.get(
            f"{UPSTASH_REDIS_URL}/scan/{cursor}",
            params={"match": pattern, "count": 500},
            headers=upstash_headers(),
            timeout=15,
        )
        response.raise_for_status()
        payload = response.json()
        result = payload.get("result") or ["0", []]
        cursor = str(result[0])
        chunk = result[1] if len(result) > 1 else []
        if isinstance(chunk, list):
            keys.extend(chunk)
        if cursor == "0":
            break

    return list(dict.fromkeys(keys))


def read_redis_value(key):
    response = requests.get(
        f"{UPSTASH_REDIS_URL}/get/{quote(str(key), safe='')}",
        headers=upstash_headers(),
        timeout=15,
    )
    response.raise_for_status()
    payload = response.json()
    return payload.get("result")


def read_redis_values(keys):
    if not keys:
        return {}

    try:
        response = requests.post(
            f"{UPSTASH_REDIS_URL}/pipeline",
            headers={**upstash_headers(), "Content-Type": "application/json"},
            json=[["GET", key] for key in keys],
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
        if isinstance(payload, list):
            return {
                key: item.get("result") if isinstance(item, dict) else None
                for key, item in zip(keys, payload)
            }
    except Exception as exc:
        print(f"QR analytics pipeline fallback: {exc}")

    values = {}
    max_workers = min(12, max(1, len(keys)))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {executor.submit(read_redis_value, key): key for key in keys}
        for future in as_completed(future_map):
            key = future_map[future]
            try:
                values[key] = future.result()
            except Exception:
                values[key] = None
    return values


def parse_json_value(raw_value):
    if raw_value is None:
        return None
    if isinstance(raw_value, dict):
        return raw_value
    if not isinstance(raw_value, str):
        return None
    try:
        return json.loads(raw_value)
    except Exception:
        return None


def detect_clinic(source_text, record):
    haystack_parts = [str(source_text or "")]
    for field in ("clinic", "clinicName", "clinic_name", "facility", "location"):
        value = record.get(field)
        if value:
            haystack_parts.append(str(value))
    haystack = " ".join(haystack_parts).lower()

    for clinic in QR_CLINICS:
        if clinic["name"].lower() in haystack:
            return clinic["name"]

    return None


def detect_source_type(source_text):
    text = str(source_text or "")
    for source_name, pattern in QR_SOURCE_PATTERNS.items():
        if pattern.search(text):
            return source_name
    return None


def build_qr_analytics(force_refresh=False):
    now = time.time()
    with QR_CACHE_LOCK:
        if not force_refresh and QR_CACHE["payload"] and QR_CACHE["expires_at"] > now:
            cached_payload = dict(QR_CACHE["payload"])
            cached_payload["cached"] = True
            cached_payload["cacheAgeSeconds"] = max(0, int(QR_CACHE["expires_at"] - now))
            return cached_payload

    counts = {clinic["name"]: {source: 0 for source in QR_SOURCES} for clinic in QR_CLINICS}
    stats = {
        "totalRecords": 0,
        "validRecords": 0,
        "malformedRecords": 0,
        "matchedRecords": 0,
    }

    keys = scan_redis_keys("referrals*")
    stats["totalRecords"] = len(keys)

    if not keys:
        payload = {
            "ok": True,
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "cached": False,
            "cacheTtlSeconds": QR_CACHE_TTL_SECONDS,
            "totalRecords": 0,
            "validRecords": 0,
            "malformedRecords": 0,
            "matchedRecords": 0,
            "clinics": QR_CLINICS,
            "sources": QR_SOURCES,
            "counts": counts,
        }
        with QR_CACHE_LOCK:
            QR_CACHE["payload"] = payload
            QR_CACHE["expires_at"] = time.time() + QR_CACHE_TTL_SECONDS
        return payload

    values = read_redis_values(keys)
    for raw_value in values.values():
        record = parse_json_value(raw_value)
        if not isinstance(record, dict):
            stats["malformedRecords"] += 1
            continue

        stats["validRecords"] += 1
        source_text = record.get("source", "")
        clinic_name = detect_clinic(source_text, record)
        source_type = detect_source_type(source_text)

        if clinic_name and source_type:
            counts[clinic_name][source_type] += 1
            stats["matchedRecords"] += 1

    payload = {
        "ok": True,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "cached": False,
        "cacheTtlSeconds": QR_CACHE_TTL_SECONDS,
        **stats,
        "clinics": QR_CLINICS,
        "sources": QR_SOURCES,
        "counts": counts,
    }

    with QR_CACHE_LOCK:
        QR_CACHE["payload"] = payload
        QR_CACHE["expires_at"] = time.time() + QR_CACHE_TTL_SECONDS

    return payload


@app.route('/api/qr-analytics')
def qr_analytics():
    try:
        force_refresh = str(request.args.get("refresh", "")).lower() in {"1", "true", "yes"}
        return jsonify(build_qr_analytics(force_refresh=force_refresh)), 200
    except Exception as exc:
        print(f"QR analytics error: {exc}")
        print(traceback.format_exc())
        zero_counts = {clinic["name"]: {source: 0 for source in QR_SOURCES} for clinic in QR_CLINICS}
        return jsonify({
            "ok": False,
            "error": "Could not load referral analytics right now.",
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "totalRecords": 0,
            "validRecords": 0,
            "malformedRecords": 0,
            "matchedRecords": 0,
            "clinics": QR_CLINICS,
            "sources": QR_SOURCES,
            "counts": zero_counts,
        }), 200


# Serve chats.html when opening http://127.0.0.1:5000/
@app.route('/')
def index():
    return send_from_directory('.', 'chats.html')


@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory('css', filename)


@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('js', filename)


@app.route('/img/<path:filename>')
def serve_img(filename):
    return send_from_directory('img', filename)


@app.route('/<path:filename>')
def serve_page(filename):
    if filename.endswith('.html'):
        return send_from_directory('.', filename)
    abort(404)


# 🔹 WhatsApp webhook (GET = verify, POST = incoming messages)
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Verify webhook
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return 'Forbidden', 403

    elif request.method == 'POST':
        try:
            data = request.get_json()
            print(f"Incoming webhook data: {data}")

            if data.get('object') == 'whatsapp_business_account':
                for entry in data.get('entry', []):
                    for change in entry.get('changes', []):
                        if change.get('field') == 'messages':
                            value = change.get('value')
                            if value:
                                message = value.get('messages', [{}])[0]
                                sender = message.get('from')
                                msg_type = message.get('type')
                                text = None

                                if msg_type == 'text':
                                    text = message.get('text', {}).get('body', '')

                                elif msg_type == 'interactive':
                                    interactive = message.get('interactive', {})
                                    if interactive.get('type') == 'button_reply':
                                        text = interactive['button_reply'].get('title')
                                    elif interactive.get('type') == 'list_reply':
                                        text = interactive['list_reply'].get('title')

                                elif msg_type == 'image':
                                    text = f"IMAGE ID: {message['image'].get('id')}"

                                print(f"📩 Message from {sender}: {text}")

            return jsonify({'status': 'success'}), 200

        except Exception as e:
            print(f"Error processing webhook: {e}")
            print(traceback.format_exc())
            return jsonify({'status': 'error', 'message': str(e)}), 500

    return jsonify({'status': 'bad_request'}), 400


# 🔹 Endpoint to send outbound WhatsApp messages
@app.route('/sendWhatsApp', methods=['POST'])
def send_whatsapp():
    try:
        data = request.get_json()
        recipient = data.get("to")
        message = data.get("message")

        url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "text",
            "text": {"body": message}
        }

        r = requests.post(url, headers=headers, json=payload)

        # Debug log
        print("WhatsApp API response:", r.status_code, r.text)

        if r.status_code >= 400:
            return jsonify({"status": "error", "response": r.json()}), r.status_code

        return jsonify({"status": "sent", "response": r.json()}), 200
    except Exception as e:
        print("Error sending message:", e)
        print(traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)

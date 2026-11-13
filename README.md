# AI Agent Dashboard

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](LICENSE)

A web dashboard for managing and monitoring an AI agent for healthcare workflows, built by [Dawa Health](https://github.com/Dawa-Health). It includes authentication pages, conversation (chat) views, analytics, order tracking, risk triage, and account settings.

> **Status:** Work in progress. Not a medical device. Do not use it as the sole basis for clinical decisions.

## Features

- **Authentication**: login, registration, forgot/reset/change password
- **Dashboard**: overview of agent activity (`index.html`)
- **Chats**: browse and review agent conversations (`chats.html`)
- **Analytics**: usage and performance charts (`analytics.html`)
- **Orders**: view and track orders (`orders.html`)
- **Risk triage**: client-side triage logic (`js/risk-triage.js`)
- **Profile & settings**: user profile and preferences, including light/dark theme and layout settings

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript, jQuery, Bootstrap
- **Backend:** Python (`app.py`)
- **Icons/Fonts:** Font Awesome, Ionicons, Themify, Foundation Icons, Dropways

## Project Structure

```
.
├── app.py                # Python backend
├── requirements.txt      # Python dependencies
├── index.html            # Main dashboard
├── analytics.html        # Analytics
├── chats.html            # Chat/conversation views
├── orders.html           # Orders
├── profile.html          # User profile
├── settings.html         # Settings
├── login.html / register.html / forgot-password.html /
│   reset-password.html / change-password.html   # Auth pages
├── css/                  # Stylesheets (theme, layout, UI refresh)
├── js/                   # Scripts (auth, shell, triage, layout)
├── fonts/                # Icon fonts
└── img/                  # Images and logos
```

## Getting Started

### Prerequisites

- Python 3.9+
- pip

### Installation

```bash
git clone https://github.com/Dawa-Health/ai_agent_dashboard.git
cd ai_agent_dashboard

python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration

Keep secrets such as API keys, tokens, and passwords out of the repository. Store them in environment variables or a `.env` file, which is listed in `.gitignore`. Add every variable `app.py` expects to this section, for example:

```bash
# Example only; replace with the variables your app actually uses
export SECRET_KEY="change-me"
```

### Run

```bash
python app.py
```

Then open the URL printed in the terminal (commonly `http://localhost:5000`). If you only want to preview the static pages, you can also serve them from any web server, such as XAMPP or `python -m http.server`.

## Security & Privacy

This project may handle sensitive health-related data. Before deploying:

- Never commit credentials, tokens, or patient data
- Serve over HTTPS
- Apply access controls and audit logging appropriate to your jurisdiction (for example HIPAA or local health data regulations)

To report a vulnerability, contact the maintainers privately rather than opening a public issue.

## Contributing

1. Fork the repository
2. Create a branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push the branch: `git push origin feature/your-feature`
5. Open a pull request

## License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**. See the [LICENSE](LICENSE) file for the full text.

SPDX-License-Identifier: AGPL-3.0

If you run a modified version of this software as a network service, the AGPL requires you to offer the corresponding source code to its users.

## Acknowledgments

The UI is based on the DeskApp admin template and uses open-source libraries including Bootstrap, jQuery, and Font Awesome. Each remains under its own license. Check that your use of the template and its assets permits redistribution.

# AI Agent Dashboard Project Charter

This charter describes what the AI Agent Dashboard project is for, what it covers, who is responsible for it and how decisions are made. It applies to everything in this repository.

## 1. Mission

AI Agent Dashboard exists to give care teams a clear, safe view of an AI agent that supports healthcare workflows. People can see what the agent is doing, review its conversations and step in when a case needs them.

## 2. Goals

- Let staff review the agent's conversations and find problems quickly.
- Flag higher-risk cases through risk triage, so that a person can act on them.
- Show usage and performance, so the team can see how the agent is working over time.
- Let staff view and track orders.
- Protect health data through access control, and keep credentials out of the code.
- Keep the code open, documented and easy to run.

## 3. Scope

**In scope**

- The dashboard pages, styles and scripts (`css/`, `js/` and the HTML pages).
- The Python backend (`app.py`).
- The risk triage logic (`js/risk-triage.js`).
- The authentication, profile and settings pages.
- Documentation and setup instructions.

**Out of scope**

- Personal, patient or user data of any kind, including de-identified conversations.
- The AI agent itself and its models. This repository manages and monitors the agent; it does not contain it.
- Clinical decisions. The dashboard is not a medical device and must not be the sole basis for a clinical decision.
- Credentials and settings for any particular deployment.
- Content that Dawa Health or the contributor does not have the right to share.

## 4. Principles

- **Patient safety first.** Triage rules and health wording are reviewed by a qualified health professional before they are merged. The dashboard supports clinical judgement and never replaces it.
- **People stay in charge.** The dashboard exists so that people can see what the agent does and step in. New features should make that easier, not harder.
- **Privacy and security.** Nothing that could identify a person is accepted. Secrets stay out of the repository. Deployments are expected to use HTTPS, access controls and audit logging that fit the rules where they operate.
- **Openness.** The code and its history are public. Known problems are recorded, not hidden.
- **Respect for other people's work.** The DeskApp template and the libraries the dashboard uses keep their own licenses.

## 5. Roles and responsibilities

| Role | Responsibilities |
| --- | --- |
| Project steward (Dawa Health) | Owns the repository, holds the copyright, sets direction and appoints maintainers. |
| Maintainers | Review and merge pull requests, cut releases, keep documentation current, and enforce this charter and the Code of Conduct. |
| Clinical reviewers | Check risk triage and health wording for accuracy and safety. At least one must approve any change to them. |
| Contributors | Anyone who opens an issue or pull request. Contributors follow the contributing guide and the Code of Conduct. |

Current maintainers and reviewers:

| Name | Role | Area |
| --- | --- | --- |
| Tariro F Munzwa | Maintainer | Repository and releases |
| Tafadzwa K Munzwa, MD| Clinical reviewer | Risk triage and health wording |

## 6. Decision making

- Day-to-day changes are decided by pull request review. A change is merged when it has the approvals in section 7 and the checks in the contributing guide have been run.
- Maintainers aim for consensus. If maintainers cannot agree, the project steward decides.
- Larger changes need an issue for discussion first, open for at least seven days. These include changing how risk triage works, changing authentication or how data is stored, moving to a new framework, and changing the license.
- An urgent fix for a safety, security or privacy problem can be merged without the seven-day wait. It is discussed in an issue afterwards.
- Clinical disagreements are settled by the clinical reviewers, with reference to current national and WHO guidance. Where guidance differs between countries, the triage rules say which they follow.

## 7. How changes are made

1. Open an issue describing the problem or proposal, unless the change is a small fix.
2. Create a branch and make the change. Nobody commits directly to `main`.
3. Open a pull request that says what changed, why, and how it was tested.
4. Run the checks described in the contributing guide.
5. Review and approval:
   - any change: one maintainer;
   - risk triage and health wording: one maintainer and one clinical reviewer.
6. A maintainer merges the pull request.

Details are in [CONTRIBUTING.md](CONTRIBUTING.md).

## 8. Quality

- Before a change is merged, the app is run and each changed page is checked in both themes and at desktop and mobile widths.
- Every change to a triage rule states the guidance it follows.
- Known problems are tracked in issues until they are fixed.
- Reports from clinicians and health workers who use the dashboard, and any security or privacy problem, are treated as a priority.

## 9. Releases

- Releases use version numbers of the form MAJOR.MINOR.PATCH.
  - MAJOR: a change that existing deployments cannot take without changing their configuration or stored data.
  - MINOR: new features or pages.
  - PATCH: fixes and documentation.
- Each release has a tag and an entry in `CHANGELOG.md`.
- Any change to risk triage is named in the changelog.

## 10. License and contributions

The project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0). Copyright is held by Dawa Health. Contributions are accepted under the same license, and contributors confirm they have the right to share what they submit. The DeskApp template and third-party libraries keep their own licenses.

## 11. Code of Conduct

Everyone taking part in the project follows the [Code of Conduct](CODE_OF_CONDUCT.md). Reports go to developers@dawa-health.com.

## 12. Funding and independence

Where the project receives outside funding, funders do not decide what is merged; that is decided through the process in this charter.

## 13. Changes to this charter

Changes to this charter or to the Code of Conduct are proposed by pull request, discussed in an issue for at least seven days, and approved by the project steward.

## Contact

developers@dawa-health.com

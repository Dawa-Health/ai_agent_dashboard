# Contributing to AI Agent Dashboard

Thank you for helping to improve AI Agent Dashboard. Fixes and improvements are welcome, especially from clinicians and health workers who use the dashboard.

By taking part you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## Ways to contribute

- **Report a problem.** A bug, a broken layout, a page that fails in the dark theme or on a small screen, a triage result that looks wrong or unsafe, an unclear label.
- **Fix or improve the dashboard.** Pages, styles, scripts and the Python backend.
- **Improve risk triage.** Changes to `js/risk-triage.js` need clinical review (see "Review and approval").
- **Improve the project.** Documentation, setup instructions and the list of environment variables in the README.

You do not need to write code to contribute. If you are not comfortable with Git, open an issue describing the problem, or email developers@dawa-health.com, and a maintainer will make the change and credit you.

## Rules for all contributions

- **No personal or patient information.** Never include names, contact details, conversations, orders, triage results or case details from real people, even if de-identified. Use made-up data in examples, screenshots and test data.
- **No secrets.** Never commit API keys, tokens, passwords or a `.env` file. Keep them in environment variables, as described in the README.
- **Only share what you have the right to share.** Do not copy code, images, icons or text unless their license allows it, and say where they came from. The UI is based on the DeskApp admin template, so check that any new template asset can be redistributed.
- **Health content must be accurate and safe.** Base triage rules and health wording on current national or WHO guidance, and say which in the pull request. The dashboard is not a medical device, so do not word anything as a diagnosis.

## Reporting a problem

Open an issue and include:

- the page (for example `chats.html`) and what you were doing;
- what went wrong, and what you expected;
- your browser and screen size, and whether you were using the light or dark theme;
- a source, for corrections to triage or health wording.

For a security vulnerability, or personal information that has been published by mistake, do not open a public issue. Email developers@dawa-health.com.

## Making a change

Nobody commits directly to `main`. All changes go through a pull request.

1. Open an issue first for anything larger than a small fix, so it can be discussed before you do the work. Changes to risk triage, authentication or how data is stored always need an issue.

2. Fork the repository and create a branch. Name it after the change:

   ```
   git checkout -b fix/chats-empty-state
   git checkout -b feature/analytics-date-range
   git checkout -b docs/environment-variables
   ```

3. Make the change. See "Working on the code" below.

4. Run the checks on your machine. See "Checks" below.

5. Commit with a short message that says what changed and where:

   ```
   Fix empty state on chats page when no conversations load
   ```

6. Open a pull request against `main`. Say what changed, why, and how you tested it, and link the issue it resolves.

7. Respond to review. Push further commits to the same branch. A maintainer merges the pull request once it is approved.

## Working on the code

- **Use the existing stack.** Pages are HTML in the repository root, with styles in `css/` and scripts in `js/`, built on JavaScript, jQuery and Bootstrap. Propose a new library or framework in an issue first.
- **Explain triage changes.** Keep client-side triage logic in `js/risk-triage.js`. For every rule you change, say in the pull request what it was, what it is now and the guidance behind it.
- **Document configuration.** When `app.py` starts reading a new environment variable, add it to the Configuration section of the README.
- **Keep changes small.** One page or one kind of fix per pull request is easier to review.

## Checks

Before opening a pull request, run the app locally:

```
pip install -r requirements.txt
python app.py
```

Then open each page you changed and check that:

- it loads without errors in the browser console;
- it works in the light and dark themes, with the layout settings, and at desktop and mobile widths;
- sign-in, registration and the password pages still work, if you changed authentication code or `app.py`.

## Review and approval

| Change | Approvals needed |
| --- | --- |
| Documentation, styling and code | One maintainer |
| Risk triage and health wording | One maintainer and one clinical reviewer |

Reviewers check that the change works and is safe, contains no personal information or secrets, and does not weaken how health data is protected. Maintainers aim to give a first response within seven days.

## Credit

Contributors are credited through their commits. When a maintainer makes a change for you from an issue or an email, they credit you as a co-author.

## License

The project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0). By submitting a contribution you agree that it is licensed under the same terms, and you confirm that you have the right to submit it. Third-party libraries and template assets keep their own licenses.

## Questions

Open an issue, or email developers@dawa-health.com.

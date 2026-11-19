# Publish Masar Study on GitHub

## Current status

The project has been prepared for publication. No GitHub repository has been created or updated through ChatGPT yet.

## One-time GitHub setup

1. Open https://github.com/new while signed in to the intended GitHub account.
2. Set the repository name to `masar-study`.
3. Choose **Private** initially. Do not initialize the repository with a README, `.gitignore`, or license because these are already included in this package.
4. Create the repository.
5. Give the connected GitHub app access to the repository via GitHub app permissions; if using 'Only selected repositories', select `masar-study`.
6. Share the repository URL in ChatGPT, where the files can be uploaded through the connected GitHub tool once the installation reports the repository as accessible.

## Project layout

- `server.py` — FastAPI backend, configured to disable real form submissions until legal/privacy and SMTP settings are complete.
- `site/` — responsive Arabic landing page and demo legal notices.
- `render.yaml` — Render Blueprint for a *preview* web service.
- `requirements.txt` — Python dependencies.
- `.env.example` — environment-variable names only; no real secrets.
- `DEPLOYMENT.md` — Render deployment instructions and important launch safeguards.
- `MASTER_PROMPT.md` — product/design build prompt.

## Safety

Never commit `.env`, SMTP credentials, OAuth tokens, student records, uploaded documents, or real private personal data. The GitHub bundle intentionally does not include these.
The site is not ready to accept live student applications until the operator's legal notices, data protection procedures, file-upload safeguards, and mailbox configuration are complete.

## Alternative manual upload

If you cannot give ChatGPT's GitHub connector repository permission, unzip the package, open the repository on GitHub and choose **Add file > Upload files**. Upload the source files/directories (not the ZIP file itself). Check that `site/index.html`, `server.py` and `render.yaml` are present in the repository root structure.

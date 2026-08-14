# EcoBot — Deployment Guide

This guide walks you through deploying EcoBot to the web using GitHub and Streamlit Community Cloud.

---

## Prerequisites

| Tool | Purpose | Install |
|------|---------|---------|
| Git | Version control | https://git-scm.com/downloads |
| GitHub account | Remote repository host | https://github.com |
| Streamlit Cloud account | Free app hosting | https://share.streamlit.io |
| Groq API key | LLM inference | https://console.groq.com |

---

## Part 1 — Push the Repository to GitHub

### Step 1: Initialise a local git repository

Open a terminal in the project root (`energy_chatboat/`) and run:

```bash
git init
git add .
git status          # confirm all expected files are staged
```

> **Important:** verify that `.env` and `.venv/` are **not** listed in `git status` output.
> They are excluded by `.gitignore`. If they appear, do not commit them.

### Step 2: Make the first commit

```bash
git commit -m "feat: initial EcoBot deployment setup"
```

### Step 3: Create a new repository on GitHub

1. Go to https://github.com/new
2. Set **Repository name** to `energy_chatboat` (or any name you prefer).
3. Set visibility to **Public** (required for the free tier of Streamlit Cloud).
4. Leave "Add a README", ".gitignore", and "license" **unchecked** — you already have these locally.
5. Click **Create repository**.

### Step 4: Connect local repo to GitHub and push

Copy the remote URL shown on GitHub (HTTPS format) and run:

```bash
git remote add origin https://github.com/<YOUR_USERNAME>/energy_chatboat.git
git branch -M main
git push -u origin main
```

Replace `<YOUR_USERNAME>` with your actual GitHub username.

GitHub Actions will immediately run the CI workflow (`.github/workflows/deploy.yml`) on this push.
You can watch it under the **Actions** tab of your repository.

---

## Part 2 — Connect to Streamlit Community Cloud

### Step 1: Sign in to Streamlit Cloud

Go to https://share.streamlit.io and sign in with your GitHub account.
Grant Streamlit permission to access your repositories when prompted.

### Step 2: Deploy a new app

1. Click **New app** (top-right button).
2. Fill in the form:

   | Field | Value |
   |-------|-------|
   | Repository | `<YOUR_USERNAME>/energy_chatboat` |
   | Branch | `main` |
   | Main file path | `app.py` |

3. Click **Deploy**.

Streamlit Cloud will clone your repo, install `requirements.txt`, and launch the app.
First deployment takes a few minutes because of the ML library downloads (torch, sentence-transformers).

### Step 3: Verify the deployment

Once the spinner completes, Streamlit Cloud will show you a public URL in the format:

```
https://<YOUR_USERNAME>-energy-chatboat-app-<hash>.streamlit.app
```

Open it in a browser. The app will display a red error banner if `GROQ_API_KEY` is missing —
that is expected until you complete Part 3 below.

---

## Part 3 — Configure GROQ_API_KEY in Streamlit Cloud Secrets

The app reads your Groq API key from Streamlit Cloud Secrets at runtime.
**Never commit the key to git.**

### Step 1: Open the Secrets editor

1. In Streamlit Cloud, find your deployed app.
2. Click the **⋮ (three-dot menu)** next to the app name.
3. Select **Settings → Secrets**.

### Step 2: Add the secret

Paste the following into the secrets text box (TOML format):

```toml
GROQ_API_KEY = "gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

Replace the value with your actual key from https://console.groq.com/keys.

### Step 3: Save and reboot

Click **Save**. Streamlit Cloud automatically reboots the app.
Within 30 seconds the app will reload with the key available, and EcoBot will respond to queries.

---

## Part 4 — Subsequent Updates

Any `git push` to the `main` branch triggers two things automatically:

1. **GitHub Actions CI** — lints your code and runs smoke tests.
2. **Streamlit Cloud auto-redeploy** — pulls the latest commit and restarts the app.

Typical update workflow:

```bash
# make your code changes, then:
git add <changed_files>
git commit -m "fix: <description of change>"
git push origin main
```

---

## Part 5 — Local Development Setup

To run EcoBot locally:

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows PowerShell
# source .venv/bin/activate     # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your API key as an environment variable
$env:GROQ_API_KEY = "gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"   # PowerShell
# export GROQ_API_KEY="gsk_..."                          # bash

# 4. Launch the app
streamlit run app.py
```

Alternatively, create a `.streamlit/secrets.toml` file locally (it is git-ignored):

```toml
# .streamlit/secrets.toml  — DO NOT COMMIT THIS FILE
GROQ_API_KEY = "gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

Then run `streamlit run app.py` without setting an environment variable.

---

## File Structure Reference

```
energy_chatboat/
├── app.py                          # Streamlit UI entry point
├── query_engine.py                 # RAG + Groq inference logic
├── ingest.py                       # Data ingestion script (run once)
├── requirements.txt                # Python dependencies (pinned)
├── .gitignore                      # Excludes venv, secrets, cache
├── DEPLOYMENT.md                   # This guide
├── bg.png                          # Background image (tracked in git)
├── logo.png                        # App logo (tracked in git)
├── .github/
│   └── workflows/
│       └── deploy.yml              # GitHub Actions CI pipeline
├── data/
│   ├── raw/                        # Source CSV, PDF, HTML files
│   └── processed/
│       └── chunked_documents.json  # Pre-chunked document store
├── vector_db/                      # ChromaDB persisted index (tracked in git)
│   ├── chroma.sqlite3
│   └── <uuid>/
└── ingestion/                      # Data loading & embedding modules
    ├── chunker.py
    ├── data_loader.py
    └── embedder.py
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Red error banner: "GROQ_API_KEY not found" | Secret not set in Streamlit Cloud | Complete Part 3 of this guide |
| App stuck on spinner / crashes on boot | Heavy deps still installing | Wait 2–3 minutes, then refresh |
| `ModuleNotFoundError` in CI | Dependency missing from `requirements.txt` | Add the missing package and push |
| GitHub Actions fails on lint step | Syntax or import error in Python file | Check the Actions log for the file and line number |
| Vector DB returns no results | `vector_db/` not pushed to GitHub | Run `git add vector_db/ && git commit` |
| `torch` download times out in CI | Slow runner | Re-run the failed job; GitHub provides a fresh runner |

---

## Security Notes

- The `GROQ_API_KEY` is **never** stored in the codebase. It lives only in Streamlit Cloud Secrets or your local environment.
- `.streamlit/secrets.toml` is excluded by `.gitignore` — confirm with `git status` before each commit.
- Rotate your Groq API key at https://console.groq.com/keys if you believe it was accidentally exposed.

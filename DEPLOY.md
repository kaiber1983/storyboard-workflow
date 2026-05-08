# Storyboard Workflow Deploy Guide

This project can run as a single deployable Python web service:

- `GET /` serves `storyboard-workflow.html`
- `POST /agent/extract` extracts character and scene information
- `POST /agent/storyboard` generates shot tables and prompts
- `GET /health` returns a health check

## Local Run

```powershell
.\run_local.ps1
```

Open:

```text
http://127.0.0.1:8787
```

## Public Server Run

Set environment variables:

```text
HOST=0.0.0.0
PORT=8787
```

Then run:

```bash
python storyboard_agent_server.py
```

Open your server URL:

```text
http://YOUR_SERVER_IP:8787
```

## Server-Side LLM Config

You can let users enter API settings in the page, or configure a shared server-side model:

```text
STORYBOARD_LLM_ENABLED=true
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
LLM_API_KEY=your_api_key
```

When server-side config is enabled, users do not need to enter an API key in the browser.

## Security Notes

For public use, put this behind HTTPS and add authentication or rate limiting before sharing widely. Avoid storing shared API keys in frontend code.

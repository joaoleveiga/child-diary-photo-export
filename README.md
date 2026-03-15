# child-diary-photo-export

Export media from ChildDiary to local files.

The script logs in with your account credentials from `.env`, fetches paginated media from the ChildDiary API, and downloads files into `media/` with retry support.

## Requirements

- Python `3.14`
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

## Quick Start

1. Sync the project environment:

```bash
uv sync --all-extras
```

2. Create your local environment file:

```bash
cp .env.example .env
```

3. Fill `.env` with your ChildDiary credentials:

```dotenv
CHILD_DIARY_USERNAME=you@example.com
CHILD_DIARY_PASSWORD=your-password
```

4. Run the exporter:

```bash
uv run python script.py
```

Downloaded files will be written to `media/`.

## How It Works

- Authenticates with `POST https://app.childdiary.net/api/Account/login`
- Requests media pages from `GET https://app.childdiary.net/api/media?page=<n>`
- Downloads each item URL concurrently (`ThreadPoolExecutor`)
- Retries failed file downloads using exponential backoff (`tenacity`)

## Environment Variables

- `CHILD_DIARY_USERNAME`: ChildDiary login email/username
- `CHILD_DIARY_PASSWORD`: ChildDiary account password

## Development

Useful commands:

```bash
make sync
make ruff
make mypy
```

Install hooks once per clone:

```bash
uv run pre-commit install
```

## Security Notes

- Never commit `.env`.
- If you previously used copied browser cookies/headers, invalidate that old session.

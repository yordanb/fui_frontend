# FUI Frontend

Frontend untuk FUI Management System + Oil Lab + DBR Dashboard.

## Stack

- **Flask** (Python 3.x) — server-side rendering
- **Vite + React + TypeScript** (dev/build)
- **Tailwind CSS v4**

## Struktur

```
├── app.py                   # Flask entry point
├── routes/                  # Flask blueprints
│   ├── auth.py              # Login/logout
│   ├── fui.py               # FUI CRUD
│   ├── main_routes.py       # Dashboard, users, list
│   ├── oil_lab.py           # Oil Lab proxy
│   └── dbr.py               # DBR proxy
├── templates/               # Jinja2 templates
├── static/                  # Static assets
├── src/                     # React source (build only)
├── vite.config.ts
├── package.json
└── README.md
```

## Running

```bash
# Development - Flask
python3 app.py

# Development - Vite (hot reload)
npm run dev
```

## Endpoint Proxy

| Route | Backend |
|---|---|
| `/oil-lab-api/*` | `http://localhost:8009` |
| `/dbr-api/*` | `http://localhost:8010` |
| Direct call | `http://localhost:8008/api` |

## Port

- Flask: `3005`
- Vite dev: `3005`

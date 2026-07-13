# FUI Frontend

FUI Frontend adalah sistem manajemen terpadu yang melayani **FUI Management**, **Oil Lab**, dan **DBR Dashboard**. Sistem ini dibangun dengan pendekatan *Server-Side Rendering* (SSR) yang ringan menggunakan **Flask** dan **Jinja2**.

## Tech Stack

- **Framework**: Flask (Python)
- **Templating**: Jinja2
- **Styling**: Tailwind CSS (via CDN)
- **Charts**: ApexCharts (via CDN)
- **Server**: Gunicorn

## Struktur Proyek

```text
├── app.py                   # Entry point aplikasi
├── routes/                  # Modul Blueprints
│   ├── auth.py              # Autentikasi pengguna
│   ├── fui.py               # Operasi CRUD FUI
│   ├── oil_lab.py           # Proxy API Oil Lab
│   ├── dbr.py               # Proxy API DBR
│   └── upload.py            # API Import & Upload
├── templates/               # Layout Jinja2
└── static/                  # Assets (JS, CSS)
```

## Setup & Deployment

### Environment Variables
Pastikan file `.env` telah dikonfigurasi sebelum menjalankan aplikasi:
```bash
SECRET_KEY=your-secret-key
OIL_LAB_BACKEND=http://...
DBR_BACKEND=http://...
```

### Development
```bash
pip install -r requirements.txt
python app.py
```

### Production
Aplikasi menggunakan **Docker** dan **Gunicorn**. Jalankan dengan:
```bash
docker-compose up --build -d
```

## Proxy Endpoints

| Route | Target Backend |
|---|---|
| `/oil-lab-api/*` | `http://localhost:8009` |
| `/dbr-api/*` | `http://localhost:8010` |

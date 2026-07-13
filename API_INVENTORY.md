# API Inventory — FUI Frontend

Generated: 2026-07-03

## Oil Lab API (target: `/api/v1/`)

| File | Line | Fetch Pattern |
|---|---|---|
| `oil_dashboard.html` | 129 | `\`${API}/api/samples/stats?${params}\`` |
| `oil_dashboard.html` | 148 | `\`${API}/api/samples/search?${params}\`` |
| `oil_dashboard.html` | 248 | `\`${API}/api/samples/units?${params}\`` |
| `oil_dashboard.html` | 272 | **Hardcoded:** `'/oil-lab-api/api/samples/stats'` |
| `fui_form.html` | 124 | **Hardcoded:** `'/oil-lab-api/api/samples/search?…'` |
| `fui_form.html` | 185 | **Hardcoded:** `'/oil-lab-api/api/samples/search?…'` |

## DBR API (sudah `/api/v1/`)

| File | Line | Fetch Pattern |
|---|---|---|
| `dbr_dashboard.html` | 295+ | `API + '/api/v1/dashboard/…'` |
| `dbr_dashboard.html` | 311 | **Hardcoded:** `'/dbr-api/api/v1/breakdowns?…'` |
| `equipment.html` | 132+ | `'/dbr-api/api/v1/equipment/…'` |
| `equipment.html` | 248 | `'/dbr-api/api/v1/equipment/…'` |
| `equipment.html` | 257 | `'/dbr-api/api/v1/equipment/…'` |
| `fui_form.html` | 231 | `'/dbr-api/api/v1/breakdowns?…'` |
| `fui_form.html` | 267 | `'/dbr-api/api/v1/equipment/search/…'` |
| `fui_detail.html` | 160 | `'/dbr-api/api/v1/breakdowns?…'` |

## Users API (internal, no proxy)

| File | Line | Fetch Pattern |
|---|---|---|
| `users.html` | 130+ | `'/users/api/users'` |

## Upload API (internal)

| File | Line | Fetch Pattern |
|---|---|---|
| `upload.html` | 202 | `svc.endpoint` (dynamic) |

---

# Migration Order

1. **Oil Lab API Backend** — Ubah `prefix="/api"` → `prefix="/api/v1"` di `app/api/v1/...`
2. **Oil Lab Frontend** — Ganti semua `${API}/api/...` → `${API}/api/v1/...` di `oil_dashboard.html`
3. **FUI Form** — Ganti semua `'/oil-lab-api/api/...'` → `\`${API}/api/v1/...\`` (dua tempat)
4. **Cleanup** — Hapus `Import Router` root jika tidak lagi dipakai.

```bash
# Quick search for any leftover hardcoded paths:
grep -rn "fetch" /opt/projects/fui-frontend/templates/*.html | grep -v "users\|upload"
```

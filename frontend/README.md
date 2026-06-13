# English Education Frontend

Backend kodiga tegmasdan yozilgan frontend SPA.

## Ishga tushirish

1. Django serverni root papkada ishga tushiring:

```bash
venv/bin/python manage.py runserver
```

2. Frontend serverni alohida terminalda ishga tushiring:

```bash
cd frontend
npm run dev
```

3. Brauzerda oching:

```text
http://127.0.0.1:5173
```

`server.js` `/User/...` so'rovlarini Django backendga proxy qiladi. Shu sabab backenddagi CORS sozlamalariga tegish shart emas.

## Moslangan endpointlar

- `POST /User/login/`
- `GET/PATCH /User/users/me/`
- `POST /User/users/change-password/`
- `GET/POST/PATCH/DELETE /User/users/`
- `GET/POST/PATCH/DELETE /User/parents/`
- `GET /User/telegram-check/<student_user_id>/`

# Run the TAK administration platform locally

The backend is configured to use SQLite and local media storage when the
repository `.env` contains `DJANGO_USE_SQLITE=True`.

From this repository, run:

```powershell
py -3.12 manage.py migrate
py -3.12 manage.py createsuperuser
py -3.12 manage.py runserver 127.0.0.1:8000
```

Use the same staff username and password at the Next.js admin application.
The protected API is available at `http://127.0.0.1:8000/api/admin/v1/`.

From `D:\Projects\TAK KIN WORK\tak-kinship-admin`, use:

```powershell
npm.cmd install
npm.cmd run dev -- --port 3001
```

Then visit `http://127.0.0.1:3001/login`.

Production remains PostgreSQL/S3-backed. Do not set `DJANGO_USE_SQLITE=True`
in a deployed environment; configure the Railway PostgreSQL, storage, email,
secret-key, and allowed-origin variables there instead.

# Archive

`frontend-vanilla/` is the original plain HTML/CSS/JS frontend. It still works and is kept
as a fallback while the app uses a Lovable-built frontend.

Use it again either way:

- **Serve it from the backend:** set `FRONTEND_DIR=../archive/frontend-vanilla` (see
  `backend/.env.example`), then open the backend URL.
- **Restore it:** `git mv archive/frontend-vanilla frontend`.

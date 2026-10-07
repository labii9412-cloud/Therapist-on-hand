# 🌿 Therapist-on-hand

A platform that connects patients with **screened, qualified therapists** and lets them hold regular **video sessions** from anywhere.

| Client | What it is | Where |
|---|---|---|
| **Web app** | Responsive website, works on any browser | `web/` (served by the backend) |
| **Mobile app** | The same web app, installable on a phone home screen (PWA) | `web/` + `manifest.json` + `sw.js` |
| **Desktop app** | One-click Windows app (Electron): starts the server itself, then shows the dashboard | `desktop/` |
| **Backend** | REST API + database + WebRTC signaling (Python, FastAPI) | `backend/` |

## Features

- **Accounts & login** for three roles: patient, therapist, admin (JWT tokens, PBKDF2-hashed passwords).
- **Rigorous 3-step therapist screening**: licence verification → credential review → background check. A therapist is **only visible to patients after an admin approves** and **every step is passed**.
- **Scheduling**: therapists publish time slots, patients book them; double-booking is prevented; cancelling frees the slot.
- **Real video sessions** using WebRTC (peer-to-peer, encrypted) with in-call chat, mute and camera toggle.
- **Private session notes** written by the therapist; patients can never read them.
- **Admin dashboard** to review applications and see platform statistics.
- **Automated tests** (21 backend tests) covering auth, screening, booking, privacy and video signaling.

## Quick start

See **[SETUP.md](SETUP.md)** for the full step-by-step guide. In short:

```bash
# 1. backend + web app  (Windows: double-click run-backend.bat)
./run-backend.sh
# 2. open http://localhost:8000
# 3. (optional) demo data
cd backend && python seed.py
# 4. (optional) desktop app: starts the server by itself
cd desktop && npm install && npm start
# 5. (optional) Windows installer with desktop shortcut: double-click build-desktop.bat
```

Default admin login: `admin@therapistonhand.com` / `Admin@12345` (change it in `backend/.env`).
Demo password for seeded accounts: `Demo@12345`.

## Project structure

```
therapist-on-hand/
├── README.md
├── SETUP.md                  ← step-by-step install & run guide
├── run-backend.sh / .bat     ← one-command start (server only)
├── build-desktop.bat         ← builds the Windows installer
├── backend/
│   ├── app/
│   │   ├── main.py           ← FastAPI app, serves the web client
│   │   ├── config.py  database.py  models.py  schemas.py  security.py  deps.py  utils.py
│   │   └── routers/          ← auth, therapists, admin, appointments, video (WebRTC signaling)
│   ├── tests/                ← pytest suite
│   ├── seed.py               ← demo data
│   ├── requirements.txt
│   └── .env.example
├── web/                      ← HTML / CSS / JavaScript client (+ PWA files)
├── desktop/                  ← Electron app
└── docs/
    ├── SRS.md                ← Software Requirements Specification
    ├── DESIGN.md             ← architecture, ERD, sequence diagrams
    ├── API.md                ← REST + WebSocket reference
    ├── SCREENING_PROCESS.md  ← therapist vetting procedure
    ├── TEST_PLAN.md          ← automated + manual test cases
    └── USER_GUIDE.md         ← how patients, therapists and admins use the app
```

## Important notice

This is a course project. It is **not** a certified medical device or emergency service, and before real-world use it would need legal review, privacy/data-protection compliance, a professional licence-verification process and a security audit (see `docs/SRS.md` §3.4 and `docs/DESIGN.md` §7).

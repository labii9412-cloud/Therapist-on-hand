# Software Requirements Specification (SRS)
## Therapist-on-hand Service

| | |
|---|---|
| **Document version** | 1.0 |
| **Prepared by** | Laiba Asif |
| **Project type** | Course project, BS Software Engineering |
| **Status** | Implemented (see `docs/TEST_PLAN.md` for verification) |

---

## 1. Introduction

### 1.1 Purpose
This document specifies the requirements of **Therapist-on-hand**, a service that connects patients with qualified therapists so that their treatment runs smoothly and regularly. It is intended for the project supervisor, developers, and testers.

### 1.2 Scope
Therapist-on-hand provides:
- a rigorous **screening procedure** for therapists before they can accept patients;
- **appointment booking** between patients and screened therapists;
- **live video sessions** (with in-call chat) for more personal sessions;
- delivery as a **mobile app**, a **website**, and a **desktop application**.

Out of scope for version 1.0: online payments, insurance claims, e-prescriptions, group therapy rooms, session recording, AI-based matching, and emergency/crisis handling (the app displays an emergency notice and does not replace emergency services).

### 1.3 Definitions

| Term | Meaning |
|---|---|
| Patient | A person seeking therapy |
| Therapist | A licensed mental-health professional who applies to offer sessions |
| Admin | Platform staff who screen therapists and monitor the platform |
| Screening | The 3-step vetting process in `docs/SCREENING_PROCESS.md` |
| Slot | A time window a therapist publishes as bookable |
| WebRTC | Browser technology for real-time peer-to-peer audio/video |
| Signaling | Small messages used to set up a WebRTC call |
| PWA | Progressive Web App: a website installable like a phone app |
| JWT | JSON Web Token used to keep users logged in |

### 1.4 References
- IEEE Std 830-1998, *Recommended Practice for Software Requirements Specifications*
- W3C WebRTC 1.0 specification
- Project documents: `DESIGN.md`, `API.md`, `SCREENING_PROCESS.md`, `TEST_PLAN.md`, `USER_GUIDE.md`

### 1.5 Overview
Section 2 describes the product in general. Section 3 lists specific requirements. Section 4 gives use cases. Section 5 lists future work.

---

## 2. Overall Description

### 2.1 Product perspective
A client-server system. One backend (REST API + WebSocket signaling + database) serves three clients that share the same user interface code: browser, installable mobile PWA, and an Electron desktop app.

```
Browser / Phone (PWA) / Electron  ──HTTPS + WSS──►  FastAPI backend ──► SQLite / PostgreSQL
            ▲                                          (auth, screening, booking, signaling)
            └────────── WebRTC audio/video (peer to peer) ──────────┘
```

### 2.2 Product functions (summary)
1. Register / log in with role-based access
2. Therapist application and multi-step screening by an admin
3. Therapist directory (approved therapists only) with search
4. Therapist availability management
5. Appointment booking, cancelling, completing
6. Video session with chat, mute, and camera toggle
7. Private therapist session notes
8. Admin dashboard and statistics

### 2.3 User classes

| User | Characteristics | Main needs |
|---|---|---|
| Patient | Any adult, varying technical skill | Trust that therapists are qualified; easy booking; private, reliable video |
| Therapist | Licensed professional | Get vetted once, manage schedule, run sessions, keep private notes |
| Admin | Platform staff | Efficient, auditable screening; overview of platform |

### 2.4 Operating environment
- Backend: Python 3.10+, any OS; SQLite (development) or PostgreSQL (production)
- Clients: latest Chrome, Edge, Firefox, Safari; Android/iOS via PWA; Windows/macOS/Linux via Electron
- Network: HTTPS required for camera access on non-localhost hosts

### 2.5 Design and implementation constraints
- Camera/microphone access requires a secure context (HTTPS or localhost).
- Peer-to-peer video may need a TURN relay behind strict firewalls.
- Health-related data is sensitive; the design follows data-minimisation and least-privilege principles.

### 2.6 Assumptions and dependencies
- Admins verify therapist licences against the relevant licensing body manually (no official API integration in v1.0).
- Users have a device with a camera, microphone, and stable internet.
- Public STUN server is available for connection set-up.

---

## 3. Specific Requirements

### 3.1 Functional requirements

**Priority:** H = high, M = medium.

#### Accounts and authentication
| ID | Requirement | Pri |
|---|---|---|
| FR-1 | The system shall allow a patient to register with full name, email, and a password of at least 8 characters. | H |
| FR-2 | The system shall reject registration with an email that already exists (case-insensitive). | H |
| FR-3 | The system shall allow users to log in with email and password and issue a time-limited access token. | H |
| FR-4 | The system shall store passwords only as salted hashes (PBKDF2-SHA256). | H |
| FR-5 | The system shall enforce role-based access (patient, therapist, admin) on every protected operation. | H |

#### Therapist screening
| ID | Requirement | Pri |
|---|---|---|
| FR-6 | A therapist shall register with licence number, specialization, years of experience, education, bio, and fee. | H |
| FR-7 | On registration the system shall create three screening steps: licence verification, credential review, background check, each initially *pending*. | H |
| FR-8 | An admin shall be able to list applications, filter them by status, and open the details of each. | H |
| FR-9 | An admin shall be able to mark each step *pending / passed / failed* with notes. | H |
| FR-10 | The system shall allow approval **only when all three steps are passed**. | H |
| FR-11 | An admin shall be able to reject an application at any time with a note. | H |
| FR-12 | A therapist shall be able to view their own screening progress and the admin's decision note. | M |
| FR-13 | Therapists who are not approved shall not appear in patient searches, cannot be booked, and cannot publish availability. | H |

#### Discovery and scheduling
| ID | Requirement | Pri |
|---|---|---|
| FR-14 | A patient shall be able to list approved therapists and filter by specialization. | H |
| FR-15 | A patient shall be able to view a therapist's profile and their open future slots. | H |
| FR-16 | An approved therapist shall be able to add slots (start time, 15–180 min) that are in the future and do not overlap other slots. | H |
| FR-17 | A therapist shall be able to remove an unbooked slot; booked slots cannot be removed. | M |
| FR-18 | A patient shall be able to book an open slot with an optional reason. | H |
| FR-19 | The system shall prevent two patients from booking the same slot. | H |
| FR-20 | Patient or therapist shall be able to cancel a scheduled appointment; the slot becomes bookable again if still in the future. | H |
| FR-21 | A therapist shall be able to mark an appointment completed. | M |
| FR-22 | Users shall see only their own appointments; other users' appointments must not be accessible. | H |

#### Video sessions
| ID | Requirement | Pri |
|---|---|---|
| FR-23 | Only the patient and therapist of a *scheduled* appointment shall be able to join its video room. | H |
| FR-24 | The system shall establish a two-way audio/video call between them using WebRTC, with the server relaying only signaling messages. | H |
| FR-25 | Users shall be able to mute the microphone, turn the camera off, and leave the call. | H |
| FR-26 | Users shall be able to exchange text chat messages during the call. | M |
| FR-27 | If a participant disconnects, the other shall be notified and the call shall resume when they rejoin. | M |
| FR-28 | Optionally (configuration), joining shall be limited to a window around the appointment time. | M |

#### Notes and administration
| ID | Requirement | Pri |
|---|---|---|
| FR-29 | A therapist shall be able to write private session notes per appointment, visible only to that therapist. | M |
| FR-30 | An admin shall see platform statistics (patients, approved therapists, applications in screening, scheduled and completed sessions). | M |
| FR-31 | The system shall create a default admin account on first start from configuration. | H |

### 3.2 External interface requirements
- **User interface:** responsive web UI that adapts from phone to desktop screens; installable as an app; shows an emergency notice on every page.
- **Software interfaces:** REST/JSON API over HTTP(S) (`API.md`); WebSocket for signaling; WebRTC for media; STUN/TURN servers configured in `web/js/video.js`.
- **Hardware interfaces:** camera and microphone through the browser's `getUserMedia` API.

### 3.3 Non-functional requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-1 | Performance | Typical API calls respond in under 500 ms with up to 100 concurrent users on a single small server. |
| NFR-2 | Performance | Video call set-up completes in under 10 s on a normal broadband connection. |
| NFR-3 | Usability | A new patient shall be able to book a first session in under 5 minutes without instructions. |
| NFR-4 | Usability | The interface shall be usable on screens from 360 px wide upward. |
| NFR-5 | Reliability | Bookings are transactional; a slot can never end up booked twice. |
| NFR-6 | Portability | Runs on Windows, macOS, Linux; clients on Android, iOS, and desktop. |
| NFR-7 | Maintainability | Code is modular (routers, models, schemas), documented, and covered by automated tests. |
| NFR-8 | Availability | Target 99% uptime in production deployment (excluding maintenance). |

### 3.4 Security and privacy requirements

| ID | Requirement |
|---|---|
| SEC-1 | All traffic in production shall use HTTPS/WSS. |
| SEC-2 | Video and audio shall be encrypted (WebRTC DTLS-SRTP) and shall not be recorded or stored by the server. |
| SEC-3 | Session notes and booking reasons are visible only to the treating therapist (notes) or the two participants (reason). |
| SEC-4 | Access tokens expire (default 8 h). |
| SEC-5 | Error messages shall not reveal whether another user's appointment exists. |
| SEC-6 | User input shall be validated on the server and escaped when displayed (protection against injection and XSS). |
| SEC-7 | Before real-world deployment: compliance review against applicable health-data law (e.g. GDPR; HIPAA if serving the US; Pakistan's data-protection legislation as applicable), a privacy policy, user consent, encryption of the database at rest, audit logging, and a security review. |

### 3.5 Quality attributes
Correctness (automated tests), security (least privilege), maintainability (layered design), usability (simple flow), portability (single web codebase for all clients).

---

## 4. Use Cases

### UC-1 Register and get screened (Therapist)
**Actor:** Therapist, Admin. **Pre:** none.
1. Therapist submits the registration form with professional details.
2. System creates the account and three pending screening steps; status = *pending*.
3. Admin reviews each step, records notes, and sets pass/fail.
4. When all steps have passed, admin approves; status = *approved*.
5. Therapist can now publish availability and is listed for patients.

**Alternate:** any step fails → admin rejects; therapist sees the note. **Exception:** admin tries to approve with steps not passed → system refuses (FR-10).

### UC-2 Book a session (Patient)
**Pre:** patient logged in, an approved therapist has open slots.
1. Patient searches/browses therapists and opens a profile.
2. Patient picks a slot, optionally adds a reason, confirms.
3. System marks the slot booked and creates the appointment.
**Exception:** slot taken meanwhile → system shows "just booked by someone else".

### UC-3 Attend a video session (Patient, Therapist)
**Pre:** scheduled appointment.
1. Both open *Appointments* and choose **Join video**, allowing camera/microphone.
2. The second person to join starts the WebRTC negotiation; signaling flows via the server.
3. Video/audio appear; users chat, mute, or toggle camera as needed.
4. Either leaves; the other is told. Therapist marks the appointment completed and writes private notes.

### UC-4 Cancel an appointment (Patient or Therapist)
1. User opens *Appointments* → Cancel → confirms.
2. System sets status *cancelled* and frees the slot if still in the future.

### UC-5 Monitor the platform (Admin)
Admin opens Overview to see counts, and Applications to see queue status.

---

## 5. Future Enhancements
- Online payments and invoices
- Email/SMS/push reminders before sessions
- Ratings and reviews after completed sessions
- Smart matching (specialization, language, gender preference)
- Secure document upload for therapist credentials
- Group sessions and session recording with explicit consent
- Native mobile apps (Capacitor/Flutter), multi-language support (English/Urdu)
- Crisis resources page and escalation workflow
- Two-factor authentication

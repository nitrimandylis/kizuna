<div align="center">

<img src="static/images/kizuna-logo.svg" alt="Kizuna" width="420"/>

### `絆 // CONNECT. COLLABORATE. GROW.`

*the self-governing platform for the IBDP community — CAS, clubs, and events under one roof*

![bonds](https://img.shields.io/badge/絆-bonds_included-d64550?style=flat-square&labelColor=111111)
![governance](https://img.shields.io/badge/governance-students._entirely-d64550?style=flat-square&labelColor=111111)
![license](https://img.shields.io/badge/AGPLv3-community_code_stays_community-f0a04b?style=flat-square&labelColor=111111)
![deploy](https://img.shields.io/badge/deployed-render-f0a04b?style=flat-square&labelColor=111111)
![cas hours](https://img.shields.io/badge/CAS_hours-coordinated,_not_invented-d64550?style=flat-square&labelColor=111111)

**[→ live demo](https://kizuna-n1pq.onrender.com/)**

</div>

---

## 🪢 What is this

**Kizuna (絆)** is Japanese for the bonds between people — and this platform
exists to create them across the IBDP community. Students working on similar
CAS projects find each other, passionate learners connect through subject
clubs, and shared events turn a year group into a community.

Self-governing and student-led: a Flask app with a central events calendar,
one-click registration, a club directory, and an admin panel that handles
everything from participant lists to the newsletter.

```console
nick@kizuna:~$ status
[✓] events listed. clubs federated. newsletter armed.
[i] bonds: forming. CAS reflections: still everyone's problem.
```

## 🏮 The platform

| | feature | what it actually does |
|---|---|---|
| 01 | **event discovery** | centralized calendar of every CAS activity and community gathering |
| 02 | **event registration** | one-click signup, confirmation emails included (`templates/emails/`) |
| 03 | **club directory** | every student-led club, browsable, with detail pages |
| 04 | **admin panel** | create/edit events and clubs, manage users, print participant lists |
| 05 | **newsletter** | keeping the community in the loop without a group chat |
| 06 | **auth + roles** | Flask-Login keeps the admin desk student-run but not student-overrun |

## 🚀 Run it

```bash
git clone https://github.com/nitrimandylis/kizuna.git
cd kizuna
pip install -r requirements.txt
python -m backend.app
```

Needs PostgreSQL and the mail/env config from `backend/config.py`.
Production deploys to [Render](https://render.com) straight from
`render.yaml` — push, and the bonds go live.

## 🔩 Under the hood

| layer | path | job |
|---|---|---|
| 🧠 app core | `backend/app.py` + `config.py` | Flask factory, settings, logging |
| 🗃️ models | `backend/models.py` | SQLAlchemy — users, events, clubs, registrations |
| 🚦 routes | `backend/routes/` | main, events, clubs, auth, admin, newsletter — one blueprint each |
| ✉️ mail | `backend/mail.py` | registration confirmations and newsletter sends |
| 🎨 frontend | `templates/` + `static/` | Jinja2, custom CSS, Excalifont — hand-drawn warmth on purpose |
| 🚀 deploy | `render.yaml` | the whole production story in one file |

**Stack:** Flask · SQLAlchemy · Flask-Login · PostgreSQL · Jinja2 · Render.

---

<div align="center">

**[Nick Trimandylis](https://github.com/nitrimandylis)**

`STRONGER TOGETHER. ALSO, PLEASE RSVP.`

GNU AGPL v3 — see [LICENSE](LICENSE). Community code stays community code.

</div>

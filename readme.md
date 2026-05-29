# FairBet Lab

Plataforma educativa de apuestas deportivas con moneda virtual (USS — Taller LP).

> **Aviso legal:** Plataforma educativa con moneda virtual. No constituye una casa de apuestas.

---

## Requisitos

- Python 3.12+ o Docker Desktop
- PostgreSQL (vía Docker) o SQLite en local

---

## Inicio rápido (Docker)

```powershell
cd Reto_Fairbet-lab
copy .env.example .env
docker compose up --build
```

Abre **http://127.0.0.1:8000/** — contenedores: `fairbet_web`, `fairbet_db`.

Guía completa: [docs/DOCKER.md](docs/DOCKER.md)

> Cierra otros `runserver` en el puerto 8000 (ej. Facturación). FairBet usa `/cuenta/login/`, no `/login/`.

---

## Inicio rápido (sin Docker)

```powershell
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_sistema
python manage.py seed_eventos
python manage.py runserver
```

---

## Estructura

```
Reto_Fairbet-lab/
├── apps/
│   ├── portal/              # Interfaz web (templates)
│   ├── users/               # KYC, perfil
│   ├── wallet/              # Partida doble, billetera
│   ├── events/              # Eventos, mercados, cuotas
│   ├── betting/             # Apuestas
│   ├── responsible_gaming/  # Límites, autoexclusión
│   ├── dashboard/           # Nivel 3 (pendiente)
│   └── realtime/            # Nivel 2 (pendiente)
├── templates/               # HTML del portal
├── static/css/              # Estilos
├── config/                  # Settings Django
└── docs/                    # ADR, Docker, declaración IA
```

---

## Portal web

| Ruta | Descripción |
|------|-------------|
| `/` | Inicio |
| `/registro/` | Alta + KYC |
| `/cuenta/login/` | Sesión |
| `/perfil/` | Verificar KYC (demo) |
| `/wallet/` | Saldo, recarga, retiro |
| `/eventos/` | Apostar 1X2 |
| `/apuestas/` | Historial |
| `/juego-responsable/` | Límites y autoexclusión |

---

## API REST

Prefijo `/api/` — ver tabla en commits o usar Postman. Ejemplos: `/api/wallet/saldo/`, `/api/apuestas/simple/`.

---

## Tests

```powershell
python manage.py test apps.wallet.tests apps.betting.tests apps.responsible_gaming.tests
```

---

## Rama del grupo (Git)

```powershell
git checkout -b feat/nivel1-portal-api
git add .
git status
git commit -m "feat: portal web, API nivel 1 y tests wallet/betting"
git push -u origin feat/nivel1-portal-api
```

Usen **Conventional Commits** y marquen `[ai-assisted]` si aplica (ver `docs/anti-ai-disclosure.md`).

---

## Documentación

- [docs/DOCKER.md](docs/DOCKER.md)
- [docs/adr/](docs/adr/)
- [docs/anti-ai-disclosure.md](docs/anti-ai-disclosure.md)

---

## Pendiente (siguientes sprints)

- Channels / cuotas en vivo
- Auditoría hash + dashboard operador
- Hypothesis y cobertura 80 %
- Bocetos en `docs/sketches/`

# FairBet Lab — Docker paso a paso

## Qué contenedores verás en Docker Desktop

| Nombre | Rol |
|--------|-----|
| **fairbet_web** | Django + interfaz http://127.0.0.1:8000 |
| **fairbet_db** | PostgreSQL (puerto en tu PC: **5434**) |

No confundir con `facturacion_sur`, `encomiendas`, etc. (son otros proyectos).

---

## 1. Requisitos

- Docker Desktop abierto (estado **Engine running**).
- Carpeta del proyecto: `Reto_Fairbet-lab`.

---

## 2. Crear el archivo `.env`

En PowerShell:

```powershell
cd "c:\Users\USER\Documents\CURSOS 2026-I\Reto_Fairbet-lab"
copy .env.example .env
```

El `.env` ya puede existir; debe tener `DB_HOST=db` (nombre del servicio, no `localhost`).

---

## 3. Levantar FairBet

```powershell
docker compose up --build
```

La primera vez tarda (descarga Postgres + build de la imagen).

Cuando veas algo como `Starting development server at http://0.0.0.0:8000/`, abre:

**http://127.0.0.1:8000/**

---

## 4. Parar

`Ctrl + C` en la terminal, o en Docker Desktop → Stop en `fairbet_web` y `fairbet_db`.

Para borrar contenedores:

```powershell
docker compose down
```

---

## 5. Si el puerto 8000 está ocupado

Cambia en `docker-compose.yml` la línea de ports del servicio `web`:

```yaml
ports:
  - "8001:8000"
```

Y entra a http://127.0.0.1:8001/

---

## 6. Comandos útiles dentro del contenedor

```powershell
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py seed_eventos
docker compose logs -f web
```

---

## 7. Sin Docker (solo Python)

```powershell
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_sistema
python manage.py seed_eventos
python manage.py runserver
```

Usa SQLite (`db.sqlite3`) si no tienes `.env` con Postgres.

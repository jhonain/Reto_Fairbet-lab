# Declaración de Uso de IA

**Fecha:** 2026-05-28  
**Autor:** edin jhamil romero melendres 
**Rama / alcance:** `edin` — entrega **Nivel 1** (sin combinadas, cash-out ni WebSockets)

---

## Uso registrado

| Fecha | Parte del proyecto | Tipo de uso | Detalle |
|-------|-------------------|-------------|---------|
| 2026-05-25 | `apps/portal/` (vistas, URLs, templates) | Generar e integrar código | la estructura del portal (registro, login, wallet, eventos, apuestas, juego responsable). se pudo conectar formularios con los servicios existentes de `wallet` y `betting`, probé el flujo en navegador y ajusté mensajes de error con `django.contrib.messages`. |
| 2026-05-25 | `templates/portal/` y `static/css/estilo.css` | Generar UI | HTML base y estilos. pude simplificar pantallas para que se vean bien y se reviso que el aviso legal salga en todas las páginas vía `context_processors`. |
| 2026-05-25 | `apps/betting/services.py` → `crear_apuesta_simple` | Revisar e implementar | pude ordenar validaciones (KYC, monto, mercado abierto, juego responsable) antes del bloqueo en billetera. podiendo verificar  que portal y API llamen la **misma función** y se pudo corregir  los tests. |
| 2026-05-25 | `apps/wallet/models.py` → bug `AsientoContable.save()` | Depurar | La IA detectó que usar `if self.pk` fallaba con UUID generado antes del insert. Yo validé el fix con `_state.adding` y corrí tests de recarga e idempotencia. |
| 2026-05-25 | `config/urls.py` + static en DEBUG | Corregir despliegue | Con Daphne el CSS no cargaba.sugeri `staticfiles_urlpatterns()`. Luego, volvimos a `runserver` en Docker y mantuvimos la ruta static. |
| 2026-05-25 | `requirements.txt` (UTF-16 en Windows) | Depurar Docker | reescribí el archivo en UTF-8 y agregué `.gitattributes`. |
| 2026-05-25 | `docker-compose.yml`, `.env.example`, `docs/DOCKER.md` | Documentar y ajustar | se  levanto Postgres + web. deje lo necesario para Nivel 1 (sin Redis) y documenté el error de `DB_HOST=db` fuera de Docker. |

| 2026-05-28 | `docs/adr/0001-estructura-proyecto.md` | redacte el ADR. Falta completar los otros 9 ADR que pide la guía de proceso. |

me ayude de la ia a depurar errores de entorno (Docker, encoding, static). **Revisé el código**, corrí tests y probé en navegador antes de considerarlo listo. huebieron cosas que no entendia y me ayudaba con la ia.
---

## Lo que hice yo (sin IA)

- **Probar el flujo completo en navegador:** registro → KYC demo → recarga → apuesta → historial.
- **Coordinación con el equipo:** repartir módulos (Reynaldo modelos base; yo portal + integración + docs).
- **Preparación exposición:** leer `services.py` y `ServicioBilletera` para explicar partida doble en defensa.
Elegí que un usuario logueado en / vaya directo a /eventos/ y no al home público.
Decidí que el registro redirija a login y no deje sesión abierta automática 
Pedí que el checkbox de juego responsable sea obligatorio en el formulario de apuesta, no solo texto informativo. y me ayude de las guias que se trabajo en clase entendiendo las estructuras para trabajar 

---

## 2026-05-28 — Entrega integración Nivel 1 (rama edin)

| Fecha | Parte del proyecto | Tipo de uso | Detalle |
|-------|-------------------|-------------|---------|
| 2026-05-28 | `apps/betting/tests.py`, `apps/wallet/tests.py` | Revisar tests |  mantener solo tests de apuesta simple y wallet. ejecuté `python manage.py test apps.wallet apps.betting apps.responsible_gaming`. |
| 2026-05-28 | `apps/events/management/commands/seed_eventos.py` | Simplificar seed | Dejé un solo evento demo (Perú vs Chile programado) acorde a Nivel 1. |
| 2026-05-28 | Esta declaración | Redactar | Basada en el formato de mi compañero Reynaldo; yo completé mi parte |

---




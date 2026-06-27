# Selecciones Históricas ⚽

Trabajo Práctico N°1 de la materia **Introducción al Software** (proyecto académico).

Aplicación web para armar las formaciones de selecciones históricas de fútbol.
Cada selección tiene su plantel; los jugadores se muestran como **cartas estilo
FIFA** (con puntaje, posición y foto) y se pueden ubicar en una formación 4-4-2
sobre una cancha.

> ℹ️ Editá esta sección con el nombre real de la materia, la comisión y los
> integrantes del grupo.

---

## ¿Qué se puede hacer?

- Ver las selecciones disponibles (pantalla principal).
- Entrar a una selección y **armar su formación** 4-4-2.
- En cada puesto, **agregar** un jugador disponible del plantel o **editar/quitar**
  el que está.
- **Crear** un jugador nuevo (nombre, posición, edad, pie hábil, puntaje e imagen).

---

## Tecnologías

| Capa | Tecnología |
|------|------------|
| Backend | Python + **Flask** (API REST) |
| ORM | SQLAlchemy (`flask-sqlalchemy`) |
| Base de datos | **PostgreSQL** |
| Frontend | HTML + CSS + JavaScript (vanilla) + Bootstrap 5 |

La arquitectura es **cliente-servidor**: el frontend es un sitio estático que
le pide los datos al backend por HTTP (`fetch`), y el backend los guarda en
PostgreSQL.

```
Navegador  ──HTTP/fetch──►  Backend Flask (:5000)  ──SQL──►  PostgreSQL
(frontend :8000)
```

---

## Requisitos (instalar antes de empezar)

1. **Python 3** → https://www.python.org/downloads/
   (verificá con `python --version`)
2. **PostgreSQL** → https://www.postgresql.org/download/
   Durante la instalación se pide una contraseña para el usuario `postgres`;
   este proyecto espera que sea **`postgres`** y el puerto **`5432`** (los valores
   por defecto).

> En Windows, si `psql` no se reconoce en la terminal, está en
> `C:\Program Files\PostgreSQL\17\bin`.

---

## Instalación (una sola vez)

Desde la carpeta raíz del proyecto:

```powershell
# 1. Crear el entorno virtual
python -m venv venv

# 2. Activarlo  (Windows PowerShell)
venv\Scripts\Activate.ps1
#   En Linux/Mac sería:  source venv/bin/activate

# 3. Instalar las dependencias
pip install flask flask-cors flask-sqlalchemy psycopg2-binary

# 4. Crear la base de datos
psql -U postgres -c "CREATE DATABASE seleccioneshistoricas;"

# 5. Precargar las selecciones, jugadores y fotos
cd backend
python precarga.py
cd ..
```

> Si `Activate.ps1` da error de permisos, ejecutá una vez:
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`

---

## Cómo correr el proyecto

Hacen falta **dos terminales** (una para el backend y otra para el frontend).
En las dos, primero activá el venv si no se activó solo.

⚠️ **Lo más importante:** cada parte se corre **parado en su carpeta**.

### Terminal 1 — Backend
```powershell
cd C:\Users\santi\RespositoriosGithub\Tp1-Intro-main\backend
python main.py
```
Tiene que aparecer: `Running on http://127.0.0.1:5000`

### Terminal 2 — Frontend
```powershell
cd C:\Users\santi\RespositoriosGithub\Tp1-Intro-main\frontend
python -m http.server 8000
```

### Abrir la app
En el navegador: **http://localhost:8000**

Para frenar cada servidor: `Ctrl + C`.

---

## Estructura del proyecto

```
Tp1-Intro-main\
├── backend\
│   ├── main.py          API Flask (rutas /equipos, /jugadores, etc.)
│   ├── models.py        Modelos de la base (Jugador, Equipo, Posicion)
│   ├── precarga.py      Resetea la base y carga selecciones + jugadores + fotos
│   ├── bajar_fotos.py   Descarga fotos de los jugadores desde Wikipedia
│   └── seed.py          Cargar jugadores propios (editás la lista y lo corrés)
├── frontend\
│   ├── index.html               Pantalla principal (lista de selecciones)
│   ├── formacion-equipo\        Armado de la formación 4-4-2
│   ├── jugador\crear\           Formulario para crear un jugador
│   ├── jugador\agregar\         Jugadores disponibles para un puesto
│   ├── fifa-card.css / .js      Componente de carta estilo FIFA
│   └── img\                     Fotos de los jugadores
└── venv\                Entorno virtual de Python
```

---

## Endpoints del backend

| Método | Ruta | Qué hace |
|--------|------|----------|
| GET | `/equipos` | Lista las selecciones |
| GET | `/equipos/<id>/formacion` | Jugadores ubicados en la formación |
| GET | `/equipos/<id>/posiciones/<pos>` | Jugadores disponibles para un puesto |
| POST | `/equipos/<id>/jugadores` | Crea un jugador |
| PUT | `/jugadores/<id>` | Ubica un jugador en la formación (lugar 1-11) |
| DELETE | `/jugadores/<id>` | Elimina un jugador |

---

## Las fotos de los jugadores

Las fotos viven en `frontend/img/`. El nombre del archivo es el del jugador en
minúsculas y con guiones, por ejemplo `diego-maradona.webp`.

- Para **agregar/cambiar** una foto: guardá la imagen en `frontend/img/` con ese
  nombre y volvé a correr `python precarga.py`.
- Para **bajar automáticamente** las fotos desde Wikipedia:
  `cd backend` → `python bajar_fotos.py` → `python precarga.py`.
- Si un jugador no tiene foto, la carta muestra un **avatar con sus iniciales**
  (no se rompe nada).

---

## Errores comunes

| Síntoma | Causa / Solución |
|---------|------------------|
| `python3 no se reconoce` | En Windows el comando es `python`, no `python3`. |
| `source ... no se reconoce` | Eso es de Linux. En Windows: `venv\Scripts\Activate.ps1`. |
| `can't open file '...\main.py'` | Estás parado en otra carpeta. Hacé `cd backend` antes de `python main.py`. |
| El navegador muestra una lista de archivos | Corriste `http.server` fuera de `frontend`. Pará y corré desde `frontend`. |
| `No module named flask` | No está activado el venv, o faltó `pip install`. |
| `could not connect to server` (psycopg2) | PostgreSQL no está corriendo. |
| `Address already in use` (puerto 5000/8000) | Ya hay un servidor en ese puerto. Cerralo o usá otro puerto. |
| No se ven las selecciones en la app | Falta levantar el **backend**, o no corriste `precarga.py`. |

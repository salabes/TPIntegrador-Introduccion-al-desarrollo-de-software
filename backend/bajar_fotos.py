r"""
Baja las fotos de cara de los jugadores desde Wikipedia / Wikimedia Commons
(imagenes de licencia libre) y las guarda en frontend/img con el nombre que
espera la precarga (slug del jugador).

USO (parado en backend/):
    ..\venv\Scripts\python.exe bajar_fotos.py

Despues de bajarlas, corre la precarga para que las cartas las tomen:
    ..\venv\Scripts\python.exe precarga.py

No pisa fotos que ya existan (si ya pusiste una a mano, la respeta).
"""

import json
import os
import subprocess
import time
from urllib.parse import quote

MIN_BYTES = 5000        # menos que esto = imagen invalida (icono/placeholder)
PAUSA = 1.0             # segundos entre jugadores, para no saturar Wikipedia
REINTENTOS = 3

import precarga  # reutiliza EQUIPOS, slug() e IMG_DIR

UA = "TP1-IntroSoftware/1.0 (proyecto educativo)"

# Titulo EXACTO del articulo de Wikipedia cuando difiere del "nombre apellido".
# (acentos, desambiguaciones, apodos)
TITULOS = {
    "jose-luis-cuciuffo": "José Luis Cuciuffo",
    "jose-luis-brown": "José Luis Brown",
    "hector-enrique": "Héctor Enrique",
    "felix-mielli": "Félix (footballer, born 1937)",
    "carlos-alberto": "Carlos Alberto Torres",
    "hercules-brito": "Brito (footballer)",
    "everaldo-marques": "Everaldo (footballer, born 1944)",
    "clodoaldo-tavares": "Clodoaldo",
    "gerson-de-oliveira": "Gérson",
    "roberto-rivelino": "Rivellino",
    "jair-jairzinho": "Jairzinho",
    "edson-pele": "Pelé",
    "eduardo-tostao": "Tostão",
    "paulo-cesar-lima": "Paulo Cézar Lima",
    "jonas-edu": "Edu (footballer, born 1949)",
    "dario-maravilha": "Dadá Maravilha",
    "stephane-guivarch": "Stéphane Guivarc'h",
    "robert-pires": "Robert Pirès",
}


def curl(url, binario=False):
    """Devuelve el contenido de una URL usando curl (evita lios de SSL en Windows)."""
    salida = subprocess.run(
        ["curl", "-sL", "--max-time", "30", "-H", f"User-Agent: {UA}", url],
        capture_output=True,
    )
    return salida.stdout if binario else salida.stdout.decode("utf-8", "ignore")


def url_de_foto(titulo):
    """Pide a Wikipedia la imagen principal del articulo. Devuelve la URL o None.
    Reintenta ante fallos (suele ser rate-limiting temporal)."""
    api = (
        "https://en.wikipedia.org/w/api.php?action=query&redirects=1"
        f"&titles={quote(titulo)}&prop=pageimages&piprop=thumbnail"
        "&pithumbsize=500&format=json"
    )
    for intento in range(REINTENTOS):
        try:
            data = json.loads(curl(api))
            paginas = data["query"]["pages"]
            for pagina in paginas.values():
                thumb = pagina.get("thumbnail")
                if thumb and thumb.get("source"):
                    return thumb["source"]
            return None  # respuesta valida pero el articulo no tiene foto
        except Exception:
            time.sleep(2 * (intento + 1))  # backoff antes de reintentar
    return None


def ya_tiene_foto(slug):
    for ext in precarga.EXTENSIONES:
        if os.path.exists(os.path.join(precarga.IMG_DIR, slug + ext)):
            return True
    return False


def main():
    os.makedirs(precarga.IMG_DIR, exist_ok=True)
    bajadas, salteadas, fallidas = 0, 0, []

    for equipo in precarga.EQUIPOS:
        print(f"\n=== {equipo['nombre']} ===")
        for jugador in equipo["jugadores"]:
            nombre, apellido = jugador[2], jugador[3]
            slug = precarga.slug(nombre, apellido)

            if ya_tiene_foto(slug):
                print(f"  = {nombre} {apellido}: ya tiene foto, se respeta")
                salteadas += 1
                continue

            titulo = TITULOS.get(slug, f"{nombre} {apellido}")
            time.sleep(PAUSA)
            url = url_de_foto(titulo)
            if not url:
                print(f"  x {nombre} {apellido}: sin foto en Wikipedia ('{titulo}')")
                fallidas.append(f"{nombre} {apellido}")
                continue

            ext = os.path.splitext(url)[1].lower() or ".jpg"
            if ext not in precarga.EXTENSIONES:
                ext = ".jpg"
            destino = os.path.join(precarga.IMG_DIR, slug + ext)

            contenido = b""
            for intento in range(REINTENTOS):
                contenido = curl(url, binario=True)
                if contenido and len(contenido) >= MIN_BYTES:
                    break
                time.sleep(2 * (intento + 1))

            if not contenido or len(contenido) < MIN_BYTES:
                print(f"  x {nombre} {apellido}: descarga invalida ({len(contenido)} bytes)")
                fallidas.append(f"{nombre} {apellido}")
                continue

            with open(destino, "wb") as f:
                f.write(contenido)
            print(f"  + {nombre} {apellido}: {slug}{ext} ({len(contenido)//1024} KB)")
            bajadas += 1

    print(f"\nResumen: {bajadas} bajadas, {salteadas} respetadas, {len(fallidas)} sin foto.")
    if fallidas:
        print("Sin foto (quedan con avatar): " + ", ".join(fallidas))
    print("\nAhora corre:  ..\\venv\\Scripts\\python.exe precarga.py")


if __name__ == "__main__":
    main()

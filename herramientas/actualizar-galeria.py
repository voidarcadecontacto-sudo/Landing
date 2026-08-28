#!/usr/bin/env python3
"""
Regenera la galería de fotos de la landing.

Lee las imágenes de fotos-galeria/, las recorta a 4:3, las convierte a WebP
en dos tamaños (400px y 800px) y reescribe el bloque de la galería dentro de
public/index.html, entre los marcadores GALERIA:INICIO y GALERIA:FIN.

Uso:  ./actualizar-galeria.sh
"""

import os
import re
import sys
import unicodedata

try:
    from PIL import Image
except ImportError:
    sys.exit("Falta Pillow. Instálalo con:  python3 -m pip install --user Pillow")

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGEN = os.path.join(RAIZ, "fotos-galeria")
DESTINO = os.path.join(RAIZ, "public", "img", "fotos")
HTML = os.path.join(RAIZ, "public", "index.html")
MANIFIESTO = os.path.join(ORIGEN, "descripciones.txt")

ANCHOS = (400, 800)
PROPORCION = 4 / 3
CALIDAD = 82
EXTENSIONES = (".webp", ".jpg", ".jpeg", ".png", ".heic", ".tif", ".tiff")

# Fotos usadas fuera de la galería (tarjetas de evento). No se tocan.
PROTEGIDAS = {"ganadores", "evento-lleno"}

VERDE, ROJO, AMARILLO, GRIS, FIN = "\033[32m", "\033[31m", "\033[33m", "\033[90m", "\033[0m"


def slug(nombre):
    """'01-sala neón.webp' -> 'sala-neon' (sin número de orden ni extensión)."""
    base = os.path.splitext(nombre)[0]
    base = re.sub(r"^\d+[-_\s]*", "", base)
    base = unicodedata.normalize("NFKD", base).encode("ascii", "ignore").decode()
    base = re.sub(r"[^a-zA-Z0-9]+", "-", base).strip("-").lower()
    return base or "foto"


def leer_manifiesto():
    """Devuelve {archivo: (descripcion, (vf, hf, zoom))}."""
    datos = {}
    if not os.path.exists(MANIFIESTO):
        return datos
    for n, linea in enumerate(open(MANIFIESTO, encoding="utf-8"), 1):
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        partes = [p.strip() for p in linea.split("|")]
        if len(partes) < 2 or not partes[1]:
            print(f"{AMARILLO}  aviso: línea {n} de descripciones.txt sin descripción, se ignora{FIN}")
            continue
        archivo, descripcion = partes[0], partes[1]
        vf, hf, zoom = 0.5, 0.5, 1.0
        if len(partes) > 2 and partes[2]:
            try:
                nums = [float(x) for x in partes[2].split()]
                vf = nums[0] if len(nums) > 0 else vf
                hf = nums[1] if len(nums) > 1 else hf
                zoom = nums[2] if len(nums) > 2 else zoom
            except ValueError:
                print(f"{AMARILLO}  aviso: recorte inválido en línea {n}, uso el centro{FIN}")
        datos[archivo] = (descripcion, (vf, hf, zoom))
    return datos


def recortar(im, ar, hf=0.5, vf=0.5, zoom=1.0):
    """Recorta a la proporción ar. zoom<1 se acerca antes de recortar."""
    w, h = im.size
    if zoom < 1.0:
        nw, nh = int(w * zoom), int(h * zoom)
        x, y = int((w - nw) * hf), int((h - nh) * vf)
        im = im.crop((x, y, x + nw, y + nh))
        w, h = im.size
        hf = vf = 0.5
    if w / h > ar:
        nw = int(h * ar)
        x = int((w - nw) * hf)
        return im.crop((x, 0, x + nw, h))
    nh = int(w / ar)
    y = max(0, min(int((h - nh) * vf), h - nh))
    return im.crop((0, y, w, y + nh))


def main():
    if not os.path.isdir(ORIGEN):
        sys.exit(f"{ROJO}No existe la carpeta {ORIGEN}{FIN}")

    archivos = sorted(
        f for f in os.listdir(ORIGEN)
        if f.lower().endswith(EXTENSIONES) and not f.startswith(".")
    )
    if not archivos:
        sys.exit(f"{ROJO}No hay fotos en fotos-galeria/. No cambio nada.{FIN}")

    manifiesto = leer_manifiesto()
    os.makedirs(DESTINO, exist_ok=True)

    print(f"\n{GRIS}Procesando {len(archivos)} fotos de fotos-galeria/{FIN}\n")

    tarjetas, generados, sin_descripcion, peso = [], set(), [], 0

    for archivo in archivos:
        ruta = os.path.join(ORIGEN, archivo)
        mb = os.path.getsize(ruta) / 1024 / 1024
        if mb > 5:
            print(f"{AMARILLO}  aviso: {archivo} pesa {mb:.1f} MB. Funciona, pero no hace"
                  f" falta tanto: con 1600px sobra.{FIN}")

        nombre = slug(archivo)
        if nombre in PROTEGIDAS:
            print(f"{ROJO}  {archivo}: '{nombre}' es de las fotos de evento. Renómbrala.{FIN}")
            continue

        descripcion, (vf, hf, zoom) = manifiesto.get(archivo, (None, (0.5, 0.5, 1.0)))
        if not descripcion:
            descripcion = slug(archivo).replace("-", " ").capitalize()
            sin_descripcion.append(archivo)

        try:
            im = Image.open(ruta).convert("RGB")
        except Exception as e:
            print(f"{ROJO}  {archivo}: no se pudo abrir ({e}){FIN}")
            continue

        im = recortar(im, PROPORCION, hf=hf, vf=vf, zoom=zoom)

        # Nunca ampliar: ampliar una foto no agrega detalle, solo la vuelve borrosa.
        if im.size[0] < max(ANCHOS):
            print(f"{AMARILLO}  aviso: {archivo} da {im.size[0]}px después de recortar,"
                  f" menos de los {max(ANCHOS)}px ideales.")
            if zoom < 1.0:
                print(f"         Es por el zoom {zoom}. Usa una foto más grande"
                      f" o sube el zoom.{FIN}")
            else:
                print(f"         Usa una foto de al menos"
                      f" {int(max(ANCHOS) / (zoom or 1))}px de ancho.{FIN}")

        for ancho in ANCHOS:
            # Tamaño exacto, no thumbnail: el HTML declara width/height fijos y
            # el redondeo del recorte puede dejar la altura corrida por 1px.
            alto = round(ancho / PROPORCION)
            copia = im.resize((ancho, alto), Image.LANCZOS)
            salida = os.path.join(DESTINO, f"{nombre}-{ancho}.webp")
            copia.save(salida, "WEBP", quality=CALIDAD, method=6)
            generados.add(f"{nombre}-{ancho}.webp")
            peso += os.path.getsize(salida)

        tarjetas.append((nombre, descripcion))
        print(f"{VERDE}  ✓{FIN} {archivo:26s} -> {nombre}-{{400,800}}.webp")

    if not tarjetas:
        sys.exit(f"\n{ROJO}Ninguna foto se pudo procesar. No toco el HTML.{FIN}")

    # --- limpiar WebP huérfanos de galerías anteriores ---
    protegidos = {f"{n}-{a}.webp" for n in PROTEGIDAS for a in (600, 1200)}
    borrados = 0
    for f in os.listdir(DESTINO):
        if f.endswith(".webp") and f not in generados and f not in protegidos:
            os.remove(os.path.join(DESTINO, f))
            borrados += 1

    # --- reescribir el bloque del HTML ---
    html = open(HTML, encoding="utf-8").read()
    ini = html.find("<!-- GALERIA:INICIO")
    fin = html.find("<!-- GALERIA:FIN -->")
    if ini == -1 or fin == -1:
        sys.exit(f"{ROJO}No encontré los marcadores GALERIA:INICIO / GALERIA:FIN"
                 f" en public/index.html{FIN}")

    sizes = "(min-width: 1112px) 253px, (min-width: 700px) 33vw, calc(100vw - 32px)"
    filas = []
    for nombre, descripcion in tarjetas:
        alt = descripcion.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")
        filas.append(
            f'      <div class="shot">\n'
            f'        <img src="/img/fotos/{nombre}-400.webp"\n'
            f'             srcset="/img/fotos/{nombre}-400.webp 400w,'
            f' /img/fotos/{nombre}-800.webp 800w"\n'
            f'             sizes="{sizes}"\n'
            f'             width="800" height="600" loading="lazy" decoding="async"\n'
            f'             alt="{alt}">\n'
            f'      </div>'
        )

    bloque = (
        '<!-- GALERIA:INICIO — generado por herramientas/actualizar-galeria.py\n'
        '         No edites esto a mano: se reescribe completo en cada ejecución.\n'
        '         Para cambiar las fotos, edita fotos-galeria/ y corre ./actualizar-galeria.sh -->\n'
        '    <div class="grid grid--gallery">\n'
        + "\n".join(filas) + "\n"
        '    </div>\n'
        '    '
    )
    open(HTML, "w", encoding="utf-8").write(html[:ini] + bloque + html[fin:])

    # --- resumen ---
    print(f"\n{VERDE}Galería actualizada: {len(tarjetas)} fotos, {peso/1024:.0f} KB en total{FIN}")
    if borrados:
        print(f"{GRIS}  {borrados} archivos viejos eliminados{FIN}")
    if sin_descripcion:
        print(f"\n{AMARILLO}Estas fotos no tienen descripción en descripciones.txt:{FIN}")
        for f in sin_descripcion:
            print(f"{AMARILLO}  · {f}{FIN}")
        print(f"{AMARILLO}Les puse un texto provisional. Agrégales una descripción real:"
              f" Google la lee.{FIN}")

    print(f"\n{GRIS}Míralo antes de publicar:{FIN}")
    print(f"  cd public && python3 -m http.server 8000")
    print(f"\n{GRIS}Si te gusta, publícalo:{FIN}")
    print(f"  git add -A && git commit -m \"Actualiza fotos de la galeria\" && git push\n")


if __name__ == "__main__":
    main()

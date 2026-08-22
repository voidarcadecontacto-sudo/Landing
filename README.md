# Landing — Void Arcade

Landing page de Void Arcade: cyber, sala de juegos y simulador en Facatativá.
En producción: <https://voidarcadecy.com>

Sitio **estático**: HTML, CSS y JavaScript plano. Sin framework, sin `npm install`,
sin paso de compilación. Los archivos de `public/` son exactamente los que se publican.

---

## Estructura

```
wrangler.jsonc         Configuración de despliegue de Cloudflare. No lleva código de Worker.
public/                Todo lo que se publica. Esta carpeta es la raíz del sitio.
├── index.html         La página. Contenido, metadatos SEO y datos estructurados.
├── 404.html           Página de error.
├── css/styles.css     Estilos. Colores y tipografías arriba, en :root.
├── js/reservas.js     Arma el mensaje de WhatsApp del formulario.
├── img/               Fotos en WebP (dos tamaños c/u) + logo e iconos.
├── fonts/             Archivo Black y Barlow auto-hospedadas.
├── docs/              Menús en PDF.
├── _headers           Reglas de caché y seguridad que aplica Cloudflare.
├── robots.txt         Permite indexación y apunta al sitemap.
├── sitemap.xml        Mapa del sitio para Google.
├── site.webmanifest   Permite "añadir a pantalla de inicio" en el celular.
└── favicon.ico        Icono de la pestaña.
```

Todo lo que esté dentro de `public/` queda accesible en internet. Lo que esté fuera
(este README, `wrangler.jsonc`) no se publica.

La carpeta `Landing cyber sala de juegos/` es el **diseño original** exportado del
editor de canvas. Pesa 139 MB y está en `.gitignore`: se queda en tu computador.

> ⚠️ Esas fotos originales solo existen ahí. Si formateas el computador, se pierden.
> Guarda una copia en un disco externo o en la nube.

---

## Verla en tu computador

Abrir `index.html` con doble clic **no funciona bien**: las rutas son absolutas
(`/css/styles.css`) y necesitan un servidor. Desde la carpeta del proyecto:

```bash
cd public
python3 -m http.server 8000
```

Abre <http://localhost:8000>. Para detenerlo, `Ctrl + C`.

---

## Desplegar

El proyecto ya está conectado a Cloudflare. **Cada `git push` a `main` republica el
sitio automáticamente**, sin que tengas que entrar al panel.

Cloudflare ejecuta `npx wrangler deploy`, que lee `wrangler.jsonc` y sube `public/`.
No hay build command: no hace falta.

### Si tienes que reconectarlo desde cero

1. <https://dash.cloudflare.com> → **Compute** → **Workers** → **Create**.
2. **Import a repository** → autoriza GitHub → elige `voidarcadecontacto-sudo/Landing`.
3. Configuración:
   - Project name: `landing`
   - Build command: *(vacío)*
   - Deploy command: `npx wrangler deploy`
4. **Deploy**.

---

## Conectar el dominio voidarcadecy.com (está en Hostinger)

`voidarcadecy.com` es un dominio **apex** (sin `www` adelante). Para esos, Cloudflare
necesita manejar el DNS completo: **hay que cambiar los nameservers en Hostinger**.
El truco de poner solo un CNAME funciona para subdominios, no para el dominio raíz.

**Antes de empezar:** si usas correo con ese dominio (algo@voidarcadecy.com), revisa
que Cloudflare importe los registros MX en el paso 2. Si se pierden, el correo deja
de llegar.

### 1. Agregar el dominio en Cloudflare

- Panel de Cloudflare → **Add a domain** → escribe `voidarcadecy.com`.
- Elige el plan **Free**.
- Cloudflare escanea los registros DNS actuales. **Revisa que estén todos**, sobre
  todo los MX del correo. Si falta alguno, agrégalo a mano ahora.
- Al final te muestra **dos nameservers**, algo como
  `xxxx.ns.cloudflare.com` y `yyyy.ns.cloudflare.com`. Cópialos.

### 2. Cambiar los nameservers en Hostinger

- Entra a <https://hpanel.hostinger.com> → **Dominios** → `voidarcadecy.com`.
- Busca **Servidores DNS / Nameservers** → **Cambiar** → **Usar nameservers personalizados**.
- Borra los de Hostinger y pega los dos de Cloudflare.
- Guarda.

### 3. Esperar

La propagación tarda entre unos minutos y unas horas. Cloudflare te manda un correo
cuando el dominio queda activo. No sigas al paso 4 antes de eso.

### 4. Apuntar el dominio al sitio

- Cloudflare → **Compute** → **Workers** → proyecto `landing` → **Settings** →
  **Domains & Routes** → **Add** → **Custom domain**.
- Agrega `voidarcadecy.com`.
- Repite con `www.voidarcadecy.com` para que ambos funcionen.

El certificado HTTPS se emite solo. No compres SSL en Hostinger: no hace falta.

> No crees los registros DNS a mano antes de agregar el dominio en el proyecto.
> Si lo haces al revés, el sitio responde error 522.

---

## Cómo cambiar cosas

**Precios, productos, horarios** → están en `public/index.html` como texto normal.
Ojo: los precios de tarifas aparecen en **dos** lugares — las tarjetas de estaciones
y la tabla de paquetes por horas. Cambia ambos.

**Colores** → arriba de `public/css/styles.css`, en el bloque `:root`.

**Número de WhatsApp** → está en `public/js/reservas.js` (constante `TELEFONO`) y
varias veces en `public/index.html`:

```bash
grep -rl 573103420856 public | xargs sed -i '' 's|573103420856|TU-NUMERO|g'
```

**Fotos nuevas** → en `public/img/fotos/`, en dos tamaños (`nombre-400.webp` y
`nombre-800.webp`), y actualiza `src`, `srcset` y `alt` en `index.html`.
El `alt` describe la foto y Google lo lee: escribe algo real, no "foto1".

---

## Que Google te encuentre

El código ya trae lo que le corresponde: HTML semántico, título y descripción,
Open Graph, `sitemap.xml`, `robots.txt`, `alt` en todas las imágenes y datos
estructurados (`LocalBusiness` con dirección y horarios, más el `Event` del torneo).

Falta lo que solo puedes hacer tú, y **pesa más que el sitio web** para un negocio local:

1. **Google Business Profile** — <https://business.google.com>. Lo más importante de
   todo. Es lo que te hace aparecer en el mapa cuando alguien busca "sala de juegos
   Facatativá". Verifica el negocio, sube fotos, pon el horario real y enlaza
   `voidarcadecy.com`.
2. **Google Search Console** — <https://search.google.com/search-console>. Verifica el
   dominio y envía `https://voidarcadecy.com/sitemap.xml`.
3. **Reseñas.** El botón de Google Maps ya está en la página. Pídelas en el local:
   la cantidad y frecuencia de reseñas es de los factores más fuertes en búsqueda local.
4. **Mantén el sitio vivo.** Actualiza precios y eventos cuando cambien.

Cuando pase el torneo de FC 26, actualiza o quita el bloque `Event` del JSON-LD en
`index.html` — un evento vencido no ayuda.

---

## Rendimiento

Las fotos originales pesaban 139 MB. En WebP y dos tamaños, la galería completa quedó
en 603 KB, y solo se descarga si el visitante baja hasta ella (`loading="lazy"`).

Lo que carga un celular al abrir la página por primera vez: **~64 KB**.

Las tipografías están auto-hospedadas en `public/fonts/` en vez de pedirlas al CDN de
Google: una conexión menos y el texto aparece antes.

---

## Ramas

- `main` — lo que está publicado en producción.
- `develop` — integración. Trabaja aquí y haz merge a `main` cuando esté listo.
- `feature/*` — una rama por cambio, sale de `develop` y vuelve a `develop`.

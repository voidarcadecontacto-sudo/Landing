#!/usr/bin/env bash
# Regenera la galería de fotos a partir de la carpeta fotos-galeria/.
# Uso:  ./actualizar-galeria.sh
set -euo pipefail
cd "$(dirname "$0")"
exec python3 herramientas/actualizar-galeria.py "$@"

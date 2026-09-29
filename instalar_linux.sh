#!/usr/bin/env bash
# Instala lo necesario para correr Dino IA en Ubuntu (o Debian).
# Uso:  ./instalar_linux.sh
set -e
cd "$(dirname "$0")"

sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip fonts-dejavu-core

# Ubuntu no deja instalar paquetes con pip en el Python del sistema,
# así que se usa un entorno virtual dentro de la carpeta del proyecto.
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

echo
echo "Listo. Para usarlo:"
echo "  source .venv/bin/activate"
echo "  python entrenar.py"

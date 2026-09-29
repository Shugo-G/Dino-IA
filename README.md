# Dino IA

Réplica del juego del dinosaurio de Google Chrome en Python (pygame), en la que una población de
dinosaurios aprende a jugar sola con una red neuronal (7 → 7 ReLU → 2) y un algoritmo genético.

La explicación completa de cómo funciona está en
[Dino_IA_Explicacion_Red_Neuronal.docx](Dino_IA_Explicacion_Red_Neuronal.docx).

## Instalación

Hace falta Python 3.10 o más nuevo.

### Windows

```
pip install -r requirements.txt
```

### Ubuntu

```
chmod +x instalar_linux.sh
./instalar_linux.sh
source .venv/bin/activate
```

El script instala Python y sus herramientas con `apt` (pide la contraseña de `sudo`), crea un entorno
virtual en `.venv` e instala las dependencias adentro. Cada vez que abras una terminal nueva, activá
el entorno con `source .venv/bin/activate` antes de ejecutar el juego.

## Uso

Ejecutar los comandos desde la carpeta del proyecto (en Ubuntu, `python` es el del entorno virtual).

| Comando | Qué hace |
|---|---|
| `python juego.py` | Jugar con el teclado (↑ saltar, ↓ agacharse, ESC reiniciar) |
| `python entrenar.py` | Entrenar 1000 dinosaurios, con pausa al final de cada generación |
| `python entrenar.py --turbo --auto` | Entrenar a máxima velocidad y sin pausas |
| `python entrenar.py --cargar mejor_red.json` | Seguir entrenando desde una red guardada |
| `python juego.py --red mejor_red.npz` | Ver jugar sola a la mejor red guardada |

Teclas durante el entrenamiento: **T** turbo, **A** automático, **ENTER/ESPACIO** siguiente generación, **ESC** salir.

Al entrenar se crean `mejor_red.npz` (exacto) y `mejor_red.json` (legible) con la mejor red del
entrenamiento actual. Otras opciones: `python entrenar.py --help`.

### Entrenar sin pantalla (servidor Linux)

En una máquina sin entorno gráfico, se puede entrenar sin abrir ventana:

```
SDL_VIDEODRIVER=dummy python entrenar.py --turbo --auto
```

El progreso se ve en la terminal. Para cortarlo, Ctrl+C.

## Archivos

| Archivo | Contenido |
|---|---|
| `mundo.py` | El juego: física, obstáculos, choques y las 7 entradas de la red |
| `red.py` | La red neuronal, la mutación y la evolución |
| `entrenar.py` | El ciclo de generaciones y la pantalla de entrenamiento |
| `graficos.py` | El dibujo del juego y del panel de la red |
| `juego.py` | El juego para jugar con teclado o ver una red guardada |

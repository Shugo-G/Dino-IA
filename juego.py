"""DinoRun jugable con el teclado (↑ saltar, ↓ agacharse / caer rápido, ESC reiniciar).

Con --red mejor_red.npz juega la red guardada en lugar del teclado.
"""
import argparse

import numpy as np
import pygame

from graficos import Graficos
from mundo import ALTO, ANCHO, ESCALA_ENTRADAS, FPS, Mundo
from red import Poblacion, cargar_red

TEXTO_FINAL = 'Juega más, llora menos'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--red', metavar='RUTA', help='red entrenada (.npz) que juega sola')
    args = parser.parse_args()

    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption('DinoRun by Shugo')
    g = Graficos(pantalla)
    reloj = pygame.time.Clock()

    ia = Poblacion(1, base=cargar_red(args.red)) if args.red else None

    mundo = Mundo(1)
    record = 0
    while True:
        reloj.tick(FPS)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                return
        teclas = pygame.key.get_pressed()

        if mundo.terminado:
            record = max(record, mundo.puntuacion)
            if teclas[pygame.K_ESCAPE] or ia is not None:
                mundo.reiniciar()
        elif ia is not None:
            salida = ia.decidir(mundo.entradas() / ESCALA_ENTRADAS)
            mundo.paso(salida[:, 0] > 0, salida[:, 1] > 0)
        else:
            mundo.paso(np.array([teclas[pygame.K_UP]]), np.array([teclas[pygame.K_DOWN]]))

        g.escenario(mundo)
        g.dino(mundo, 0)
        g.puntuacion(mundo, record)
        if mundo.terminado:
            g.texto(TEXTO_FINAL, ANCHO // 2, ALTO // 2, g.fuente_grande, centro=True)
        pygame.display.flip()


if __name__ == '__main__':
    main()

"""Entrena una población de dinosaurios con un algoritmo genético.

Teclas:  T = modo turbo (sin dibujar ni límite de FPS)   A = pasar de generación automáticamente
         ENTER / ESPACIO = siguiente generación (en la pausa)   ESC = salir

La mejor red de este entrenamiento se guarda en mejor_red.npz y mejor_red.json
(se sobrescribe la de entrenamientos anteriores).
"""
import argparse
import datetime
import time

import numpy as np
import pygame

from graficos import Graficos
from mundo import ALTO, ANCHO, ESCALA_ENTRADAS, FPS, Mundo
from red import Poblacion, cargar_red, guardar_red

ETIQUETAS = ('distancia', 'obst. x', 'obst. y', 'obst. ancho', 'obst. alto', 'dino y', 'velocidad')
RUTA_MEJOR = 'mejor_red.npz'


class Salir(Exception):
    pass


def es_tecla(evento, *teclas):
    return evento.type == pygame.KEYDOWN and evento.key in teclas


def eventos_comunes(evento):
    if evento.type == pygame.QUIT or es_tecla(evento, pygame.K_ESCAPE):
        raise Salir


def esperar_siguiente(g, lineas):
    """Pausa al terminar una generación. Devuelve True si se activó el modo automático."""
    p = g.pantalla
    velo = pygame.Surface((ANCHO, ALTO))
    velo.fill((255, 255, 255))
    velo.set_alpha(210)
    p.blit(velo, (0, 0))
    caja = pygame.Rect(0, 0, 560, (len(lineas) + 2) * 26 + 20)
    caja.midtop = (ANCHO // 2, 88)
    pygame.draw.rect(p, (255, 255, 255), caja)
    pygame.draw.rect(p, (0, 0, 0), caja, 2)
    for k, linea in enumerate(lineas):
        g.texto(linea, ANCHO // 2, 110 + k * 26, centro=True)
    g.texto('ENTER / ESPACIO: siguiente generación    A: automático    ESC: salir',
            ANCHO // 2, 110 + (len(lineas) + 1) * 26, g.fuente_chica, centro=True)
    pygame.display.flip()
    while True:
        for evento in pygame.event.get():
            eventos_comunes(evento)
            if es_tecla(evento, pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                return False
            if es_tecla(evento, pygame.K_a):
                return True
        pygame.time.wait(20)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-n', '--poblacion', type=int, default=1000, help='dinos por generación')
    parser.add_argument('--dibujar', type=int, default=100, help='máximo de dinos dibujados a la vez')
    parser.add_argument('--cargar', metavar='RUTA', help='empezar desde una red guardada (.npz o .json)')
    parser.add_argument('--semilla', type=int, help='semilla para repetir un entrenamiento')
    parser.add_argument('--turbo', action='store_true', help='arrancar en modo turbo')
    parser.add_argument('--auto', action='store_true', help='pasar de generación sin pausar')
    parser.add_argument('--limite', type=int, default=5000,
                        help='puntos a los que se corta la generación (0 = sin límite)')
    args = parser.parse_args()

    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption('Dino IA - entrenamiento')
    g = Graficos(pantalla)
    try:
        entrenar(args, g)
    except (Salir, KeyboardInterrupt):
        pass
    pygame.quit()


def entrenar(args, g):
    pantalla = g.pantalla
    reloj = pygame.time.Clock()
    base = cargar_red(args.cargar) if args.cargar else None
    poblacion = Poblacion(args.poblacion, args.semilla, base)
    generacion = 0
    prom_ult = max_ult = record = 0
    turbo, auto = args.turbo, args.auto

    while True:
        semilla_mundo = None if args.semilla is None else args.semilla + generacion
        mundo = Mundo(args.poblacion, semilla_mundo)
        ultimo_dibujo = 0.0

        while True:
            for evento in pygame.event.get():
                eventos_comunes(evento)
                if es_tecla(evento, pygame.K_t):
                    turbo = not turbo
                if es_tecla(evento, pygame.K_a):
                    auto = not auto

            crudas = mundo.entradas()
            X = crudas / ESCALA_ENTRADAS
            salida = poblacion.decidir(X)
            mundo.paso(salida[:, 0] > 0, salida[:, 1] > 0)

            if mundo.terminado or (args.limite and mundo.puntuacion >= args.limite):
                break
            ahora = time.perf_counter()
            if turbo and ahora - ultimo_dibujo < 0.2:
                continue
            ultimo_dibujo = ahora

            vivos = np.flatnonzero(mundo.vivo)
            # Se destaca al campeón de la generación anterior (índice 0) mientras siga vivo
            destacado = 0 if mundo.vivo[0] else vivos[0]
            if turbo:
                pantalla.fill((255, 255, 255))
                g.texto('MODO TURBO (T para ver)', ANCHO // 2, ALTO // 2 + 40, g.fuente_grande, centro=True)
            else:
                g.escenario(mundo)
                for i in vivos[:args.dibujar]:
                    if i != destacado:
                        g.dino(mundo, i, transp=True)
                g.dino(mundo, destacado)
            g.red(poblacion, destacado, crudas[destacado], X[destacado], ETIQUETAS)
            hud = (f'Generación: {generacion}',
                   f'Promedio (últ. gen): {prom_ult:.0f}',
                   f'Máximo (últ. gen): {max_ult}',
                   f'Récord: {record}',
                   f'Vivos: {mundo.vivos}/{mundo.n}')
            for k, linea in enumerate(hud):
                g.texto(linea, 20, 15 + k * 22)
            g.texto(f'T: turbo   A: automático ({"sí" if auto else "no"})', 20, ALTO - 18, g.fuente_chica)
            g.puntuacion(mundo)
            pygame.display.flip()
            if not turbo:
                reloj.tick(FPS)

        puntos = mundo.frames_vivo // 2
        prom_ult, max_ult = puntos.mean(), int(puntos.max())
        campeon = int(np.argmax(mundo.frames_vivo))
        guardada = max_ult > record
        if guardada:
            record = max_ult
            guardar_red(RUTA_MEJOR, poblacion.red(campeon), ETIQUETAS,
                        puntos=max_ult, generacion=generacion,
                        fecha=datetime.datetime.now().isoformat(timespec='seconds'))
        resumen = f'Gen {generacion} | promedio {prom_ult:.1f} | máximo {max_ult} | récord {record}'
        print(resumen + ('  -> red guardada' if guardada else ''))

        if not auto:
            auto = esperar_siguiente(g, [
                f'Generación {generacion} terminada',
                f'Promedio: {prom_ult:.1f}    Máximo: {max_ult}',
                f'Récord: {record}' + ('  (¡nuevo! red guardada)' if guardada else ''),
            ])
        poblacion.evolucionar(mundo.frames_vivo)
        generacion += 1


if __name__ == '__main__':
    main()

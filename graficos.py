"""Dibujo con pygame. Las imágenes se cargan una sola vez y las comparten todos los dinos."""
import os

import pygame

from mundo import ANCHO, SUELO, DINO_X

BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
GRIS = (150, 150, 150)
VERDE = (40, 200, 40)
ROJO = (220, 40, 40)
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Assets')
ALPHA_POBLACION = 70   # transparencia de los dinos que no están destacados


def cargar(nombre):
    img = pygame.image.load(os.path.join(ASSETS, nombre)).convert()
    img.set_colorkey(BLANCO)
    return img


def transparente(img):
    copia = img.copy()
    copia.set_alpha(ALPHA_POBLACION)
    return copia


class Graficos:
    def __init__(self, pantalla):
        self.pantalla = pantalla
        self.correr = [cargar('DinoRun1.png'), cargar('DinoRun2.png')]
        self.agachado = [cargar('DinoDown1.png'), cargar('DinoDown2.png')]
        self.saltar = cargar('DinoJump.png')
        self.muerto = cargar('DinoDead.png')
        self.cactus = [cargar(f'cactus{i}.png') for i in range(1, 7)]
        self.pajaro = [cargar('pajaro1.png'), cargar('pajaro2.png')]
        self.suelo = cargar('bg.png')

        self.correr_t = [transparente(i) for i in self.correr]
        self.agachado_t = [transparente(i) for i in self.agachado]
        self.saltar_t = transparente(self.saltar)

        self.fuente_chica = pygame.font.SysFont('consolas', 13)
        self.fuente = pygame.font.SysFont('consolas', 16)
        self.fuente_grande = pygame.font.SysFont('consolas', 36)

    def texto(self, txt, x, y, fuente=None, centro=False, derecha=False):
        sup = (fuente or self.fuente).render(txt, True, NEGRO)
        rect = sup.get_rect()
        if centro:
            rect.center = (x, y)
        elif derecha:
            rect.topright = (x, y)
        else:
            rect.topleft = (x, y)
        self.pantalla.blit(sup, rect)

    def escenario(self, mundo):
        p = self.pantalla
        p.fill(BLANCO)
        ancho_suelo = self.suelo.get_width()
        x = -(mundo.suelo_x % ancho_suelo)
        p.blit(self.suelo, (x, SUELO - 10))
        p.blit(self.suelo, (x + ancho_suelo, SUELO - 10))
        frame_ave = (mundo.frame // 4) % 2
        for o in mundo.obstaculos:
            img = self.pajaro[frame_ave] if o.tipo == 'pajaro' else self.cactus[o.tipo]
            p.blit(img, (o.x, o.bottom - img.get_height()))

    def dino(self, mundo, i, transp=False):
        paso = (mundo.frame // 4) % 2
        if not mundo.vivo[i]:
            img = self.muerto
        elif mundo.en_aire[i]:
            img = self.saltar_t if transp else self.saltar
        elif mundo.agachado[i]:
            img = (self.agachado_t if transp else self.agachado)[paso]
        else:
            img = (self.correr_t if transp else self.correr)[paso]
        self.pantalla.blit(img, (DINO_X, mundo.y[i] - img.get_height()))

    def red(self, poblacion, i, crudas, normalizadas, etiquetas, x0=470, y0=22):
        """Dibuja la red del dino i: verde = peso positivo, rojo = negativo, gris = neurona activa."""
        p = self.pantalla
        h, salida = poblacion.activaciones(i, normalizadas)
        sep, radio = 26, 10
        col_ent, col_ocu, col_sal = x0, x0 + 80, x0 + 160
        pos_ent = [(col_ent, y0 + k * sep) for k in range(len(crudas))]
        pos_ocu = [(col_ocu, y0 + k * sep) for k in range(len(h))]
        pos_sal = [(col_sal, y0 + (k + 2.5) * sep) for k in range(len(salida))]

        for capa, origen, destino in ((poblacion.W1[i], pos_ent, pos_ocu),
                                      (poblacion.W2[i], pos_ocu, pos_sal)):
            for a, pa in enumerate(origen):
                for b, pb in enumerate(destino):
                    w = capa[a, b]
                    ancho = min(4, int(abs(w) * 1.5))
                    if ancho:
                        pygame.draw.line(p, VERDE if w > 0 else ROJO, pa, pb, ancho)

        for pos, activo in [(q, False) for q in pos_ent] + \
                           list(zip(pos_ocu, h > 0)) + list(zip(pos_sal, salida > 0)):
            pygame.draw.circle(p, GRIS if activo else BLANCO, pos, radio)
            pygame.draw.circle(p, NEGRO, pos, radio, 1)

        for (x, y), etiqueta, valor in zip(pos_ent, etiquetas, crudas):
            self.texto(f'{etiqueta}: {valor:.0f}', x - radio - 6, y - 7, self.fuente_chica, derecha=True)
        for (x, y), etiqueta in zip(pos_sal, ('saltar', 'agacharse')):
            self.texto(etiqueta, x + radio + 6, y - 7, self.fuente_chica)

    def puntuacion(self, mundo, record=None):
        txt = f'{mundo.puntuacion:05d}'
        if record is not None:
            txt = f'HI {record:05d}  {txt}'
        self.texto(txt, ANCHO - 20, 12, derecha=True)

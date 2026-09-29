"""Lógica del juego sin pygame: un mundo compartido y N dinosaurios vectorizados con numpy.

Todo se mide en frames (no en milisegundos), así la simulación es idéntica
corra a 30 FPS con dibujo o a miles de FPS sin dibujar.
"""
import random

import numpy as np

# PANTALLA
ANCHO = 800
ALTO = 400
FPS = 30

# DINOSAURIO
SUELO = 380          # borde inferior del dino cuando está en el suelo
DINO_X = 100
DINO_W, DINO_H = 40, 43            # tamaño de DinoRun/DinoJump
AGACHADO_W, AGACHADO_H = 55, 26    # tamaño de DinoDown
SALTO_VEL = 25.0
GRAVEDAD = 3.4
GRAVEDAD_CAIDA = GRAVEDAD * 4      # con ↓ en el aire cae rápido
MARGEN = 3                         # recorte de los hitbox para perdonar los bordes del sprite

# VELOCIDAD DEL JUEGO
VEL_INICIAL = 12.0
VEL_MAX = 30.0
ACELERACION = 0.02

# OBSTÁCULOS (tamaños de los PNG)
CACTUS_TAM = [(15, 33), (32, 33), (49, 33), (23, 45), (48, 45), (73, 46)]
PAJARO_W, PAJARO_H = 43, 30
PAJARO_ALTURAS = (SUELO, SUELO - 30, SUELO - 100)  # saltar / agacharse / pasa por arriba
PROB_PAJARO = 1 / 11
ESPERA_CACTUS = (26, 45)   # frames hasta el próximo obstáculo
ESPERA_PAJARO = (24, 36)

# Valores con los que se dividen las entradas para dejarlas en un rango ~[0, 1]
ESCALA_ENTRADAS = np.array([ANCHO, ANCHO, ALTO, 100, 100, ALTO, VEL_MAX], dtype=float)


class Obstaculo:
    __slots__ = ('tipo', 'x', 'bottom', 'w', 'h')

    def __init__(self, tipo, bottom, w, h):
        self.tipo = tipo      # 0-5: cactus, 'pajaro'
        self.x = float(ANCHO)
        self.bottom = bottom
        self.w = w
        self.h = h

    @property
    def top(self):
        return self.bottom - self.h


class Mundo:
    def __init__(self, n, semilla=None):
        self.n = n
        self.rng = random.Random(semilla)
        self.reiniciar()

    def reiniciar(self):
        n = self.n
        self.frame = 0
        self.velocidad = VEL_INICIAL
        self.suelo_x = 0.0
        self.obstaculos = []
        self.proximo_spawn = 20

        self.y = np.full(n, SUELO, dtype=float)   # borde inferior de cada dino
        self.vy = np.zeros(n)
        self.en_aire = np.zeros(n, dtype=bool)
        self.agachado = np.zeros(n, dtype=bool)
        self.vivo = np.ones(n, dtype=bool)
        self.frames_vivo = np.zeros(n, dtype=np.int64)   # aptitud

    @property
    def puntuacion(self):
        return self.frame // 2

    @property
    def vivos(self):
        return int(self.vivo.sum())

    @property
    def terminado(self):
        return not self.vivo.any()

    def alto_dinos(self):
        return np.where(self.agachado, AGACHADO_H, DINO_H)

    def proximo_obstaculo(self):
        for o in self.obstaculos:          # están ordenados por x
            if o.x + o.w > DINO_X:
                return o
        return None

    def entradas(self):
        """Matriz (n, 7): distancia, x, y, ancho y alto del obstáculo, y del dino, velocidad."""
        X = np.empty((self.n, 7))
        o = self.proximo_obstaculo()
        if o is None:
            X[:, 0:5] = (ANCHO, ANCHO, 0, 0, 0)
        else:
            X[:, 0:5] = (o.x - (DINO_X + DINO_W), o.x, o.top, o.w, o.h)
        X[:, 5] = self.y - self.alto_dinos()
        X[:, 6] = self.velocidad
        return X

    def paso(self, saltar, agachar):
        """Avanza un frame. `saltar` y `agachar` son arrays booleanos de tamaño n."""
        vivo = self.vivo
        saltar = saltar & vivo
        agachar = agachar & vivo

        # Movimiento de los dinos
        en_suelo = ~self.en_aire
        inicia = en_suelo & saltar & ~agachar
        self.vy[inicia] = -SALTO_VEL
        self.en_aire |= inicia
        self.agachado = en_suelo & ~inicia & agachar

        aire = self.en_aire & vivo
        self.vy[aire] += np.where(agachar[aire], GRAVEDAD_CAIDA, GRAVEDAD)
        self.y[aire] += self.vy[aire]
        aterriza = aire & (self.y >= SUELO)
        self.y[aterriza] = SUELO
        self.vy[aterriza] = 0
        self.en_aire[aterriza] = False

        # Obstáculos
        for o in self.obstaculos:
            o.x -= self.velocidad
        if self.obstaculos and self.obstaculos[0].x + self.obstaculos[0].w < 0:
            self.obstaculos.pop(0)
        self.proximo_spawn -= 1
        if self.proximo_spawn <= 0:
            self._generar_obstaculo()

        # Colisiones: la x es la misma para todos, solo cambia el tamaño y la altura
        ancho = np.where(self.agachado, AGACHADO_W, DINO_W)
        izq = DINO_X + MARGEN
        der = DINO_X + ancho - MARGEN
        abajo = self.y - MARGEN
        arriba = self.y - self.alto_dinos() + MARGEN
        choque = np.zeros(self.n, dtype=bool)
        for o in self.obstaculos:
            if o.x + MARGEN > DINO_X + AGACHADO_W:
                break
            choque |= ((izq < o.x + o.w - MARGEN) & (der > o.x + MARGEN)
                       & (arriba < o.bottom - MARGEN) & (abajo > o.top + MARGEN))
        self.vivo &= ~choque

        self.frame += 1
        self.frames_vivo[self.vivo] = self.frame
        self.velocidad = min(self.velocidad + ACELERACION, VEL_MAX)
        self.suelo_x += self.velocidad

    def _generar_obstaculo(self):
        rng = self.rng
        if rng.random() < PROB_PAJARO:
            o = Obstaculo('pajaro', rng.choice(PAJARO_ALTURAS), PAJARO_W, PAJARO_H)
            self.proximo_spawn = rng.randint(*ESPERA_PAJARO)
        else:
            tipo = rng.randrange(len(CACTUS_TAM))
            w, h = CACTUS_TAM[tipo]
            o = Obstaculo(tipo, SUELO, w, h)
            self.proximo_spawn = rng.randint(*ESPERA_CACTUS)
        self.obstaculos.append(o)

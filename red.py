"""Población de redes neuronales 7 -> 7 (ReLU) -> 2, evaluadas todas juntas con numpy.

Cada dinosaurio tiene sus propios pesos: la fila i de W1, b1, W2 y b2.
En total son 7*7 + 7 + 7*2 + 2 = 72 números por dinosaurio (su "genoma").
"""
import json
import os

import numpy as np

N_ENTRADAS, N_OCULTAS, N_SALIDAS = 7, 7, 2
PARAMETROS = ('W1', 'b1', 'W2', 'b2')

FRAC_ELITE = 0.05      # porcentaje de los mejores que pasan sin cambios y son padres
TASA_MUTACION = 0.2    # probabilidad de que cada peso mute
SIGMA_MUTACION = 0.4   # tamaño de la mutación


def relu(x):
    return np.maximum(0, x)


class Poblacion:
    def __init__(self, n, semilla=None, base=None):
        self.n = n
        self.rng = np.random.default_rng(semilla)
        r = self.rng
        self.W1 = r.normal(0, 1, (n, N_ENTRADAS, N_OCULTAS))
        self.b1 = r.normal(0, 1, (n, N_OCULTAS))
        self.W2 = r.normal(0, 1, (n, N_OCULTAS, N_SALIDAS))
        self.b2 = r.normal(0, 1, (n, N_SALIDAS))
        if base is not None:
            # Todos parten de la red cargada; el 0 queda idéntico y el resto se muta
            for nombre in PARAMETROS:
                getattr(self, nombre)[:] = base[nombre]
            self._mutar(desde=1)

    def decidir(self, X):
        """X: (n, 7) entradas normalizadas -> (n, 2) salidas [saltar, agacharse]."""
        H = relu(np.einsum('ni,nij->nj', X, self.W1) + self.b1)
        return np.einsum('ni,nij->nj', H, self.W2) + self.b2

    def activaciones(self, i, x):
        """Capa oculta y salida de un solo dinosaurio (para dibujar su red)."""
        h = relu(x @ self.W1[i] + self.b1[i])
        return h, h @ self.W2[i] + self.b2[i]

    def evolucionar(self, aptitud):
        """Arma la próxima generación a partir de los mejores de esta."""
        orden = np.argsort(-aptitud, kind='stable')
        n_elite = max(1, int(self.n * FRAC_ELITE))
        elite = orden[:n_elite]
        padres = self.rng.choice(elite, size=self.n)
        padres[:n_elite] = elite           # el mejor queda en el índice 0
        for nombre in PARAMETROS:
            setattr(self, nombre, getattr(self, nombre)[padres])
        self._mutar(desde=n_elite)
        return orden[0]

    def _mutar(self, desde):
        for nombre in PARAMETROS:
            p = getattr(self, nombre)[desde:]
            mascara = self.rng.random(p.shape) < TASA_MUTACION
            p += mascara * self.rng.normal(0, SIGMA_MUTACION, p.shape)

    def red(self, i):
        return {nombre: getattr(self, nombre)[i].copy() for nombre in PARAMETROS}


def ruta_json(ruta):
    return os.path.splitext(ruta)[0] + '.json'


def guardar_red(ruta, red, etiquetas, **info):
    """Guarda la red en .npz (exacto) y en .json (legible, redondeado) con los datos de `info`."""
    np.savez(ruta, **red)

    def fila(valores):
        return json.dumps([round(v, 4) for v in valores])

    items = [f'  {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)}' for k, v in info.items()]
    items.append(f'  "entradas": {json.dumps(list(etiquetas), ensure_ascii=False)}')
    items.append('  "salidas": ["saltar", "agacharse"]')
    for nombre in PARAMETROS:
        valores = red[nombre].tolist()
        if red[nombre].ndim == 1:
            items.append(f'  "{nombre}": {fila(valores)}')
        else:
            filas = ',\n    '.join(fila(f) for f in valores)
            items.append(f'  "{nombre}": [\n    {filas}\n  ]')
    with open(ruta_json(ruta), 'w', encoding='utf-8') as f:
        f.write('{\n' + ',\n'.join(items) + '\n}\n')


def cargar_red(ruta):
    """Carga una red desde .npz o .json."""
    if ruta.endswith('.json'):
        with open(ruta, encoding='utf-8') as f:
            datos = json.load(f)
        return {nombre: np.array(datos[nombre], dtype=float) for nombre in PARAMETROS}
    with np.load(ruta) as datos:
        return {nombre: datos[nombre] for nombre in PARAMETROS}

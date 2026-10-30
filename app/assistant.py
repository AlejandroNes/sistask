"""Clasificador local Naive Bayes entrenado con los gastos ya registrados."""

import math
import re
from collections import Counter, defaultdict


def palabras(texto):
    return re.findall(r'[^\W\d_]+', texto.casefold(), flags=re.UNICODE)


def sugerir_subcategoria(descripcion, ejemplos):
    documentos = Counter()
    terminos = defaultdict(Counter)
    vocabulario = set()
    for subcategoria_id, nombre, texto in ejemplos:
        tokens = palabras(texto or '')
        if not tokens:
            continue
        documentos[(subcategoria_id, nombre)] += 1
        terminos[(subcategoria_id, nombre)].update(tokens)
        vocabulario.update(tokens)
    if sum(documentos.values()) < 3 or len(documentos) < 2:
        return None
    tokens = [token for token in palabras(descripcion) if token in vocabulario]
    if not tokens:
        return None
    total = sum(documentos.values())
    puntuaciones = {}
    for categoria, cantidad in documentos.items():
        cuenta = terminos[categoria]
        denominador = sum(cuenta.values()) + len(vocabulario)
        puntuaciones[categoria] = math.log(cantidad / total) + sum(
            math.log((cuenta[token] + 1) / denominador) for token in tokens
        )
    return max(puntuaciones, key=puntuaciones.get)[1]

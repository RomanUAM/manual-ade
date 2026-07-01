#!/usr/bin/env python3
"""Simulador didactico para Taguchi y violeta africana.

Genera datos pequenos para que el estudiante observe variabilidad antes de
aplicar un analisis formal.
"""

from __future__ import annotations

import random
import statistics


def simular(seed: int = 7) -> None:
    random.seed(seed)
    control = [random.gauss(10.0, 1.2) for _ in range(8)]
    tratamiento = [random.gauss(11.0, 1.2) for _ in range(8)]
    print("Pregunta:", 'Como explorar varios factores sin hacer todos los experimentos?')
    print("Media control:", round(statistics.mean(control), 3))
    print("Media tratamiento:", round(statistics.mean(tratamiento), 3))
    print("Diferencia observada:", round(statistics.mean(tratamiento) - statistics.mean(control), 3))
    print("Advertencia: una diferencia observada no basta; hay que compararla con la variabilidad.")


if __name__ == "__main__":
    simular()

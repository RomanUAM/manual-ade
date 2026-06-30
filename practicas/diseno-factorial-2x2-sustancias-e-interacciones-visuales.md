# Diseno factorial 2x2: sustancias e interacciones visuales

## Situacion de partida

Una empresa quiere producir papeles decorativos con cambios visuales controlados. La pregunta no es solamente que mezcla "se ve mejor", sino si dos sustancias producen efectos medibles por separado o si su combinacion genera un comportamiento nuevo.

Para que el estudiante vea la diferencia entre observar y experimentar, el capitulo contrasta tres situaciones:

- hongos en tortillas: observacion biologica util para discutir factores, contaminacion y control, pero insuficiente si no se define un diseno;
- lentejas: sistema sencillo, ya desarrollado en el material LaTeX local, para comparar germinacion, crecimiento, presencia de hongos y control de tratamientos;
- curcuma y cloro en papel: practica factorial 2^2 completa, con tratamientos, blanco, replicas y medicion con luxometro.

## Objetivo general

Construir una practica de Diseno factorial 2^2 a partir de la fuente indicada y convertirla en una actividad didactica verificable.

## Evidencia de partida

- Fuente principal: `docs/libro_latex/Capitulos/02-conceptos.tex`
- Tema: Diseno factorial 2^2
- Fecha de creacion: 2026-06-29

## Diseno experimental

| Elemento | Definicion inicial |
|---|---|
| Unidad experimental | Un post-it tratado bajo una combinacion especifica |
| Factores | Concentracion de curcuma y concentracion de cloro comercial |
| Niveles | Curcuma: 1 g y 4 g; cloro: 5 g y 10 g |
| Tratamientos | T1 (-,-), T2 (-,+), T3 (+,-), T4 (+,+) |
| Repeticiones | 6 unidades experimentales por tratamiento |
| Blanco | Papel tratado con 0 g de curcuma y 0 g de cloro |
| Variables respuesta | Bloqueo o transmision de luz, intensidad visual, uniformidad y contraste |
| Variables controladas | Agua, sal, distancia de aspersion, numero de aspersiones, papel y tiempo de secado |

## Procedimiento

1. Preparar las soluciones con base comun de agua y sal.
2. Construir la matriz 2^2 antes de aplicar sustancias.
3. Asignar tratamientos a unidades experimentales independientes.
4. Aplicar tres aspersiones a distancia constante.
5. Registrar fotografia y medicion con luxometro.
6. Calcular porcentaje de bloqueo de luz.
7. Comparar efectos principales e interaccion.
8. Usar el blanco para decidir si el cambio se debe al tratamiento o al proceso.

## Analisis esperado

El analisis esperado es un ANOVA factorial 2^2 con efectos principales de curcuma y cloro e interaccion curcuma-cloro. La discusion debe iniciar con la grafica de interaccion, porque si la interaccion domina, los efectos principales aislados pueden confundir al estudiante.

## Limitaciones

No usar conclusiones hasta verificar datos y supuestos. La practica de hongos en tortillas aparece indexada en el manifiesto de Estadistica y debe tratarse como contraste didactico: permite explicar por que una experiencia biologica interesante no equivale automaticamente a un diseno 2^2 si no hay niveles, replicas, control de contaminacion y variable respuesta defendible.

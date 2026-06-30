# Politica de publicacion reutilizable

## Proposito

El sistema debe poder recibir una coleccion nueva de PDFs, notas, presentaciones, datos o imagenes y producir tres salidas limpias:

1. Una base de conocimiento interna.
2. Una pagina compartible para estudiantes.
3. Un archivo descargable autorizado, normalmente PDF.

El sistema no debe publicar la materia prima como si fuera el producto final.

## Regla de derechos

Todo material de entrada se clasifica en una de estas categorias:

- `propio`: creado por Roman A. Mora o por el proyecto.
- `curso_autorizado`: material docente que se puede compartir con estudiantes.
- `referencia_externa`: articulo, libro, capitulo, tesis, repositorio o PDF ajeno.
- `desconocido`: no hay evidencia suficiente para publicarlo.

Solo `propio` y `curso_autorizado` pueden aparecer como descarga publica.

`referencia_externa` y `desconocido` pueden usarse unicamente como insumo interno para:

- identificar conceptos;
- contrastar metodologia;
- construir fichas de conocimiento;
- redactar explicaciones originales;
- generar actividades propias.

No deben enlazarse, copiarse, incrustarse ni redistribuirse en la pagina publica.

## Entrada reutilizable

Cada PDF o archivo incorporado debe pasar por ingesta antes de usarse:

1. Registrar ruta, tipo de archivo y estado de lectura.
2. Extraer texto o marcar pendiente.
3. Crear ficha de conocimiento.
4. Clasificar derechos.
5. Decidir uso didactico.
6. Definir si puede publicarse o solo alimentar la memoria interna.

Ningun agente debe decidir por nombre de archivo.

## Salidas obligatorias

Cada corrida completa debe producir:

- `memory/materiales_investigados.json`: fichas y clasificacion de uso.
- `memory/matriz_investigacion_material.md`: matriz humana de lectura.
- Un PDF descargable generado por el proyecto.
- Una pagina en `site/` que enlace solo archivos publicables.

## Pagina compartible

La pagina publica debe servirse desde `site/`, no desde la raiz del repositorio.

Comando recomendado:

```bash
python3 scripts/maestro.py servir --port 8765
```

No usar como publicacion final:

```bash
python3 -m http.server 8765
```

Ese comando expone `data/raw/` y puede publicar archivos sin permiso.

## Criterio editorial

La pagina no debe parecer inventario. Debe mostrar:

- el manual descargable;
- la presentacion descargable si existe;
- un indice navegable por preguntas de aprendizaje;
- recursos generados o autorizados;
- actividades o practicas integradas.

Los archivos fuente, TXT, LaTeX, hojas de calculo y PDFs externos son insumos internos, no material principal del estudiante.

## Contrato de reutilizacion

Para reutilizar el sistema con otro conjunto de PDFs:

1. Colocar archivos en `data/raw/<proyecto>/`.
2. Ejecutar `python3 scripts/maestro.py investigar`.
3. Revisar fichas y clasificacion de derechos.
4. Ejecutar `python3 scripts/maestro.py compilar`.
5. Ejecutar `python3 scripts/maestro.py pagina`.
6. Ejecutar `python3 scripts/maestro.py auditar-publicacion`.
7. Publicar con `python3 scripts/maestro.py servir --port 8765`.

Si el PDF descargable no existe, el sistema debe generarlo desde contenido propio o autorizado antes de publicar.

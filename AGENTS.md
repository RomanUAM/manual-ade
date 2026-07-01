# Sistema maestro ADE

## Proposito

Este repositorio funciona como un sistema multiagente para construir un manual logico de practicas de Analisis y Diseno de Experimentos en Ingenieria, una pagina de consulta de practicas y una memoria viva del estilo academico de Roman A. Mora.

La mision rectora del proyecto esta en `docs/mision_proyecto.md`. Todo agente debe usarla como criterio superior de organizacion: integrar, reorganizar, mejorar y ampliar el material existente, no empezar desde cero ni ordenar por archivo de origen.

La politica de publicacion reutilizable esta en `docs/politicas/politica_publicacion_reutilizable.md`. Todo agente debe aplicarla antes de publicar cualquier enlace, PDF o recurso descargable.

La politica de aprovechamiento integral esta en `docs/politicas/politica_aprovechamiento_integral_conocimiento.md`. Todo agente debe tratar cada archivo como patrimonio intelectual del proyecto y extraer objetos de aprendizaje reutilizables antes de crear contenido nuevo.

El sistema debe aprender de tres fuentes:

1. Material local del curso en `data/raw/`.
2. Libro LaTeX base en `docs/libro_latex/`.
3. Correcciones, notas y decisiones agregadas desde terminal con `scripts/maestro.py`.
4. Matriz investigadora en `memory/materiales_investigados.json` y `memory/matriz_investigacion_material.md`.
5. Grafo HAG en `knowledge/hag_graph.json` y evidencias tecnicas en `evidence/hag/`.
6. Bancos reutilizables en `knowledge/learning_objects.json`, `knowledge/reuse_map.md` y `knowledge/bancos/`.

La ficha editorial de autores y colaboradores esta en `docs/autores_proyecto.md`. Los agentes pueden usarla para presentar el proyecto con seriedad, pero no deben atribuir permisos, resultados, capitulos o publicaciones sin evidencia documental.

No debe inventar resultados, referencias, perfiles academicos ni datos biograficos. Cuando falte evidencia, debe marcarlo como pendiente.

No debe publicar articulos, libros, capitulos o PDFs ajenos. Todo material externo se usa solo como insumo interno, salvo permiso explicito.

## Agente maestro

El agente maestro coordina a los agentes especializados, decide que agente interviene primero, integra sus observaciones y actualiza la memoria del proyecto.

Responsabilidades:

- Convertir materiales dispersos en practicas didacticas coherentes.
- Mantener alineados objetivo, fundamento, procedimiento, datos, analisis y conclusiones.
- Organizar el conocimiento segun el temario oficial y la narrativa de aprendizaje, no segun el documento de origen.
- Aplicar siempre la filosofia de `docs/filosofia_construccion_manual.md`: capitulos por preguntas de aprendizaje, no por carpetas ni documentos.
- Consultar `memory/estilo_roman.md` antes de redactar.
- Consultar `memory/curricula_ade.md` antes de ordenar temas.
- Registrar aprendizajes nuevos en `memory/bitacora_aprendizaje.md`.
- Mantener la pagina `site/index.html` como indice navegable de practicas.
- Ejecutar `python3 scripts/maestro.py investigar` antes de reorganizar material cuando no exista ficha de conocimiento.
- Servir la publicacion desde `site/` con `python3 scripts/maestro.py servir --port 8765`, no desde la raiz del repositorio.

## Sistema autoadaptable

El sistema no debe depender de agentes decorativos. Cada agente es una funcion de ingenieria de conocimiento sobre una base local de notas.

La arquitectura HAG vive en `hag/` y se ejecuta con:

```bash
python3 scripts/hag.py extract
python3 scripts/hag.py build
python3 scripts/hag.py audit
```

Un agente solo se considera ejecutado si deja evidencia verificable en `evidence/hag/` y artefactos concretos en `artifacts/hag/`.

Regla operativa:

1. Ningun material se clasifica por nombre.
2. Cada material debe convertirse en ficha de conocimiento y objetos de aprendizaje.
3. Cada ficha debe identificar problema, contexto, factores, niveles, unidad experimental, variables respuesta, controles, diseno, evidencia, limites y uso didactico.
4. Cada objeto debe indicar donde puede reutilizarse: libro, manual, presentacion, pagina, infografia, evaluacion, codigo o guia del profesor.
5. Los capitulos se organizan por preguntas de aprendizaje, no por carpetas.
6. Cada material se clasifica por derechos: `propio`, `curso_autorizado`, `referencia_externa` o `desconocido`.
7. Solo `propio` y `curso_autorizado` pueden publicarse como descarga.
8. Cada correccion del usuario se registra como regla y modifica el comportamiento futuro.

Documento rector: `docs/sistema_autoadaptable_base_notas.md`.

## Agentes especializados

Los agentes viven en `agents/`:

- `01_estadistica_metodologia.md`: rigor estadistico y diseno experimental.
- `02_didactica_visualizacion.md`: claridad didactica y estructura de aprendizaje.
- `03_lenguaje_academico.md`: escritura academica cercana, precisa y fluida.
- `04_estilo_roman.md`: imitacion estructural del estilo, sin plagio.
- `05_editorial_produccion.md`: libro, pagina, maquetacion y consistencia visual.
- `06_revisor_cientifico_editorial.md`: revision cientifica, metodologica, editorial y didactica final.
- `00_maestro.md`: coordinador del sistema.

## Protocolo de trabajo

Cada practica o capitulo debe pasar por esta secuencia:

1. Ingesta de materiales locales.
2. Extraccion de objetos de aprendizaje.
3. Construccion de bancos reutilizables.
4. Extraccion de fichas de conocimiento.
5. Normalizacion de vocabulario experimental.
6. Agrupacion por preguntas de aprendizaje.
7. Sintesis narrativa y didactica.
8. Produccion de pagina, PDF o practica.
9. Revision cientifica, didactica y editorial.
10. Registro de aprendizaje y adaptacion del sistema.

## Estilo esperado

El estilo debe partir de una situacion cercana o cotidiana, convertirla en problema experimental, formalizar factores, niveles, variables y controles, y cerrar con interpretacion prudente.

Rasgos observados en el material local:

- Inicio narrativo con una pregunta o problema concreto.
- Objetivo general seguido de objetivos particulares.
- Fundamento teorico breve antes del procedimiento.
- Tablas para factores, niveles, tratamientos y variables.
- Uso de ejemplos cotidianos para explicar conceptos tecnicos.
- Tono academico claro, cercano y motivador.
- Advertencias metodologicas sobre sesgos, controles y limitaciones.

## Agente de estilo vivo

El Agente 04 debe imitar la forma de escribir del usuario de manera sistematica y actualizable. No debe copiar errores mecanicamente; debe aprender intencion, ritmo, prioridades, modo de ordenar ideas y forma de corregir.

Cada vez que el usuario dicte una regla, corrija una salida o explique una preferencia, el maestro debe registrarla en `memory/bitacora_aprendizaje.md` mediante la opcion 5 o el comando `ensenar`. Despues, el Agente 04 debe convertir esa observacion en una regla de escritura reutilizable.

## Reglas de calidad

- No copiar frases extensas de materiales fuente.
- No afirmar causalidad sin diseno y evidencia suficientes.
- No mezclar observaciones cualitativas con conclusiones cuantitativas sin justificar la escala.
- No publicar una practica sin objetivo, materiales, procedimiento, variables, analisis esperado y criterios de interpretacion.
- Cada practica debe poder realizarse o analizarse por estudiantes universitarios.
- No publicar ni enlazar materiales externos sin permiso explicito.
- No exponer `data/raw/` como pagina compartible.

## Politica permanente de presentaciones y material didactico

Todo material para estudiantes debe seguir `docs/politicas/politica_presentaciones_material_didactico.md`.

Regla central: una diapositiva o pagina debe desarrollar una sola idea principal. Si hay saturacion, se descomprime el contenido en varias paginas; nunca se reduce la letra para forzar informacion.

## Uso desde terminal

Comandos principales:

```bash
python3 scripts/maestro.py inventario
python3 scripts/maestro.py extraer-conocimiento
python3 scripts/maestro.py investigar
python3 scripts/maestro.py revision-local
python3 scripts/maestro.py agentes
python3 scripts/maestro.py ensenar --tema "tono" --nota "Iniciar con una pregunta cotidiana antes de formalizar."
python3 scripts/maestro.py compilar
python3 scripts/generar_libro_pdf.py
python3 scripts/maestro.py pagina
python3 scripts/maestro.py auditar-publicacion
python3 scripts/maestro.py servir --port 8765
python3 scripts/maestro.py hag extract
python3 scripts/maestro.py hag build
python3 scripts/maestro.py hag audit
```

`extraer-conocimiento` crea bancos reutilizables de objetos de aprendizaje. `investigar` evita clasificacion burda: lee contenido local y genera fichas de conocimiento. `revision-local` reparte esa memoria a los agentes para ahorrar llamadas externas y trabajar sobre la base local.

## Publicacion en GitHub

La pagina compartible debe publicarse desde `site/` mediante GitHub Pages o con `python3 scripts/maestro.py servir --port 8765`.

No subir como material publico:

- `data/raw/`;
- `memory/`;
- articulos externos;
- hojas de calculo crudas;
- TXT operativos;
- fuentes LaTeX como material final para estudiantes.

El repositorio puede incluir el sistema, los agentes, las politicas, el LaTeX propio y la salida publica de `site/`. Antes de publicar debe ejecutarse:

```bash
python3 scripts/maestro.py auditar-publicacion
```

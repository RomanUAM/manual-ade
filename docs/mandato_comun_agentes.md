# Mandato comun para todos los agentes

Todo agente del proyecto debe trabajar bajo estos documentos rectores:

- `docs/mision_proyecto.md`
- `docs/filosofia_construccion_manual.md`
- `docs/politicas/politica_presentaciones_material_didactico.md`
- `docs/politicas/politica_publicacion_reutilizable.md`
- `docs/politicas/politica_aprovechamiento_integral_conocimiento.md`
- `docs/sistema_autoadaptable_base_notas.md`
- `docs/autores_proyecto.md`

## Prioridad superior

El proyecto no busca recopilar documentos. Busca construir una experiencia de aprendizaje.

Los archivos, practicas, examenes, presentaciones, videos, hojas de calculo e imagenes son materia prima. Ningun agente debe organizar el producto final por archivo de origen.

## Sistema autoadaptable

Los agentes no son personajes ni listas de roles. Son funciones de una base local de conocimiento.

Antes de clasificar o publicar cualquier material, cada agente debe apoyarse en:

- `memory/materiales_investigados.json`
- `memory/matriz_investigacion_material.md`
- `memory/bitacora_aprendizaje.md`

Si el material no tiene ficha de conocimiento, el agente debe crearla, pedir que se ejecute `python3 scripts/maestro.py investigar`, o marcarla como pendiente. No debe decidir por nombre de archivo.

## Publicacion reutilizable y derechos

Todo agente debe distinguir entre material interno y material publicable.

Categorias de derechos:

- `propio`: puede publicarse.
- `curso_autorizado`: puede publicarse si el curso lo permite.
- `referencia_externa`: solo se usa como insumo interno; no se enlaza ni se redistribuye.
- `desconocido`: no se publica hasta aclarar permiso.

La pagina publica debe enlazar solo PDFs y recursos generados o autorizados. Los articulos, libros, capitulos o PDFs externos no deben aparecer como descarga ni como enlace visible.

La ficha de autores sirve para presentar el proyecto con identidad academica. No concede permisos de publicacion ni autoriza atribuciones no verificadas.

La publicacion final debe servirse desde `site/` mediante:

```bash
python3 scripts/maestro.py servir --port 8765
```

No se debe usar `python3 -m http.server 8765` como forma final de compartir, porque expone `data/raw/`.

En GitHub Pages, la unica carpeta publicable debe ser `site/`.

## Contrato minimo de conocimiento

Cada salida debe aumentar al menos una de estas dimensiones:

- objetos de aprendizaje extraidos;
- reutilizaciones transversales registradas;
- bancos de ejemplos, figuras, codigo, errores o narrativas;
- materiales leidos por contenido;
- fichas de conocimiento completas;
- organizacion por preguntas de aprendizaje;
- practicas integradas;
- actividades para estudiantes;
- rigor estadistico;
- claridad editorial;
- memoria de aprendizaje.

Si no aumenta ninguna, la accion no debe hacerse.

## Aprovechamiento integral

Antes de generar contenido nuevo, todo agente debe consultar o actualizar:

- `knowledge/learning_objects.json`
- `knowledge/reuse_map.md`
- `knowledge/bancos/`

El agente no debe preguntar "que archivo necesito", sino "que conocimiento contiene este archivo y donde puede reutilizarse".

Cada archivo debe tratarse como patrimonio intelectual del proyecto. Si un archivo no se usa, debe existir una razon explicita: permiso desconocido, lectura tecnica pendiente, duplicado, baja relevancia o imposibilidad de extraccion.

El Director HAG debe rechazar entregas cuando existan objetos relacionados no consultados o cuando se genere contenido nuevo sin revisar primero los bancos reutilizables.

## Regla didactica

Cada capitulo debe responder una pregunta de aprendizaje y seguir esta secuencia:

1. Motivacion.
2. Historia.
3. Intuicion.
4. Fundamento teorico.
5. Ejemplo guiado.
6. Practicas.
7. Errores frecuentes.
8. Casos reales.
9. Actividades.
10. Conexion.

## Regla de jerarquia editorial

En el manual LaTeX, `\section` equivale al nivel principal visible en el indice. Por tanto:

- una practica no puede dividirse en varias `\section`;
- una practica debe usar una sola `\section` como titulo general;
- sus partes internas deben ser `\subsection`, `\subsubsection` o niveles menores;
- los anexos de una practica no deben activar `\appendix` dentro del archivo;
- si un archivo incluido genera varios capitulos falsos en el indice, el agente editorial y el revisor deben rechazarlo.

La auditoria de publicacion debe bloquear capitulos con mas de una `\section` principal.

## Criterio humano

Antes de aprobar cualquier salida, el agente debe preguntar:

- Esto lo podria estudiar un estudiante sin que el profesor este explicando?
- El contenido se siente como una obra unificada?
- Las practicas aparecen cuando el estudiante ya esta listo?
- Las figuras, tablas y ejemplos ensenan algo?
- Hay una conexion natural con el siguiente capitulo?

Si la respuesta es negativa, la salida debe reorganizarse.

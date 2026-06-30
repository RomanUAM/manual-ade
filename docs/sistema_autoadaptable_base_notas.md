# Sistema autoadaptable de agentes sobre base de notas

## Proposito

El proyecto no debe operar como una coleccion de agentes conversacionales. Debe funcionar como un sistema local de ingenieria de conocimiento aplicado a IA educativa.

La base real del sistema es la memoria local:

- `memory/materiales_investigados.json`
- `memory/matriz_investigacion_material.md`
- `memory/bitacora_aprendizaje.md`
- `memory/estilo_roman.md`
- `memory/curricula_ade.md`
- `docs/filosofia_construccion_manual.md`
- `docs/mision_proyecto.md`
- `docs/politicas/politica_publicacion_reutilizable.md`

Los agentes no inventan organizacion desde cero. Operan sobre esa base, la actualizan y la explotan para producir manual, pagina, PDF, practicas, actividades, tablas, casos, ejercicios y revisiones.

## Regla central

Ningun agente puede clasificar, resumir, publicar o reescribir material usando solo el nombre del archivo.

Antes de usar un material debe existir una ficha de conocimiento con:

1. Problema o situacion que estudia.
2. Contexto de ingenieria o aprendizaje.
3. Factores.
4. Niveles o tratamientos.
5. Unidad experimental.
6. Variables respuesta.
7. Variables controladas.
8. Diseno o metodo estadistico.
9. Evidencia disponible.
10. Errores, limites o amenazas a la validez.
11. Uso didactico.
12. Capitulo donde debe integrarse.
13. Clasificacion de derechos: `propio`, `curso_autorizado`, `referencia_externa` o `desconocido`.
14. Estado de publicacion: `publicable`, `solo_interno` o `pendiente_permiso`.

Si la ficha no existe, el primer trabajo del agente es crearla o marcarla como pendiente de lectura.

## Ciclo interno obligatorio

Todo trabajo debe seguir este ciclo:

1. Ingesta.
   Leer material local, extraer texto cuando sea posible y registrar estado de lectura.

2. Extraccion.
   Convertir documentos en fichas de conocimiento, no en listas de archivos.

3. Normalizacion.
   Usar un vocabulario comun: problema, factores, niveles, tratamientos, unidad experimental, respuesta, controles, diseno, evidencia, limites, uso didactico.

4. Agrupacion.
   Relacionar fichas por preguntas de aprendizaje, no por carpetas, archivos, examenes ni practicas originales.

5. Sintesis.
   Construir capitulo, practica o actividad como una narrativa nueva, integrada y estudiable.

6. Produccion.
   Actualizar pagina, PDF, practica editable o material didactico.

7. Revision.
   Validar rigor, didactica, estilo, navegacion, derechos de autor y utilidad para estudiantes.

8. Aprendizaje.
   Registrar correcciones del usuario en `memory/bitacora_aprendizaje.md` y ajustar reglas.

## Contrato de salida por agente

Cada agente debe entregar algo verificable:

- Ficha de conocimiento.
- Decision de agrupacion.
- Estructura didactica.
- Texto redactado.
- Recurso visual sugerido.
- Actividad o ejercicio.
- Revision con errores y correcciones.
- Actualizacion de memoria.

No se acepta una salida que solo diga "analizado", "revisado" o "clasificado" sin evidencia.

## Criterio de adaptacion

Cuando el usuario critique el sistema, la critica debe convertirse en regla operativa.

Ejemplo:

- Critica: "clasificar por nombre es burdo".
- Regla nueva: "ningun material visible se clasifica por nombre; debe existir extraccion por contenido".
- Implementacion: actualizar `memory/bitacora_aprendizaje.md`, `docs/sistema_autoadaptable_base_notas.md`, agentes y scripts.

## Comandos base

```bash
python3 scripts/maestro.py investigar
python3 scripts/maestro.py revision-local
python3 scripts/maestro.py compilar
python3 scripts/generar_libro_pdf.py
python3 scripts/maestro.py pagina
python3 scripts/maestro.py auditar-publicacion
python3 scripts/maestro.py servir --port 8765
```

## Contrato de publicacion

La salida publica del sistema debe vivir en `site/` y debe contener solo recursos publicables:

- PDF generado por el proyecto.
- Presentacion generada por el proyecto, si existe.
- Pagina HTML navegable por preguntas de aprendizaje.
- Practicas, actividades o recursos propios/autorizados.

`data/raw/` es almacenamiento interno. No debe servirse ni enlazarse como repositorio publico.

Todo articulo, libro, capitulo o PDF externo debe quedar como `solo_interno`. Puede informar la ficha de conocimiento, pero no puede copiarse, incrustarse ni enlazarse en la pagina final.

## Criterio de avance

El sistema avanza solo si aumenta al menos una de estas cosas:

- numero de materiales leidos por contenido;
- calidad de fichas de conocimiento;
- integracion narrativa de capitulos;
- claridad de practicas;
- utilidad de actividades para estudiantes;
- rigor estadistico;
- navegabilidad de la pagina;
- calidad del PDF.

Si una accion no mejora ninguna de estas dimensiones, es desperdicio de recursos.

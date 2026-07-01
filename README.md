# Manual ADE

Sistema multiagente local para construir un manual universitario de **Analisis y Diseno de Experimentos en Ingenieria** a partir de presentaciones, notas, practicas, datos y documentos del curso.

El objetivo no es guardar archivos: es transformar material disperso en una experiencia de aprendizaje navegable, descargable y reutilizable.

## Salidas publicas

- Pagina compartible en `site/index.html`.
- Manual PDF descargable en `site/manual_base_latex_compilado.pdf`.
- Presentacion PDF en `site/presentacion_integrada_ade.pdf`, si existe.
- Propuesta de enriquecimiento en `site/manual_integrado_ade.pdf`, si existe.

La pagina publica no debe enlazar `data/raw/`, articulos externos, hojas de calculo crudas, TXT ni archivos LaTeX fuente.

## Autores y colaboradores

La ficha editorial esta en `docs/autores_proyecto.md`.

El sistema no atribuye permisos ni resultados por el solo hecho de listar autores. Cada material se clasifica antes de publicarse.

## Flujo recomendado

```bash
cd "/Users/romananselmomoragutierrez/Documents/Libro de ADE"

python3 scripts/hag.py build
python3 scripts/maestro.py investigar
python3 scripts/maestro.py compilar
python3 scripts/maestro.py pagina
python3 scripts/maestro.py auditar-publicacion
python3 scripts/maestro.py servir --port 8765
```

Despues abrir:

```text
http://localhost:8765/
```

## Publicacion en GitHub Pages

Este repositorio incluye `.github/workflows/pages.yml`. Cuando el proyecto se suba a GitHub y se habilite Pages con GitHub Actions, se publicara unicamente la carpeta `site/`.

No usar `python3 -m http.server` desde la raiz como forma de publicacion, porque expone carpetas internas.

## Estructura

- `hag/`: motor Python del sistema HAG.
- `knowledge/`: grafo de conocimiento.
- `evidence/`: reportes verificables de agentes y auditoria.
- `artifacts/`: artefactos tecnicos generados por agentes.
- `agents/`: agentes especializados.
- `docs/`: mision, politicas, LaTeX base y ficha editorial.
- `practicas/`: practicas editables generadas por el sistema.
- `scripts/`: maestro, investigacion local, auditoria y servidor seguro.
- `site/`: salida publica para estudiantes.
- `data/raw/`: materia prima local, ignorada por Git por seguridad.
- `memory/`: memoria operativa local, regenerable.

## Principio didactico

Cada capitulo debe responder una pregunta de aprendizaje y conectar con el siguiente. El estudiante no debe ver un inventario de archivos, sino un manual coherente con motivacion, intuicion, fundamento, practica, errores frecuentes, casos reales, actividades y cierre.

## HAG

La arquitectura tecnica esta documentada en `docs/arquitectura_hag.md`.

Comandos principales:

```bash
python3 -m pip install -e .
python3 scripts/hag.py init
python3 scripts/hag.py build
python3 scripts/hag.py audit
python3 scripts/hag_api.py --port 8787
python3 -m unittest discover -s tests -p 'test_*.py'
```

Si `hag audit` falla, la entrega no debe considerarse terminada: el reporte indica que recursos del ecosistema siguen desconectados o incompletos.

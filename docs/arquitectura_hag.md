# Arquitectura HAG

## Proposito

HAG convierte el proyecto ADE en un ecosistema educativo gobernado por una base de conocimiento. El libro, la pagina, las practicas, presentaciones, evaluaciones y simuladores deben ser vistas de un mismo grafo.

El sistema no acepta una entrega solo porque exista un PDF. Debe auditar si cada nodo de conocimiento cuenta con los recursos necesarios para que un profesor pueda impartir la asignatura y un estudiante pueda estudiarla de forma autonoma.

## Componentes Python

- `hag.models`: modelos de nodos, relaciones, artefactos y evidencias.
- `hag.knowledge_base`: persistencia del grafo en `knowledge/hag_graph.json`.
- `hag.agents`: agentes ejecutables que generan artefactos y reportes JSON.
- `hag.generators`: registro de artefactos existentes y reporte de brechas.
- `hag.audit`: auditor tecnico, editorial y de integracion.
- `hag.director`: orquestador del sistema.
- `hag.cli`: interfaz de terminal.
- `hag.api`: API REST local sin dependencias externas.

## Comandos

```bash
python3 -m pip install -e .
python3 scripts/hag.py init
python3 scripts/hag.py build
python3 scripts/hag.py audit
python3 scripts/hag.py status
python3 scripts/hag_api.py --port 8787
python3 -m unittest discover -s tests -p 'test_*.py'
```

`build` ejecuta agentes, registra artefactos, audita y escribe evidencia en `evidence/hag/`.

Si el ecosistema esta incompleto, `build` y `audit` terminan con codigo 2. Ese comportamiento es intencional: evita entregar como terminado un sistema desconectado.

## API local

- `GET /health`: estado del servicio.
- `GET /nodes`: nodos del grafo.
- `GET /audit`: resultado de auditoria.

## Criterio de fallo

El sistema falla si:

- no hay evidencia JSON de agentes;
- un agente no produce artefactos;
- un capitulo tiene varias `\section` principales;
- un archivo incluido activa `\appendix` internamente;
- un nodo de conocimiento carece de libro, practica, presentacion, PDF, web, infografia, codigo, ejercicio, solucion o evaluacion.

La falla no es un error del software: es una senal de que el ecosistema todavia esta incompleto.

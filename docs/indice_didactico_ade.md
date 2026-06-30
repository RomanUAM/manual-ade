# Indice didactico del manual ADE

## Criterio de organizacion

Este indice evita repetir temas y organiza el material disponible en una secuencia universitaria: primero se aprende a observar y medir, despues a comparar grupos, luego a estudiar factores e interacciones, y finalmente a modelar respuestas complejas.

Cada modulo debe producir al menos una practica editable en `practicas/`, una referencia dentro del libro LaTeX y una entrada visible en la pagina `site/index.html`.

## Ruta secuencial

### Modulo 1. Pensar experimentalmente

**Proposito:** convertir una observacion cotidiana en una pregunta experimental.

**Contenidos:**

- Que es un experimento.
- Diferencia entre observar, medir, comparar y explicar.
- Unidad experimental.
- Variable respuesta.
- Variables controladas.
- Error experimental.

**Material disponible:**

- `data/raw/curso-2025/Analisis-de-Experimentos.pdf`
- `data/raw/curso-2026p/Analisis-de-Experimentos.pdf`
- `data/raw/curso-2026p/Diseno-de-experimentos-en-ingenieria.pdf`
- `docs/libro_latex/Capitulos/00-preliminares.tex`

**Practica sugerida:** Del problema cotidiano a la pregunta experimental.

**Agentes principales:** didactica, lenguaje, estilo Roman.

### Modulo 2. Datos, muestreo y variabilidad

**Proposito:** entender que la variabilidad no es ruido inutil, sino informacion para decidir.

**Contenidos:**

- Muestreo.
- Media y varianza.
- Frecuencias empiricas.
- Tamanos de muestra.
- Datos faltantes y atipicos.

**Material disponible:**

- `docs/libro_latex/Capitulos/04-anova.tex`
- `data/raw/curso-2026p/Una-exploracion-del-Indice-de-Gini-mundial-a-traves-de-cinco-metodos-de-muestreo (1).pdf`
- `docs/libro_latex/Capitulos/00-preliminares.tex`

**Practica sugerida:** Muestreo y grandes numeros en un fenomeno observable.

**Agentes principales:** estadistica, didactica.

### Modulo 3. Comparacion de grupos: ANOVA de un factor

**Proposito:** comparar tres o mas grupos sin depender solo de diferencias visuales entre medias.

**Contenidos:**

- Hipotesis nula y alternativa.
- Variabilidad entre grupos y dentro de grupos.
- Estadistico F.
- Valor p.
- Supuestos basicos.

**Material disponible:**

- `data/raw/curso-2025/ANOVA-de-un-factor-Prueba-F-y-valor-P.pdf`
- `data/raw/curso-2026p/ANOVA-de-un-factor-Prueba-F-y-valor-P.pdf`
- `data/raw/curso-2026p/ANOVA.xlsx`
- `docs/libro_latex/Capitulos/00-ANOVA.tex`
- `practicas/anova-de-un-factor-comparar-grupos-con-evidencia.md`

**Practica sugerida:** Comparar tratamientos con una sola variable respuesta.

**Agentes principales:** estadistica, lenguaje.

### Modulo 4. ANOVA de dos factores

**Proposito:** separar efectos principales de interacciones.

**Contenidos:**

- Factor A y factor B.
- Efectos principales.
- Interaccion.
- Tabla ANOVA de dos factores.
- Interpretacion grafica.

**Material disponible:**

- `data/raw/curso-2025/ANOVA-de-2-Factores.pdf`
- `data/raw/curso-2026p/ANOVA-de-2-Factores.pdf`
- `data/raw/curso-2025/ANOVA-Factorial-2-y-2-Analisis-de-efectos-principales-interacciones-y-replicas-desiguales.pdf`
- `data/raw/curso-2026p/ANOVA-Factorial-2-y-2-Analisis-de-efectos-principales-interacciones-y-replicas-desiguales.pdf`

**Practica sugerida:** Dos factores, una respuesta y una decision experimental.

**Agentes principales:** estadistica, didactica.

### Modulo 5. Diseno factorial 2x2

**Proposito:** construir tratamientos a partir de combinaciones de niveles.

**Contenidos:**

- Diseno 2^2.
- Codificacion bajo/alto.
- Tratamientos.
- Repeticiones.
- Blanco experimental.
- Control de variables.

**Material disponible:**

- `docs/libro_latex/Capitulos/02-conceptos.tex`
- `data/raw/curso-2026p/Sustancias-interacciones-y-cambios-visuales-en-papel-introduccion-al-diseno-factorial-2.pdf`
- `data/raw/curso-2026p/Examen 1/Practica 2^2 A&D.pdf`
- `data/raw/curso-2026p/Examen 1/Factorial 2^2 Corregido.xlsx`
- `data/raw/curso-2026p/Plantilla_Diseno_Factorial_2x2_6Rep (1).xlsx`
- `practicas/diseno-factorial-2x2-sustancias-e-interacciones-visuales.md`

**Practica sugerida:** Sustancias, interacciones y cambios visuales en papel.

**Agentes principales:** estadistica, didactica, estilo Roman.

### Modulo 6. Disenos factoriales aplicados y no balanceados

**Proposito:** llevar el diseno factorial a procesos manuales, productos y materiales.

**Contenidos:**

- Factoriales aplicados.
- Replicas desiguales.
- Procesos manuales.
- Lectura critica de resultados.
- Limitaciones de control experimental.

**Material disponible:**

- `data/raw/curso-2026p/Optimizacion-de-un-Proceso-Manual-mediante-un-Diseno-Factorial-2-No-Balanceado.pdf`
- `data/raw/curso-2026p/Emprendimiento-nuevos-productos-y-diseno-factorial-desarrollo-de-separadores-artesanales-utilizando- (1).pdf`
- `data/raw/curso-2026p/Examen 1/reporte separadores artesanales.pdf`
- `data/raw/curso-2026p/Analisis_Excel_Material_Compuesto.xlsx`

**Practica sugerida:** Optimizacion de un proceso manual con replicas no balanceadas.

**Agentes principales:** estadistica, editorial.

### Modulo 7. Diseno Taguchi

**Proposito:** reducir el numero de tratamientos sin perder la logica experimental.

**Contenidos:**

- Matriz L4(2^3).
- Factores de control.
- Respuestas visuales y ordinales.
- Robustez.
- Interpretacion exploratoria.

**Material disponible:**

- `docs/libro_latex/Capitulos/03-disenos-clasicos.tex`
- `data/raw/curso-2025/De-Datos-Continuos-a-Diseno-Taguchi-Analisis-Experimental-con-Python.pdf`
- `data/raw/curso-2026p/De-Datos-Continuos-a-Diseno-Taguchi-Analisis-Experimental-con-Python.pdf`
- `data/raw/curso-2026p/Practica 1/Video 1_taguchi.pdf`
- `practicas/taguchi-l4-violeta-africana-y-sistemas-biologicos-confinados.md`

**Practica sugerida:** Violeta africana en sistemas biologicos confinados.

**Agentes principales:** estadistica, didactica, estilo Roman.

### Modulo 8. Regresion y modelado

**Proposito:** pasar de comparar tratamientos a explicar una respuesta continua.

**Contenidos:**

- Modelo lineal.
- Variable predictora.
- Variable respuesta.
- Ajuste e interpretacion.
- Diagnosticos basicos.

**Material disponible:**

- `data/raw/curso-2026p/Modelado-Parte-II.pdf`
- `data/raw/curso-2026p/Modelado-de-Problemas (1).pdf`
- `data/raw/curso-2026p/Modelos de regresion bitstream_17fe69cd-b08f-4263-8b85-1ab7a9f0a1d2.pdf-PDFA.pdf`

**Practica sugerida:** Modelar una respuesta continua en un proceso experimental.

**Agentes principales:** estadistica, lenguaje.

### Modulo 9. ANCOVA

**Proposito:** comparar tratamientos considerando variables explicativas adicionales.

**Contenidos:**

- Covariable.
- Ajuste de medias.
- Interpretacion del efecto del tratamiento.
- Riesgo de confundir grupos con covariables.

**Material disponible:**

- `data/raw/curso-2026p/Analisis-de-Covarianza-ANCOVA-con-3-Variables-Explicativas-y-1-Variable-Respuesta.pdf`

**Practica sugerida:** Comparar grupos ajustando una respuesta por covariables.

**Agentes principales:** estadistica.

### Modulo 10. MANOVA y respuestas multiples

**Proposito:** analizar experimentos donde una sola respuesta no basta para describir el desempeno.

**Contenidos:**

- Multiples variables respuesta.
- Diferencia entre ANOVA y MANOVA.
- Interpretacion multivariada.
- Riesgo de conclusiones fragmentadas.

**Material disponible:**

- `data/raw/curso-2025/Ejemplo-Practico-de-MANOVA.pdf`
- `data/raw/curso-2025/global/Análisis Multivariado del Rendimiento Térmico en Procesadores de Alto Desempeño..pptx`
- `data/raw/curso-2025/global/Análisis_MANOVA_Ilse_Arevalo.xlsx`
- `data/raw/curso-2025/global/Análisis_MANOVA_Ilse_Arévalo.pdf`
- `data/raw/curso-2025/global/Articulo Manova.pdf`
- `data/raw/curso-2026p/E2/MANOVA/MANOVA.mp4`
- `data/raw/curso-2026p/Ejemplo-Practico-de-MANOVA.pdf`
- `practicas/manova-multiples-respuestas-en-rendimiento-termico.md`

**Practica sugerida:** Multiples respuestas en rendimiento termico.

**Agentes principales:** estadistica, editorial.

### Modulo 11. Proyecto integrador

**Proposito:** cerrar el curso con una practica completa: problema, diseno, datos, analisis, conclusion y limitaciones.

**Contenidos:**

- Planteamiento del problema.
- Diseno experimental.
- Ejecucion o analisis documental.
- Tabla de datos.
- Analisis estadistico.
- Discusion y limites.

**Material disponible:**

- `data/raw/curso-2025/Proyecto/DatosAcustica.xlsx`
- `data/raw/curso-2025/Proyecto/Análisis de Inductancia - Proyecto Final.docx`
- `data/raw/curso-2025/Proyecto/Análisis de Inductancia - Proyecto Final.pdf`
- `data/raw/curso-2025/Proyecto/PROYECTO FINAL DAEI.pdf`
- `data/raw/curso-2025/Proyecto/Propuesta de diseño experimental para compósitos acústicos.pdf`

**Practica sugerida:** Proyecto final de diseno experimental aplicado.

**Agentes principales:** maestro, estadistica, editorial.

## Reglas para no repetir temas

1. ANOVA de un factor se usa solo para comparacion de grupos con un factor.
2. ANOVA de dos factores se reserva para efectos principales e interaccion.
3. Diseno factorial 2x2 se trata como construccion experimental, no como repeticion de ANOVA.
4. Taguchi se presenta como reduccion y robustez, no como factorial completo.
5. Regresion se usa para modelar respuesta continua, no para comparar grupos.
6. ANCOVA se usa cuando una covariable modifica la interpretacion.
7. MANOVA se usa cuando hay multiples respuestas simultaneas.
8. Los proyectos aplicados se colocan al final como integracion, aunque usen herramientas previas.

## Producto minimo por modulo

- Una practica editable en Markdown.
- Una tabla de factores, niveles o variables.
- Una indicacion de analisis estadistico.
- Una seccion de limitaciones.
- Una fuente local principal.
- Un agente responsable de revision.


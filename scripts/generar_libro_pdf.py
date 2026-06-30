#!/usr/bin/env python3
from __future__ import annotations

import textwrap
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "pdf" / "borrador_integracion_ade.pdf"
SITE_OUT = ROOT / "site" / "borrador_integracion_ade.pdf"


CHAPTERS = [
    (
        "Por que necesitamos disenar experimentos?",
        "Experimentar no es probar cosas al azar. Es construir evidencia para decidir cuando hay ruido, variabilidad y riesgo de atribuir causas falsas.",
        "Una empresa cambia una formula y observa una mejora. Pero tambien cambio el operador, la temperatura y el lote de material. El estudiante aprende que sin diseno no hay una historia causal defendible.",
        "Diagnosticar un experimento mal planteado y reconstruirlo con pregunta, unidad experimental, variable respuesta y controles.",
    ),
    (
        "Como convertir datos dispersos en informacion confiable?",
        "Los datos no hablan solos: deben ordenarse para distinguir patron, variabilidad y error.",
        "Dos equipos cuentan el mismo fenomeno en momentos distintos y obtienen respuestas diferentes. La media resume, pero la varianza advierte cuanto puede enganarnos una muestra pequena.",
        "Construir frecuencias, media y varianza a partir de observaciones reales; discutir atipicos sin borrarlos por comodidad.",
    ),
    (
        "Como saber si varios tratamientos producen respuestas distintas?",
        "ANOVA compara la variabilidad entre tratamientos contra la variabilidad natural dentro de ellos.",
        "No basta mirar promedios. Si los datos dentro de cada grupo se mueven mucho, una diferencia visual puede no sostenerse.",
        "Resolver un ANOVA de un factor: hipotesis, sumas de cuadrados, F, valor p, decision y limites. Las hojas de calculo se usan para construir tablas y graficas internas, no como lectura principal.",
    ),
    (
        "Que ocurre cuando dos factores actuan al mismo tiempo?",
        "Los efectos principales no siempre explican todo: a veces un factor cambia segun el nivel del otro.",
        "Una interaccion es una historia cruzada. El efecto de una sustancia, temperatura o metodo puede depender de otra condicion.",
        "Leer una matriz de dos factores, graficar perfiles e interpretar interacciones antes de calcular.",
    ),
    (
        "Como se construye un experimento factorial 2x2?",
        "Un diseno 2x2 convierte dos factores y dos niveles en cuatro tratamientos que permiten estudiar efectos e interaccion.",
        "Cuatro combinaciones bien planeadas ensenan mas que muchas pruebas improvisadas. Por eso se contrastan tres historias: hongos en tortillas como observacion biologica, lentejas como sistema controlable y curcuma-cloro en papel como diseno 2^2 completo.",
        "Construir la matriz factorial, definir blanco, replicas, controles y variable respuesta. El caso central usa curcuma 1/4 g y cloro 5/10 g sobre post-it, seis replicas por tratamiento, blanco experimental y medicion con luxometro.",
    ),
    (
        "Como adaptar el diseno experimental a procesos reales?",
        "La realidad no siempre permite condiciones perfectas; el rigor consiste en documentar restricciones y decidir con prudencia.",
        "En procesos manuales aparecen replicas desiguales, ruido operativo y limitaciones materiales.",
        "Analizar un proceso no balanceado, declarar amenazas a la validez y separar resultado de interpretacion.",
    ),
    (
        "Como explorar varios factores sin hacer todos los experimentos?",
        "Taguchi permite explorar combinaciones reducidas cuando el tiempo, el costo o el material limitan el experimento.",
        "Una matriz L4 no es magia: es una forma ordenada de aprender con menos corridas y conclusiones prudentes. Tambien se integra el material donde datos continuos se discretizan por cuantiles para reconstruir niveles experimentales.",
        "Asignar factores a una matriz L4, observar respuestas ordinales y discutir que se puede concluir.",
    ),
    (
        "Como modelar una respuesta continua?",
        "La regresion permite estimar como cambia una respuesta al modificar una condicion.",
        "Una linea ajustada no es verdad absoluta. Es una simplificacion que debe interpretarse, diagnosticarse y limitarse.",
        "Ajustar un modelo lineal, interpretar pendiente, revisar residuos y evitar extrapolaciones.",
    ),
    (
        "Como comparar tratamientos cuando hay covariables?",
        "ANCOVA compara tratamientos ajustando variables que tambien influyen en la respuesta.",
        "Ajustar significa preguntar que diferencia queda cuando los grupos se comparan en condiciones semejantes.",
        "Identificar covariable, interpretar medias ajustadas y evitar ajustar por variables incorrectas.",
    ),
    (
        "Como decidir cuando existen varias respuestas importantes?",
        "MANOVA evita fragmentar decisiones cuando varias respuestas describen simultaneamente el desempeno.",
        "Un proceso puede mejorar en una respuesta y empeorar en otra. La decision debe mirar el perfil completo.",
        "Construir una matriz de respuestas, comparar grupos e interpretar resultados multivariados con cautela.",
    ),
    (
        "Como construir un proyecto experimental completo?",
        "Un proyecto une pregunta, diseno, datos, analisis, conclusion y limites en una cadena defendible.",
        "La calidad no esta solo en calcular bien, sino en que cada parte responda a la anterior.",
        "Armar el mapa de un proyecto final: problema, factores, datos, analisis, discusion, anexos y defensa.",
    ),
]


CASES = {
    "Como saber si varios tratamientos producen respuestas distintas?": "Material retomado: ANOVA de un factor, tablas de calculo y ejercicios del curso. En el libro se transforman en una secuencia: primero mirar dispersion, despues comparar tratamientos y finalmente justificar una decision.",
    "Como se construye un experimento factorial 2x2?": "Material retomado: practica 2^2 de sustancias, curcuma, cloro, post-it, blanco experimental, seis repeticiones y medicion de luz. La practica de hongos en tortillas y el contraste con lentejas se usan para mostrar que una observacion interesante necesita niveles, replicas y respuesta definida para convertirse en diseno factorial.",
    "Como explorar varios factores sin hacer todos los experimentos?": "Material retomado: Taguchi, violeta africana y conversion de datos continuos a niveles por cuantiles. El estudiante aprende que reducir corridas exige declarar limites, no vender certeza falsa.",
    "Como construir un proyecto experimental completo?": "Material retomado: proyecto acustico, compositos e inductancia. El capitulo no presenta archivos sueltos: los convierte en modelos de pregunta, diseno, analisis, defensa y comunicacion.",
}


def esc(text: str) -> bytes:
    text = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return text.encode("latin-1", "replace")


class PDF:
    def __init__(self) -> None:
        self.objects: list[bytes] = []
        self.pages: list[int] = []
        self.font_obj = self.add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
        self.bold_obj = self.add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")

    def add(self, data: bytes) -> int:
        self.objects.append(data)
        return len(self.objects)

    def text_line(self, x: int, y: int, text: str, size: int = 11, bold: bool = False) -> bytes:
        font = "F2" if bold else "F1"
        return b"0 0 0 rg BT /%s %d Tf %d %d Td (%s) Tj ET\n" % (font.encode(), size, x, y, esc(text))

    def add_page(self, title: str, blocks: list[tuple[str, str]]) -> None:
        ops = []
        ops.append(b"0.94 0.97 0.96 rg 0 742 612 50 re f\n")
        ops.append(self.text_line(54, 758, "Borrador de integracion del material ADE", 11, True))
        y = 706
        ops.append(self.text_line(54, y, title, 20, True))
        y -= 30
        for heading, body in blocks:
            if y < 95:
                break
            ops.append(self.text_line(54, y, heading, 12, True))
            y -= 16
            for para in body.split("\n"):
                for line in textwrap.wrap(para, width=88):
                    if y < 72:
                        break
                    ops.append(self.text_line(62, y, line, 10, False))
                    y -= 13
                y -= 5
            y -= 4
        ops.append(b"0.25 0.45 0.42 RG 54 54 504 1 re f\n")
        ops.append(self.text_line(54, 36, "Documento interno de integracion; el manual base sigue siendo la lectura principal", 8, False))
        stream = b"".join(ops)
        content = self.add(b"<< /Length %d >>\nstream\n%s\nendstream" % (len(stream), stream))
        page = self.add(
            b"<< /Type /Page /Parent PAGES 0 R /MediaBox [0 0 612 792] "
            b"/Resources << /Font << /F1 %d 0 R /F2 %d 0 R >> >> /Contents %d 0 R >>"
            % (self.font_obj, self.bold_obj, content)
        )
        self.pages.append(page)

    def write(self, path: Path) -> None:
        kids = b" ".join(b"%d 0 R" % p for p in self.pages)
        pages_obj = self.add(b"<< /Type /Pages /Kids [ " + kids + b" ] /Count %d >>" % len(self.pages))
        catalog_obj = self.add(b"<< /Type /Catalog /Pages %d 0 R >>" % pages_obj)
        fixed = []
        for data in self.objects:
            fixed.append(data.replace(b"PAGES 0 R", b"%d 0 R" % pages_obj))
        self.objects = fixed
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".pdf.tmp")
        with tmp.open("wb") as f:
            f.write(b"%PDF-1.4\n")
            offsets = [0]
            for i, obj in enumerate(self.objects, 1):
                offsets.append(f.tell())
                f.write(b"%d 0 obj\n" % i)
                f.write(obj)
                f.write(b"\nendobj\n")
            xref = f.tell()
            f.write(b"xref\n0 %d\n" % (len(self.objects) + 1))
            f.write(b"0000000000 65535 f \n")
            for off in offsets[1:]:
                f.write(b"%010d 00000 n \n" % off)
            f.write(b"trailer\n<< /Size %d /Root %d 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(self.objects) + 1, catalog_obj, xref))
        tmp.replace(path)


def main() -> None:
    pdf = PDF()
    pdf.add_page(
        "Borrador de integracion del material",
        [
            ("Proposito", "Este documento no sustituye al manual base. Sirve para integrar materiales, detectar practicas y proponer una ruta de mejora del libro."),
            ("Como leerlo", "Cada apartado resume una pregunta de aprendizaje y senala que material local puede alimentar una version futura del manual."),
            ("Estado", "Borrador interno. Debe crecer con redaccion completa, figuras, fotografias, tablas, ejercicios resueltos y practicas completas antes de considerarse manual final."),
        ],
    )
    pdf.add_page(
        "Indice narrativo",
        [(f"{i:02d}. {title}", promise) for i, (title, promise, _, _) in enumerate(CHAPTERS, 1)],
    )
    for title, promise, story, practice in CHAPTERS:
        pdf.add_page(
            title,
            [
                ("Motivacion", promise),
                ("Historia e intuicion", story),
                ("Caso integrado del material local", CASES.get(title, "Este capitulo se alimenta con documentos locales del curso, pero los reorganiza alrededor de una pregunta de aprendizaje para que no se lea como carpeta de archivos.")),
                ("Ejemplo guiado", "El capitulo se desarrolla desde una situacion concreta hacia conceptos, decisiones y calculos. Ninguna formula aparece sin responder una pregunta previa."),
                ("Practica y actividad", practice),
                ("Errores frecuentes", "El capitulo debe mostrar errores reales: conclusiones exageradas, variables mal definidas, replicas confundidas con mediciones y resultados sin contexto."),
                ("Conexion", "El cierre prepara al estudiante para el siguiente capitulo, evitando que el tema quede aislado."),
            ],
        )
    pdf.write(OUT)
    SITE_OUT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OUT, SITE_OUT)
    print(f"PDF generado: {OUT.relative_to(ROOT)}")
    print(f"Copia para la pagina: {SITE_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

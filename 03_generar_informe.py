# -*- coding: utf-8 -*-
"""
Genera el informe del Laboratorio 4 en PDF.

El informe está dirigido a personas del área ambiental sin conocimientos de
programación, por lo que no incluye código: solo resultados, figuras y su
explicación. El documento se arma en Times New Roman 12, texto negro, sin
líneas ni encabezados decorativos.

Uso:
    python 03_generar_informe.py
"""

import os

import pandas as pd
from fpdf import FPDF
from PIL import Image

TABLAS_DIR = "data/tablas"
FIGURAS_DIR = "figures"
SALIDA = "Informe_Laboratorio4_Cianobacteria.pdf"

RUTA_FUENTE = r"C:\Windows\Fonts\times.ttf"
FAMILIA = "TimesNewRoman"

INTEGRANTES = [
    "Rodrigo Ajmac, 22279",
    "Andrés Mazariegos, 21749",
    "June Herrera, 231038",
]
LOGO = "images.png"
FECHA_ENTREGA = "Guatemala, 16 de agosto de 2026"

# Resultados del mapa de persistencia (sección 8.2 del notebook 02_ANALISIS_LAB4.ipynb).
PERSISTENCIA = {
    "Amatitlán": {"siempre": 14.3, "casi_nunca": 2.0},
    "Atitlán": {"siempre": 0.0, "casi_nunca": 99.3},
}

UMBRAL_ALTO = 10.0
UMBRAL_MUY_ALTO = 25.0


# ---------------------------------------------------------------------------
# Datos
# ---------------------------------------------------------------------------
df = pd.read_csv(os.path.join(TABLAS_DIR, "estadisticas_por_escena.csv"), parse_dates=["fecha"])
df_ok = df[df["calidad_ok"]]
corr = pd.read_csv(os.path.join(TABLAS_DIR, "correlaciones_por_escena.csv"))


def resumen(lago):
    sub = df_ok[df_ok["lago"] == lago]
    return {
        "n": len(sub),
        "mediana_tipica": sub["chl_mediana"].median(),
        "mediana_promedio": sub["chl_mediana"].mean(),
        "min": sub["chl_mediana"].min(),
        "fecha_min": sub.loc[sub["chl_mediana"].idxmin(), "fecha"].strftime("%d/%m/%Y"),
        "max": sub["chl_mediana"].max(),
        "fecha_max": sub.loc[sub["chl_mediana"].idxmax(), "fecha"].strftime("%d/%m/%Y"),
        "area": sub["area_analizada_km2"].mean(),
        "pct_alta": sub["pct_area_alta"].mean(),
        "pct_alta_max": sub["pct_area_alta"].max(),
        "pct_muy_alta": sub["pct_area_muy_alta"].mean(),
        "pct_muy_alta_max": sub["pct_area_muy_alta"].max(),
        "fechas_eutroficas": int((sub["chl_mediana"] > UMBRAL_ALTO).sum()),
    }


AMA = resumen("Amatitlán")
ATI = resumen("Atitlán")


def correlacion(lago, indice):
    sub = corr[corr["lago"] == lago]
    return sub[f"pearson_{indice}"].median()


# ---------------------------------------------------------------------------
# Documento
# ---------------------------------------------------------------------------
class Informe(FPDF):
    def header(self):
        pass

    def footer(self):
        if self.page_no() == 1:  # la carátula no se numera
            return
        self.set_y(-15)
        self.set_font(FAMILIA, size=12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, str(self.page_no() - 1), align="C")


pdf = Informe(orientation="P", unit="mm", format="A4")
pdf.add_font(FAMILIA, "", RUTA_FUENTE)
pdf.set_margins(25, 25, 25)
pdf.set_auto_page_break(auto=True, margin=25)
pdf.set_text_color(0, 0, 0)
pdf.add_page()
pdf.set_font(FAMILIA, size=12)

ALTO_LINEA = 6.5


def parrafo(texto, espacio=3.5):
    pdf.set_font(FAMILIA, size=12)
    pdf.multi_cell(0, ALTO_LINEA, texto, align="J", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(espacio)


def titulo(texto, espacio_antes=5):
    if pdf.get_y() > 230:
        pdf.add_page()
    else:
        pdf.ln(espacio_antes)
    pdf.set_font(FAMILIA, size=12)
    pdf.multi_cell(0, ALTO_LINEA, texto, align="L", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1.5)


def linea(texto, sangria=0, alto=ALTO_LINEA):
    pdf.set_font(FAMILIA, size=12)
    if sangria:
        pdf.set_x(pdf.l_margin + sangria)
    pdf.multi_cell(0, alto, texto, align="L", new_x="LMARGIN", new_y="NEXT")


def vineta(texto):
    pdf.set_font(FAMILIA, size=12)
    pdf.set_x(pdf.l_margin + 5)
    pdf.multi_cell(0, ALTO_LINEA, "- " + texto, align="J", new_x="LMARGIN", new_y="NEXT")


def tabla(encabezados, filas, anchos):
    pdf.set_font(FAMILIA, size=12)
    for i, celda in enumerate(encabezados):
        pdf.cell(anchos[i], ALTO_LINEA, celda, align="L")
    pdf.ln(ALTO_LINEA)
    for fila in filas:
        if pdf.get_y() > 250:
            pdf.add_page()
            for i, celda in enumerate(encabezados):
                pdf.cell(anchos[i], ALTO_LINEA, celda, align="L")
            pdf.ln(ALTO_LINEA)
        for i, celda in enumerate(fila):
            pdf.cell(anchos[i], ALTO_LINEA, str(celda), align="L")
        pdf.ln(ALTO_LINEA)
    pdf.ln(3.5)


def figura(nombre, pie, ancho=150):
    ruta = os.path.join(FIGURAS_DIR, nombre)
    if not os.path.exists(ruta):
        raise FileNotFoundError(ruta)

    # Salta de página solo si la figura y su pie no caben en lo que queda.
    with Image.open(ruta) as imagen:
        alto_mm = ancho * imagen.height / imagen.width
    lineas_pie = 1 + len(pie) // 95
    espacio_necesario = alto_mm + (lineas_pie + 1) * ALTO_LINEA
    if pdf.get_y() + espacio_necesario > pdf.h - pdf.b_margin:
        pdf.add_page()
    x = (pdf.w - ancho) / 2
    pdf.image(ruta, x=x, w=ancho)
    pdf.ln(2)
    pdf.set_font(FAMILIA, size=12)
    pdf.multi_cell(0, ALTO_LINEA, pie, align="J", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)


# ---------------------------------------------------------------------------
# Carátula
# ---------------------------------------------------------------------------
def centrado(texto):
    pdf.set_font(FAMILIA, size=12)
    pdf.multi_cell(0, ALTO_LINEA, texto, align="C", new_x="LMARGIN", new_y="NEXT")


ANCHO_LOGO = 42
with Image.open(LOGO) as _logo:
    pdf.image(LOGO, x=(pdf.w - ANCHO_LOGO) / 2, y=30, w=ANCHO_LOGO)
    pdf.set_y(30 + ANCHO_LOGO * _logo.height / _logo.width + 14)

centrado("Universidad del Valle de Guatemala")
centrado("Facultad de Ingeniería")
centrado("Departamento de Ciencias de la Computación")
centrado("CC3084 Data Science, Semestre II 2026")
pdf.ln(20)

centrado("Laboratorio 4. Análisis de datos geoespaciales")
pdf.ln(4)
centrado("Monitoreo de cianobacteria en los lagos de Atitlán y Amatitlán")
centrado("con imágenes del satélite Sentinel-2")
pdf.ln(24)

centrado("Integrantes")
pdf.ln(2)
for integrante in INTEGRANTES:
    centrado(integrante)
pdf.ln(20)

centrado(FECHA_ENTREGA)

# ---------------------------------------------------------------------------
# Cuerpo del informe
# ---------------------------------------------------------------------------
pdf.add_page()

titulo("Resumen", espacio_antes=0)
parrafo(
    "Este informe presenta el estado de la proliferación de cianobacteria en los lagos de Atitlán "
    "y Amatitlán entre enero de 2025 y julio de 2026, estimada a partir de imágenes del satélite "
    "Sentinel-2. Se analizaron 22 imágenes, once de cada lago, en las fechas oficiales definidas "
    "para el laboratorio. El resultado central es una diferencia enorme entre los dos cuerpos de "
    f"agua: en Amatitlán la concentración típica de clorofila-a fue de {AMA['mediana_tipica']:.1f} "
    f"microgramos por litro y en {AMA['fechas_eutroficas']} de las {AMA['n']} fechas confiables el "
    "lago estuvo en condición eutrófica, con un episodio extremo el "
    f"{AMA['fecha_max']} en que el {AMA['pct_muy_alta_max']:.0f} por ciento de la superficie "
    "alcanzó niveles propios de una floración masiva. En Atitlán, en cambio, la concentración típica "
    f"fue de {ATI['mediana_tipica']:.1f} microgramos por litro y ninguna fecha superó el umbral de "
    "alerta. Además de la magnitud, el análisis muestra dónde ocurre el problema: en Amatitlán la "
    "cianobacteria se concentra de forma permanente en la cuenca occidental, frente a la "
    "desembocadura del río Villalobos, mientras que en Atitlán las señales más altas, siempre "
    "moderadas, aparecen únicamente en las bahías cercanas a los poblados."
)

# ---------------------------------------------------------------------------
titulo("1. Por qué monitorear desde el satélite")
parrafo(
    "Las cianobacterias son microorganismos que viven de forma natural en los lagos, pero que "
    "cuando encuentran exceso de nutrientes, agua cálida y poco movimiento se multiplican hasta "
    "formar floraciones visibles. Esas floraciones consumen el oxígeno del agua, matan peces, "
    "arruinan el paisaje y algunas especies liberan toxinas peligrosas para las personas y los "
    "animales. Vigilarlas es, por lo tanto, un asunto de salud pública, de economía local y de "
    "conservación."
)
parrafo(
    "El problema práctico es que tomar muestras de agua es caro, lento y solo describe el punto "
    "exacto donde se tomó la muestra. Un lago como Atitlán tiene más de cien kilómetros cuadrados "
    "de superficie: para saber qué pasa en todo el lago haría falta un número enorme de muestras "
    "el mismo día. Los satélites resuelven precisamente ese problema. El satélite Sentinel-2, del "
    "programa europeo Copernicus, fotografía todo Guatemala cada pocos días y mide, en cada punto "
    "de diez por diez metros, cuánta luz de distintos colores refleja la superficie. El agua limpia "
    "y el agua con cianobacteria reflejan la luz de forma distinta, y esa diferencia es la que "
    "permite estimar la concentración de algas sin tocar el agua."
)

titulo("2. Datos utilizados")
parrafo(
    "Se trabajó con las once fechas oficiales establecidas para cada lago, seleccionadas por su baja "
    "nubosidad, en el período comprendido entre enero de 2025 y julio de 2026. Para cada fecha se "
    "descargó únicamente el recorte del área del lago y solo las bandas de color necesarias, de modo "
    "que el volumen de datos se mantuviera manejable. La descarga se hizo directamente desde el "
    "servicio de Copernicus mediante su interfaz de programación, sin intervención manual."
)
parrafo(
    "Sobre cada imagen se calcularon cuatro capas de información. La primera es una máscara de agua, "
    "que separa el espejo del lago de la tierra que lo rodea, para que ni la vegetación de la ribera "
    "ni los techos de los poblados contaminen los resultados. Las otras tres son índices, es decir "
    "números que resumen el color de cada punto del agua:"
)
vineta(
    "El índice de cianobacteria, calculado con el script de detección de cianobacteria publicado en "
    "el repositorio de scripts de Sentinel Hub. Se basa en el contraste entre el rojo y el borde del "
    "rojo, que es donde la clorofila de las algas deja su huella más clara, y se convierte a una "
    "estimación de clorofila-a en microgramos por litro."
)
vineta(
    "El NDVI, o índice de vegetación, que es alto donde hay material vegetal. Sobre el agua, un NDVI "
    "elevado delata una nata de algas flotando en la superficie."
)
vineta(
    "El NDWI, o índice de agua, que es alto donde el agua está limpia y se comporta ópticamente como "
    "agua."
)
pdf.ln(2)
parrafo(
    "Para interpretar los valores de clorofila-a se usó la clasificación trófica de la Organización "
    "para la Cooperación y el Desarrollo Económicos, que es el estándar habitual en limnología: por "
    "debajo de 2.6 microgramos por litro el agua se considera oligotrófica, es decir muy limpia; "
    "entre 2.6 y 8 es mesotrófica; entre 8 y 25 es eutrófica, con exceso de nutrientes; y por encima "
    "de 25 es hipereutrófica, que es la condición de una floración establecida. En este informe se "
    "usan diez microgramos por litro como umbral de alerta y veinticinco como umbral de floración."
)

titulo("3. Control de calidad de las imágenes")
parrafo(
    "Antes de analizar nada se revisó la calidad de cada imagen, porque una imagen con nubes o con "
    "errores de corrección atmosférica puede producir cifras espectaculares que no corresponden a "
    "nada real. Se aplicaron dos filtros: que las mediciones de cada punto fueran físicamente "
    "posibles, y que se viera al menos el sesenta por ciento de la superficie del lago."
)
parrafo(
    "Cuatro de las veintidós imágenes no pasaron ese control: la de Atitlán del 18 de enero de 2025, "
    "cubierta de bruma, con solo el veintitrés por ciento de puntos utilizables; la de Atitlán del "
    "13 de abril de 2026 y las de Amatitlán del 2 y del 7 de febrero de 2026, con nubes que tapaban "
    "la mitad o más del espejo de agua. Esas cuatro fechas aparecen en las tablas y en los mapas, "
    "pero no se usaron para calcular promedios ni para comparar los lagos, porque un lago visto a "
    "medias no es comparable con un lago visto completo. Todas las cifras de este informe se basan "
    "en las dieciocho imágenes restantes, nueve de cada lago."
)
parrafo(
    "Por la misma razón, los resúmenes de cada fecha se expresan con la mediana y no solo con el "
    "promedio. La mediana es el valor típico del lago, el que deja la mitad de los puntos por debajo "
    "y la mitad por encima, y tiene la ventaja de no dejarse arrastrar por unos pocos puntos "
    "extremos, que en imágenes satelitales son casi siempre errores de medición y no algas."
)

# ---------------------------------------------------------------------------
titulo("4. Resultados")

titulo("4.1 Cómo evolucionó la cianobacteria en el tiempo")
parrafo(
    "La figura 1 resume el período completo. El panel de la izquierda muestra la concentración "
    "típica de cianobacteria en cada fecha y el de la derecha, qué porcentaje de la superficie del "
    "lago estaba por encima del umbral de alerta ese mismo día."
)
figura(
    "comparacion_lagos.png",
    "Figura 1. Evolución de la cianobacteria en los dos lagos entre enero de 2025 y julio de 2026. "
    "A la izquierda, la concentración típica de clorofila-a por fecha; la línea punteada marca el "
    "umbral de alerta de diez microgramos por litro. A la derecha, el porcentaje de la superficie "
    "del lago que superaba ese umbral en cada fecha.",
    ancho=165,
)
parrafo(
    f"En Amatitlán la línea nunca baja de manera sostenida. El valor típico oscila entre "
    f"{AMA['min']:.1f} microgramos por litro, su mejor día ({AMA['fecha_min']}), y "
    f"{AMA['max']:.1f} microgramos por litro, su peor día ({AMA['fecha_max']}), y en "
    f"{AMA['fechas_eutroficas']} de las {AMA['n']} fechas confiables el lago estuvo por encima del "
    "umbral de alerta. Es decir, la floración no es un accidente ocasional en Amatitlán, sino su "
    "estado habitual. Se distinguen tres momentos críticos: enero de 2026, finales de abril de 2026 "
    "y, muy por encima de todo lo demás, el 19 de junio de 2026, cuando la concentración típica "
    "llegó a sextuplicar el umbral de alerta."
)
parrafo(
    f"En Atitlán la línea es plana y baja: el valor típico se mantiene entre {ATI['min']:.1f} y "
    f"{ATI['max']:.1f} microgramos por litro en todas las fechas, siempre dentro del rango "
    "mesotrófico y siempre por debajo del umbral de alerta. La única fecha que asoma algo de señal "
    "es el 21 de noviembre de 2025, con cerca del diez por ciento de la superficie por encima del "
    "umbral, justo al terminar la temporada de lluvias, que es cuando las quebradas arrastran tierra "
    "y nutrientes hacia el lago."
)

titulo("4.2 Dónde se concentra la cianobacteria dentro de cada lago")
parrafo(
    "El promedio de un lago esconde lo más importante para quien tiene que actuar: la floración no "
    "se reparte de forma pareja. La figura 2 compara, para cada lago, el día más limpio y el día más "
    "crítico del período, con la misma escala de color en los cuatro mapas."
)
figura(
    "mapas_extremos_por_lago.png",
    "Figura 2. Distribución de la cianobacteria en el día más limpio y en el día más crítico de cada "
    "lago. Los tonos azules corresponden a agua limpia y los rojos a concentraciones propias de una "
    "floración. Las zonas en blanco son puntos que no se pudieron medir por nubes.",
    ancho=165,
)
parrafo(
    "En Amatitlán el patrón se repite en casi todas las fechas: los valores más altos se concentran "
    "en la cuenca occidental, la que está frente a la desembocadura del río Villalobos, y en el "
    "estrangulamiento que separa las dos cuencas del lago. La cuenca oriental, más amplia, aparece "
    "sistemáticamente más limpia. Esto indica que el problema tiene un origen fijo en el espacio, el "
    "ingreso de agua cargada de nutrientes por el occidente, y no un origen difuso repartido por "
    "toda la ribera. En las fechas críticas, sin embargo, la mancha deja de estar confinada y cubre "
    "todo el espejo de agua: en condiciones normales la floración es un fenómeno localizado, y en "
    "los episodios extremos se convierte en un fenómeno de lago completo."
)
parrafo(
    "En Atitlán la superficie se ve homogénea y limpia en todas las fechas. Los pocos valores altos "
    "aparecen pegados a la orilla y en las bahías, que es donde desembocan las quebradas y donde se "
    "concentra la población. La parte central y profunda del lago no muestra señal de floración en "
    "ninguna de las fechas analizadas. Conviene aclarar que los puntos pegados a la costa son "
    "también los más propensos a contaminarse con el reflejo del suelo y de la vegetación de la "
    "ribera, de modo que ese realce costero debe leerse como una señal a vigilar y no como una "
    "medición firme."
)
parrafo(
    "Las figuras 3 y 4 muestran todas las fechas de cada lago, una al lado de la otra, para ver la "
    "evolución del patrón espacial."
)
figura(
    "mapas_comparativos_amatitlan.png",
    "Figura 3. Lago de Amatitlán: distribución de la cianobacteria en las once fechas analizadas. "
    "Nótese cómo la cuenca occidental, arriba a la izquierda en cada mapa, casi siempre aparece más "
    "cargada que la oriental, y cómo el 19 de junio de 2026 el lago completo se satura. Las fechas "
    "del 2 y el 7 de febrero de 2026 se ven incompletas porque las nubes taparon el lago.",
    ancho=170,
)
figura(
    "mapas_comparativos_atitlan.png",
    "Figura 4. Lago de Atitlán: distribución de la cianobacteria en las once fechas analizadas. El "
    "lago se mantiene uniformemente en tonos azules, es decir en niveles bajos, durante todo el "
    "período. La imagen del 18 de enero de 2025 aparece moteada porque la bruma impidió medir la "
    "mayoría de los puntos.",
    ancho=170,
)

titulo("4.3 Qué tan extensa es la floración en cada fecha")
parrafo(
    "Una misma concentración promedio puede corresponder a una mancha pequeña y muy intensa o a una "
    "capa delgada repartida por todo el lago, y la respuesta ambiental es distinta en cada caso. La "
    "figura 5 muestra, para cada fecha, qué porcentaje de la superficie del lago superaba el umbral "
    "de alerta y qué porcentaje superaba el umbral de floración."
)
figura(
    "extension_floracion.png",
    "Figura 5. Porcentaje de la superficie de cada lago con valores altos de cianobacteria en cada "
    "fecha. Las barras de la izquierda corresponden al umbral de alerta de diez microgramos por "
    "litro y las de la derecha al umbral de floración de veinticinco.",
    ancho=160,
)
parrafo(
    f"En Amatitlán, en promedio el {AMA['pct_alta']:.0f} por ciento de la superficie observada está "
    f"por encima del umbral de alerta, y el {AMA['pct_muy_alta']:.0f} por ciento por encima del "
    f"umbral de floración. En su peor fecha esos porcentajes llegan al {AMA['pct_alta_max']:.0f} y "
    f"al {AMA['pct_muy_alta_max']:.0f} por ciento respectivamente: prácticamente todo el lago en "
    "condición de floración masiva. Incluso en su mejor fecha, una quinta parte del lago está por "
    "encima del umbral de alerta."
)
parrafo(
    f"En Atitlán el promedio es del {ATI['pct_alta']:.1f} por ciento de la superficie, y en seis de "
    "las nueve fechas confiables el porcentaje es inferior al uno por ciento. El máximo del período "
    f"es del {ATI['pct_alta_max']:.0f} por ciento, alcanzado el 21 de noviembre de 2025."
)

titulo("4.4 Zonas donde el problema es permanente")
parrafo(
    "Para distinguir el problema crónico del episódico se contó, punto por punto, en cuántas de las "
    "fechas observadas se superó el umbral de alerta. El resultado es el mapa de la figura 6: los "
    "tonos claros marcan lugares donde la cianobacteria está alta casi siempre, y los oscuros, "
    "lugares donde casi nunca lo está."
)
figura(
    "zonas_persistentes.png",
    "Figura 6. Zonas persistentes de acumulación. Para cada punto del lago se indica el porcentaje "
    "de las fechas observadas en que superó los diez microgramos por litro.",
    ancho=170,
)
parrafo(
    f"En Amatitlán, el {PERSISTENCIA['Amatitlán']['siempre']:.0f} por ciento de la superficie del "
    "lago supera el umbral de alerta en al menos ocho de cada diez fechas observadas. Ese núcleo "
    "coincide con la cuenca occidental y el estrangulamiento central: ahí la floración no es "
    "estacional, es permanente. En Atitlán no existe ninguna zona con ese comportamiento, y el "
    f"{PERSISTENCIA['Atitlán']['casi_nunca']:.0f} por ciento del lago supera el umbral, como máximo, "
    "en dos de cada diez fechas."
)
parrafo(
    "Este resultado tiene una consecuencia práctica directa. En Amatitlán, cualquier medida de "
    "control y cualquier estación de monitoreo permanente debería instalarse en la desembocadura del "
    "Villalobos y en la cuenca occidental, porque es ahí donde el fenómeno se origina y se sostiene. "
    "En Atitlán, en cambio, el monitoreo debe ser preventivo y concentrarse en las bahías cercanas a "
    "los poblados, que es donde aparecen las primeras señales."
)

titulo("4.5 Relación con los índices de vegetación y de agua")
parrafo(
    "Una pregunta útil para el monitoreo es si otros índices más sencillos y ampliamente disponibles "
    "sirven como señal de alerta. La figura 7 cruza, punto por punto, el NDVI y el NDWI con la "
    "concentración estimada de cianobacteria."
)
figura(
    "correlacion_indices.png",
    "Figura 7. Relación entre los índices de vegetación y de agua y la concentración de "
    "cianobacteria, considerando todos los puntos de agua de todas las fechas. Los colores indican "
    "cuántos puntos caen en cada zona del gráfico.",
    ancho=160,
)
parrafo(
    f"El NDVI muestra una relación positiva y consistente: el valor típico por fecha es de "
    f"{correlacion('Amatitlán', 'ndvi'):.2f} en Amatitlán y {correlacion('Atitlán', 'ndvi'):.2f} en "
    "Atitlán, llega hasta 0.92 en las fechas de floración de Amatitlán, y al juntar todas las fechas "
    "en un solo conjunto, como se hace en la figura 7, queda en 0.52 y 0.39 respectivamente. La "
    "explicación es directa: una nata de "
    "cianobacteria flotando se comporta ópticamente como vegetación, refleja mucho infrarrojo y poco "
    "rojo, que es exactamente lo que mide el NDVI. En la práctica, un NDVI que sube dentro del agua "
    "es una señal de alerta de floración superficial."
)
parrafo(
    f"El NDWI muestra la relación inversa: {correlacion('Amatitlán', 'ndwi'):.2f} como valor típico "
    "por fecha en Amatitlán, hasta menos 0.90 en sus fechas de floración, y una relación débil en "
    "Atitlán. También es "
    "coherente: el NDWI es alto cuando el agua está limpia y se comporta como agua, y baja cuando la "
    "superficie se cubre de material orgánico flotante. En Atitlán la relación es débil simplemente "
    "porque casi no hay floración que detectar y el índice varía dentro del ruido de medición."
)
parrafo(
    "Es importante señalar una limitación de este análisis: los tres índices se calculan a partir de "
    "las mismas bandas de color del satélite, de modo que una parte de la correlación es de origen "
    "matemático y no biológico. Por eso lo relevante no es el número exacto, sino la dirección y la "
    "consistencia del resultado, que se repite en todas las fechas críticas."
)

titulo("4.6 Distribución de valores y estacionalidad")
parrafo(
    "La figura 8 compara la distribución completa de valores de los dos lagos. No se trata solo de "
    "que Amatitlán tenga un promedio más alto: su distribución es mucho más ancha, es decir conviven "
    "zonas todavía limpias con zonas de concentración muy elevada. Atitlán, en cambio, presenta una "
    "distribución estrecha y estable, sin la cola de valores altos que caracteriza a un lago con "
    "floraciones."
)
figura(
    "boxplot_lagos.png",
    "Figura 8. Distribución de la concentración de cianobacteria en todos los puntos de agua "
    "analizados durante el período. Las líneas punteadas marcan el umbral de alerta y el de "
    "floración.",
    ancho=125,
)
parrafo(
    "Respecto a la estacionalidad, los datos disponibles no permiten confirmar un patrón, y es "
    "importante decirlo con claridad. De las nueve fechas confiables de Amatitlán solo una cae en "
    "época lluviosa, y de las de Atitlán solo tres, de modo que cualquier diferencia entre "
    "temporadas está dominada por qué fechas tocó observar y no por el comportamiento del lago. Lo "
    "que sí se puede señalar es que los dos valores más altos de Amatitlán ocurren en junio, al "
    "inicio de las lluvias, y en enero, en plena época seca. Son dos mecanismos distintos y ambos "
    "plausibles: el arrastre de nutrientes por las primeras lluvias del año y la concentración por "
    "evaporación y estancamiento durante el estiaje. Confirmarlo exigiría una serie de imágenes con "
    "cobertura pareja de los doce meses."
)
figura(
    "estacionalidad.png",
    "Figura 9. Concentración típica de cianobacteria según el mes de la observación y promedio por "
    "temporada. La comparación entre temporadas es solo indicativa, porque el número de fechas de "
    "época lluviosa es muy pequeño.",
    ancho=165,
)

# ---------------------------------------------------------------------------
titulo("5. Comparación entre los dos lagos")
parrafo(
    "La tabla siguiente resume las cifras principales del período, calculadas sobre las nueve fechas "
    "confiables de cada lago."
)
tabla(
    ["Indicador", "Amatitlán", "Atitlán"],
    [
        ["Superficie de agua analizada", f"{AMA['area']:.0f} km²", f"{ATI['area']:.0f} km²"],
        ["Clorofila-a típica del período", f"{AMA['mediana_tipica']:.1f} µg/L", f"{ATI['mediana_tipica']:.1f} µg/L"],
        ["Fecha más limpia", f"{AMA['min']:.1f} µg/L", f"{ATI['min']:.1f} µg/L"],
        ["Fecha más crítica", f"{AMA['max']:.1f} µg/L", f"{ATI['max']:.1f} µg/L"],
        ["Fechas sobre el umbral de alerta", f"{AMA['fechas_eutroficas']} de {AMA['n']}", f"0 de {ATI['n']}"],
        ["Superficie sobre el umbral, promedio", f"{AMA['pct_alta']:.0f} %", f"{ATI['pct_alta']:.1f} %"],
        ["Superficie sobre el umbral, máximo", f"{AMA['pct_alta_max']:.0f} %", f"{ATI['pct_alta_max']:.0f} %"],
        ["Superficie con floración permanente", f"{PERSISTENCIA['Amatitlán']['siempre']:.0f} %", f"{PERSISTENCIA['Atitlán']['siempre']:.0f} %"],
    ],
    [85, 35, 35],
)
parrafo(
    "La diferencia es de orden de magnitud en las dos dimensiones que importan. En intensidad, el "
    f"peor día de Amatitlán, con {AMA['max']:.1f} microgramos por litro, es unas quince veces el "
    f"peor día de Atitlán, con {ATI['max']:.1f}. En frecuencia, Amatitlán supera el umbral de alerta "
    "en dos de cada tres fechas y Atitlán en ninguna. Y en persistencia, Amatitlán tiene un núcleo "
    "permanentemente afectado, mientras que Atitlán no tiene ninguno."
)
parrafo(
    "Los dos lagos están en el mismo país y bajo el mismo régimen climático, de modo que la "
    "explicación de esta diferencia hay que buscarla en la cuenca y en la forma de cada lago:"
)
vineta(
    "Presión urbana y aguas residuales. Amatitlán recibe el río Villalobos, que drena buena parte "
    "del área metropolitana de la Ciudad de Guatemala, con más de tres millones de habitantes, aguas "
    "residuales insuficientemente tratadas y descargas industriales. Ese aporte continuo de fósforo "
    "y nitrógeno es el combustible de la floración. La cuenca de Atitlán es predominantemente rural, "
    "con población mucho menor y repartida en los pueblos de la ribera."
)
vineta(
    "Tamaño y profundidad. De Atitlán se observaron alrededor de cien kilómetros cuadrados de espejo "
    "de agua, con profundidades que superan los trescientos metros; de Amatitlán, unos trece "
    "kilómetros cuadrados con profundidades de algunas decenas de metros. En un lago pequeño y poco "
    "profundo la misma carga de nutrientes se concentra mucho más, el agua se calienta más rápido y "
    "el sedimento del fondo devuelve fósforo a la columna de agua con facilidad. El enorme volumen "
    "de Atitlán diluye y amortigua."
)
vineta(
    "Temperatura. Amatitlán se encuentra a unos mil doscientos metros sobre el nivel del mar y "
    "Atitlán a unos mil quinientos sesenta, de modo que el agua de Amatitlán es varios grados más "
    "cálida, lo que favorece directamente el crecimiento de las cianobacterias."
)
vineta(
    "Geografía de la entrada de agua. En Amatitlán la carga entra concentrada por un solo punto, lo "
    "que explica que la mancha empiece siempre en la cuenca occidental. Atitlán es una caldera "
    "volcánica sin río de salida cuyos ingresos son quebradas pequeñas repartidas por toda la "
    "ribera, sin ningún afluente equivalente al Villalobos."
)

titulo("6. Limitaciones del análisis")
parrafo(
    "Los resultados deben leerse teniendo presentes cuatro limitaciones. Primero, el satélite mide "
    "color, no organismos: la estimación de clorofila-a es un indicador de biomasa algal en la capa "
    "superficial y no distingue cianobacterias de otras algas, ni permite saber si la floración es "
    "tóxica. Para eso siguen siendo indispensables los muestreos en campo, que este método permite "
    "dirigir mejor y no reemplazar."
)
parrafo(
    "Segundo, la fórmula que convierte el color en concentración de clorofila-a es empírica y fue "
    "calibrada en otros lagos, de modo que los valores absolutos pueden tener un sesgo; las "
    "comparaciones entre fechas y entre zonas del lago, que son la base de este informe, son mucho "
    "más confiables que las cifras exactas."
)
parrafo(
    "Tercero, once fechas por lago en un período de dieciocho meses son suficientes para "
    "caracterizar el contraste entre los dos cuerpos de agua, pero insuficientes para establecer "
    "tendencias o ciclos estacionales, sobre todo porque la época lluviosa está muy poco "
    "representada. Y cuarto, las nubes limitan la observación: cuatro de las veintidós imágenes "
    "tuvieron que descartarse de los promedios por ese motivo."
)

titulo("7. Conclusiones")
parrafo(
    "El lago de Amatitlán presenta una proliferación de cianobacteria crónica, extensa y con un "
    "origen espacial identificable. En dos de cada tres fechas analizadas el lago estuvo en "
    "condición eutrófica; una séptima parte de su superficie está afectada de forma prácticamente "
    "permanente, siempre en la cuenca occidental frente a la desembocadura del río Villalobos; y el "
    "19 de junio de 2026 se registró un episodio en el que casi la totalidad del lago alcanzó "
    "condiciones de floración masiva."
)
parrafo(
    "El lago de Atitlán, en el mismo período, se mantuvo en condición mesotrófica sin ningún "
    "episodio de floración detectable desde el satélite. Las únicas señales de aumento, siempre "
    "moderadas, se localizan en las bahías cercanas a los poblados y en la fecha inmediatamente "
    "posterior a la temporada de lluvias, lo que sugiere que el arrastre de nutrientes desde la "
    "cuenca es el factor a vigilar."
)
parrafo(
    "La comparación entre ambos lagos ilustra con claridad el papel de la presión urbana sobre la "
    "calidad del agua: dos lagos del mismo país, bajo el mismo clima, con estados ecológicos "
    "radicalmente distintos según reciban o no la descarga de un área metropolitana. En términos de "
    "gestión, esto significa que en Amatitlán el esfuerzo debe concentrarse en reducir la carga de "
    "nutrientes que entra por el Villalobos, porque mientras esa entrada continúe cualquier medida "
    "dentro del lago será paliativa; y que en Atitlán la prioridad es la vigilancia preventiva de "
    "las bahías pobladas, para actuar antes de que el problema se instale."
)
parrafo(
    "Por último, el trabajo muestra que el monitoreo satelital es una herramienta viable y de bajo "
    "costo para este propósito. Con imágenes públicas y gratuitas es posible reconstruir el estado "
    "de un lago completo en fechas pasadas, identificar las zonas donde conviene tomar muestras y "
    "detectar episodios críticos que un programa de muestreo puntual difícilmente registraría."
)

pdf.output(SALIDA)
print(f"Informe generado: {SALIDA}")

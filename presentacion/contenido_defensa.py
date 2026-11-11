# Contenido de las láminas (lo ejecuta armar_defensa.py)
B = "image1.jpg"   # fondo blanco con logo arriba a la derecha
e = lambda f: os.path.join(EDA, f); s_ = lambda f: os.path.join(SIM, f)
LAMINAS = []
def nueva(fondo=B, notas=""): L = Lamina(fondo, notas); LAMINAS.append(L); return L

# 1 Portada
L = nueva("image7.jpg", "Presentación personal y del trabajo. Agradecer al jurado. Anticipar la estructura: problema, datos, modelos, simulador con verdad conocida, conclusiones.")
L.texto(0.9, 1.25, 10.6, 2.6, "Estudio in silico para la generación de datos proteómicos sintéticos y evaluación de modelos predictivos en la enfermedad de Chagas", size=32, bold=True)
L.texto(0.9, 3.95, 10.6, 0.8, "Trabajo Final de la Maestría en Explotación de Datos y Gestión del Conocimiento", size=20, color=NARANJA)
L.texto(2.6, 5.35, 7.0, 1.3, [dict(t="Lic. Brenda Buonincontro", bold=True), "Director: Mg. Ezequiel Omar Nuske", dict(t="Facultad de Ingeniería · Universidad Austral · 13 de noviembre de 2026", size=13, color=GRIS)], size=18, gap=4)
L.imagen(os.path.join(REC, "image8.png"), 9.6, 6.25, 3.75, 0.82)

# 2 Chagas
L = nueva(notas="Contexto clínico. El dato central es el último: no existe hoy forma de anticipar qué pacientes van a progresar a la forma cardíaca.").titulo("La enfermedad de Chagas", "Una enfermedad desatendida, sin biomarcadores de progresión")
tarjeta_dato(L, 0.9, 2.1, 3.6, 3.2, "8 millones", "de personas infectadas en 21 países de América", size=38)
tarjeta_dato(L, 4.85, 2.1, 3.6, 3.2, "30%", "progresa a la fase crónica sintomática, sobre todo cardíaca")
tarjeta_dato(L, 8.8, 2.1, 3.6, 3.2, "0", "biomarcadores validados para predecir quién va a progresar", fill=TINTE_N)
L.texto(0.9, 5.65, 11.5, 0.4, "Solo el 10% de las personas infectadas accede al diagnóstico.", size=18, bold=True)
L.texto(0.9, 6.55, 11.5, 0.3, "Fuentes: Lynn et al., 2020; Rassi et al., 2010; Bonney et al., 2019; Martín-Escolano et al., 2020.", size=11, color=GRIS)

# 3 Punto de partida
L = nueva(notas="Por qué simular: no hay datos crudos. Y por qué no alcanza con simular y clasificar: la circularidad. De ahí sale la pregunta del trabajo.").titulo("El punto de partida", "Pocos datos disponibles y un riesgo metodológico")
L.caja(0.9, 2.15, 5.6, 3.3); L.texto(1.2, 2.4, 5.0, 0.4, "Los datos", size=20, bold=True, color=NARANJA)
L.texto(1.2, 2.95, 5.0, 2.4, [dict(t="Garg et al. (2016), PLoS NTD, licencia CC BY 4.0", bullet=True), dict(t="Proteómica de PBMC por 2D-GE: 30 sanos, 25 asintomáticos (C/A) y 28 sintomáticos (C/S)", bullet=True), dict(t="Sin datos crudos en repositorios: solo la tabla de cambios relativos de 192 proteínas", bullet=True)], size=15, gap=8)
L.caja(6.8, 2.15, 5.6, 3.3, TINTE_N); L.texto(7.1, 2.4, 5.0, 0.4, "El riesgo: circularidad", size=20, bold=True, color=NARANJA)
L.texto(7.1, 2.95, 5.0, 2.4, "Si la diferencia entre grupos se coloca en la simulación, que un modelo la detecte no demuestra nada sobre el método.", size=16)
L.texto(0.9, 5.8, 11.5, 1.0, "Pregunta del trabajo: ¿en qué medida cada método recupera las proteínas que realmente discriminan, y cuántos pacientes hacen falta?", size=18, bold=True)

# 4 Objetivos
L = nueva(notas="El objetivo habla de discriminar estadios clínicos, no de predecir progresión: el diseño es transversal.").titulo("Objetivos")
L.caja(0.9, 2.1, 11.5, 1.6); L.texto(1.2, 2.25, 10.9, 1.3, "Implementar un flujo de trabajo in silico que combine datos proteómicos sintéticos con verdad conocida, modelos de ML e interpretabilidad, para evaluar su capacidad de recuperar proteínas que discriminan entre estadios clínicos (C/A vs. C/S).", size=17)
for i, t in enumerate(["Generar datos proteómicos sintéticos con verdad conocida.", "Entrenar y evaluar modelos de ML con distintos tamaños muestrales, variabilidad y tamaño de efecto.", "Seleccionar proteínas candidatas y medir la precisión, el recall y la estabilidad de la selección."]):
    y = 4.0 + i * 0.9
    L.caja(0.9, y, 0.7, 0.7, NARANJA); L.texto(0.9, y, 0.7, 0.7, str(i + 1), size=24, bold=True, color=BLANCO, align="c", anchor="m")
    L.texto(1.85, y, 10.5, 0.7, t, size=17, anchor="m")

# 5 Flujo
L = nueva(notas="Dos etapas. La primera es exploratoria y verifica que el pipeline funciona. La segunda es la que responde la pregunta del trabajo.").titulo("Flujo de trabajo", "Análisis exploratorio y simulador con verdad conocida")
pasos = [("Tabla 2 de Garg et al. (2016)", "192 proteínas"), ("Dataset sintético", "83 pacientes"), ("Modelos de ML", "LR, RF y GB"), ("Interpretabilidad", "17 candidatas"), ("Verdad conocida", "12 escenarios × 100")]
for i, (a, b) in enumerate(pasos):
    x = 0.9 + i * 2.36; f = TINTE_N if i == 4 else TINTE
    L.caja(x, 2.6, 2.06, 2.1, f); L.texto(x + 0.15, 2.8, 1.76, 1.1, a, size=15, bold=True, align="c", anchor="m"); L.texto(x + 0.1, 3.95, 1.86, 0.6, b, size=13, color=NARANJA, align="c", anchor="m")
    if i < 4: L.texto(x + 2.06, 3.35, 0.3, 0.5, "›", size=28, bold=True, color=NARANJA, align="c", anchor="m")
L.texto(0.9, 5.3, 11.5, 0.4, "Todo el código y los datos están publicados: github.com/buonincontro/tf_mcd", size=16)

# 6 Dataset
L = nueva(notas="Los parámetros salen del estudio de referencia. La tabla muestra promedios entre las 192 proteínas: el CV observado queda cerca del nominal.").titulo("Dataset sintético", "83 pacientes simulados y 192 proteínas")
L.texto(0.9, 2.1, 5.6, 3.8, [dict(t="Distribución lognormal por proteína y por grupo", bullet=True), dict(t="Media: 100 × el cambio relativo reportado", bullet=True), dict(t="CV de 49%, 67% y 77% (sanos, C/A y C/S), tomados del estudio de referencia", bullet=True), dict(t="Semilla fija: el dataset se reproduce a partir de la tabla publicada", bullet=True)], size=16, gap=10)
L.tabla(7.0, 2.1, [1.3, 0.8, 1.1, 1.1, 1.1], [["Grupo", "n", "Media", "DE", "CV"], ["Sanos", "30", "99.9", "47.6", "0.47"], ["C/A", "25", "171.6", "108.8", "0.64"], ["C/S", "28", "179.4", "130.1", "0.73"]], alto=0.6, size=15)
L.texto(7.0, 4.65, 5.4, 0.6, "Promedio, entre las 192 proteínas, de la media, el desvío estándar (DE) y el coeficiente de variación (CV).", size=12, color=GRIS)

# 7 EDA
L = nueva(notas="Cada punto es una proteína. Contra los sanos difiere casi todo, por construcción. Entre los dos estadios, solo 20 proteínas: ahí está la señal difícil.").titulo("Análisis exploratorio", "Casi todo distingue sanos de infectados; poco distingue los estadios")
L.imagen(e("eda_fig_A2_volcanes.png"), 0.7, 1.95, 8.3, 3.7)
L.caja(9.3, 2.1, 3.1, 1.6); L.texto(9.5, 2.2, 2.7, 0.7, "185 y 188", size=30, bold=True, color=NARANJA); L.texto(9.5, 2.9, 2.7, 0.7, "de 192 proteínas difieren de los sanos", size=13)
L.caja(9.3, 3.95, 3.1, 1.6, TINTE_N); L.texto(9.5, 4.05, 2.7, 0.7, "20", size=30, bold=True, color=NARANJA); L.texto(9.5, 4.75, 2.7, 0.7, "de 192 difieren entre C/S y C/A", size=13)
L.texto(0.9, 6.1, 11.5, 0.5, "Prueba t de Welch sobre log2, con corrección de Benjamini-Hochberg (q < 0.05).", size=12, color=GRIS)

# 8 Heatmap + PCA
L = nueva(notas="El mapa de calor muestra lo mismo proteína por proteína. En el PCA estandarizado, el segundo componente separa parcialmente los dos estadios.").titulo("192 proteínas en 83 pacientes")
L.imagen(e("eda_fig_A3_heatmap.png"), 0.7, 1.55, 6.9, 5.2); L.imagen(e("eda_fig_A5_pca_estandarizado.png"), 7.9, 2.1, 4.6, 3.4)
L.texto(7.9, 5.65, 4.6, 1.1, "PCA sobre datos estandarizados: el primer componente (33.1%) separa sanos de infectados; el segundo (3.1%) separa parcialmente C/A de C/S.", size=12, color=GRIS)

# 9 Modelos
L = nueva(notas="La regresión logística y Random Forest rinden parecido; se eligió la logística por simplicidad. Aclarar que la fuga en la validación cruzada se corrigió y los valores no cambian.").titulo("Modelos de clasificación", "C/A vs. C/S: 53 pacientes y 192 proteínas")
L.tabla(0.9, 2.1, [3.6, 3.9, 4.0], [["Modelo", "AUC, validación cruzada", "AUC, 200 particiones"], ["Regresión logística", "0.957 ± 0.038", "0.970 ± 0.051"], ["Random Forest", "0.935 ± 0.083", "0.978 ± 0.044"], ["Gradient Boosting", "0.617 ± 0.074", "0.861 ± 0.130"]], alto=0.6, size=15)
L.texto(0.9, 4.85, 11.5, 1.9, [dict(t="Se eligió la regresión logística: rinde como Random Forest y es más simple de interpretar.", bullet=True), dict(t="Con el escalado dentro de cada partición, los valores no cambian.", bullet=True), dict(t="La señal fue colocada en la simulación: el AUC verifica el pipeline, no estima el desempeño clínico.", bullet=True)], size=15, gap=8)

# 10 Candidatas
L = nueva(notas="El panel coincide con el estudio original porque los datos vienen de ahí. Varias proteínas son contaminantes conocidos de 2D-GE: son candidatas ilustrativas.").titulo("Proteínas candidatas", "Panel de 17 spots, unas 14 proteínas")
L.imagen(e("eda_fig_A4_boxplots_top12.png"), 0.7, 1.75, 5.7, 5.0)
L.texto(6.8, 2.1, 5.6, 3.2, [dict(t="Seleccionadas por coeficientes e importancia por permutación", bullet=True), dict(t="Predominan actina, queratinas y fibrinógeno", bullet=True), dict(t="Coinciden con el estudio original por construcción", bullet=True), dict(t="Varias son contaminantes habituales de 2D-GE", bullet=True)], size=16, gap=10)
L.caja(6.8, 5.35, 5.6, 0.95, TINTE_N); L.texto(7.05, 5.35, 5.1, 0.95, "Son candidatas ilustrativas, no biomarcadores.", size=17, bold=True, anchor="m")

# 11 Simulador
L = nueva(notas="Acá se define de antemano qué proteínas tienen efecto real. Así se puede medir qué recupera cada método, en lugar de solo ver si clasifica.").titulo("Simulador con verdad conocida", "Para medir qué recupera cada método")
tarjeta_dato(L, 0.9, 2.15, 3.6, 2.75, "19", "biomarcadores verdaderos (C/S y C/A difieren al menos 1.41 veces)", fill=TINTE_N)
tarjeta_dato(L, 4.85, 2.15, 3.6, 2.75, "173", "proteínas de efecto débil")
tarjeta_dato(L, 8.8, 2.15, 3.6, 2.75, "500", "proteínas nulas, que representan el ruido")
L.texto(0.9, 5.2, 11.5, 1.6, [dict(t="12 escenarios × 100 simulaciones: tamaño muestral (30 a 200), variabilidad, tamaño del efecto, correlación y datos faltantes. Test independiente de 200 pacientes.", bullet=True), dict(t="Métodos: regresión logística L1 y L2 (coeficientes, SHAP y permutación), Random Forest y Gradient Boosting.", bullet=True)], size=15, gap=8)

# 12 Cuántos pacientes
L = nueva(notas="Resultado principal. Con 50 pacientes, parecido al estudio original, el mejor método recupera la mitad. Para llegar al 80% hacen falta unos 200.").titulo("¿Cuántos pacientes hacen falta?", "Recuperación de los 19 biomarcadores verdaderos")
L.imagen(s_("figura12.png"), 0.7, 1.7, 5.2, 5.2)
L.caja(6.4, 2.1, 6.0, 1.85, TINTE_N); L.texto(6.7, 2.2, 2.4, 1.6, "51%", size=48, bold=True, color=NARANJA, anchor="m"); L.texto(9.0, 2.2, 3.2, 1.6, "con 50 pacientes (regresión logística L2, coeficientes)", size=15, anchor="m")
L.caja(6.4, 4.2, 6.0, 1.85); L.texto(6.7, 4.3, 2.4, 1.6, "≈ 80%", size=44, bold=True, color=NARANJA, anchor="m"); L.texto(9.0, 4.3, 3.2, 1.6, "recién con 200 pacientes", size=15, anchor="m")
L.texto(6.4, 6.3, 6.0, 0.45, "Gradient Boosting recupera 21% con 50 pacientes.", size=14, color=GRIS)

# 13 AUC vs recall
L = nueva(notas="El mensaje más importante del trabajo. Todos los modelos clasifican muy bien, pero el panel que eligen está incompleto.").titulo("AUC alto, panel incompleto", "Con 50 pacientes")
L.caja(0.9, 2.15, 5.6, 2.6); L.texto(0.9, 2.35, 5.6, 1.2, "0.91 – 0.97", size=48, bold=True, color=NAVY, align="c", anchor="m"); L.texto(1.2, 3.65, 5.0, 0.9, "AUC de los modelos en el test independiente", size=16, align="c")
L.caja(6.8, 2.15, 5.6, 2.6, TINTE_N); L.texto(6.8, 2.35, 5.6, 1.2, "21% – 51%", size=48, bold=True, color=NARANJA, align="c", anchor="m"); L.texto(7.1, 3.65, 5.0, 0.9, "de los biomarcadores verdaderos recuperados", size=16, align="c")
L.texto(0.9, 5.15, 11.5, 0.9, "Que un modelo clasifique bien no garantiza que el panel seleccionado coincida con los biomarcadores verdaderos.", size=19, bold=True)
L.texto(0.9, 6.2, 11.5, 0.4, "Control negativo, sin diferencia real entre grupos: AUC = 0.50 en los cuatro modelos.", size=14, color=GRIS)

# 14 Estabilidad
L = nueva(notas="Incluso con 200 pacientes, dos estudios del mismo tipo elegirían paneles que coinciden solo en parte.").titulo("Estabilidad de la selección", "Dos estudios iguales eligen paneles distintos")
L.imagen(s_("figura13.png"), 0.7, 1.85, 6.3, 4.8)
L.caja(7.4, 2.1, 5.0, 1.75); L.texto(7.65, 2.2, 2.1, 1.55, "0.20", size=40, bold=True, color=NARANJA, anchor="m"); L.texto(9.7, 2.2, 2.5, 1.55, "índice de Jaccard con 50 pacientes (mejor método)", size=14, anchor="m")
L.caja(7.4, 4.1, 5.0, 1.75, TINTE_N); L.texto(7.65, 4.2, 2.1, 1.55, "≤ 0.52", size=40, bold=True, color=NARANJA, anchor="m"); L.texto(9.7, 4.2, 2.5, 1.55, "con 200 pacientes", size=14, anchor="m")
L.texto(7.4, 6.1, 5.0, 0.6, "1 = siempre el mismo panel; 0 = nunca coincide.", size=12, color=GRIS)

# 15 Sensibilidad
L = nueva(notas="La variabilidad entre pacientes es lo que más pesa. La correlación entre proteínas casi no cambia el resultado.").titulo("¿Qué afecta la recuperación?", "Regresión logística L2 por coeficientes, 50 pacientes")
L.imagen(s_("figura14.png"), 0.7, 1.75, 5.9, 5.0)
filas = [("Variabilidad", "de 0.80 a 0.36 al pasar de CV 0.3 a 1.0", TINTE_N), ("Tamaño del efecto", "de 0.24 a 0.70 (0.5 a 1.5 veces)", TINTE), ("Datos faltantes (20%)", "de 0.51 a 0.37", TINTE), ("Correlación", "cambios de hasta 0.07", TINTE)]
for i, (a, b, f) in enumerate(filas):
    y = 2.05 + i * 1.12; L.caja(7.0, y, 5.4, 0.95, f); L.texto(7.25, y + 0.12, 4.9, 0.35, a, size=16, bold=True); L.texto(7.25, y + 0.5, 4.9, 0.35, b, size=14)

# 16 Observaciones del jurado
L = nueva(notas="Repaso rápido de cómo se atendió cada observación. Detenerse solo en las que el jurado quiera profundizar.").titulo("Observaciones del jurado", "Qué se revisó en esta versión")
L.tabla(0.9, 2.1, [4.4, 7.1], [["Observación", "Respuesta"], ["Licitud del uso de los datos", "Artículo con licencia CC BY 4.0; datos agregados, no de pacientes"], ["“Progresión” con datos transversales", "Objetivo reformulado: discriminar estadios clínicos"],
    ["Análisis exploratorio insuficiente", "Análisis de las 192 proteínas (Anexo, Figuras A1 a A5)"], ["Para qué simular; circularidad", "Simulador con verdad conocida"], ["Ajuste de la lognormal", "Gráfico Q-Q y pruebas de normalidad sobre los datos simulados"],
    ["Tabla 2 poco clara", "Recalculada como promedios por proteína"], ["Curva ROC y matriz de confusión", "El AUC ordena; la matriz usa un corte fijo de 0.5"], ["Fuga en la validación cruzada", "Recalculada con el escalado en cada partición: sin cambios"]], alto=0.5, size=13)

# 17 Limitaciones
L = nueva(notas="Ser explícita con las limitaciones: es lo que le da credibilidad al resto.").titulo("Limitaciones")
lim = [("Datos simulados", "Los resultados valen bajo los supuestos del simulador."), ("Un único estudio de origen", "Los efectos reportados pueden estar inflados."), ("Técnica 2D-GE", "Incluye contaminantes conocidos: actina, queratinas y fibrinógeno."), ("Diseño transversal", "No permite evaluar el valor pronóstico.")]
for i, (a, b) in enumerate(lim):
    x = 0.9 + (i % 2) * 5.9; y = 2.15 + (i // 2) * 2.3
    L.caja(x, y, 5.6, 2.0, TINTE_N if i == 0 else TINTE); L.texto(x + 0.3, y + 0.3, 5.0, 0.4, a, size=19, bold=True, color=NARANJA); L.texto(x + 0.3, y + 0.9, 5.0, 0.9, b, size=16)

# 18 Conclusiones
L = nueva(notas="Cerrar con las cuatro ideas. La tercera es la que quiero que recuerden.").titulo("Conclusiones")
conc = ["El pipeline in silico es reproducible y está publicado.", "Con 50 pacientes, el mejor método recupera la mitad de los biomarcadores verdaderos; hacen falta unos 200 para llegar al 80%.", "Un AUC alto no garantiza recuperar los biomarcadores, y la selección es poco estable.", "Es una prueba de concepto metodológica: las proteínas son candidatas ilustrativas."]
for i, t in enumerate(conc):
    y = 2.1 + i * 1.12
    L.caja(0.9, y, 0.8, 0.95, NARANJA); L.texto(0.9, y, 0.8, 0.95, str(i + 1), size=26, bold=True, color=BLANCO, align="c", anchor="m")
    L.caja(1.85, y, 10.55, 0.95, TINTE_N if i == 2 else TINTE); L.texto(2.1, y, 10.1, 0.95, t, size=17, bold=(i == 2), anchor="m")

# 19 Líneas futuras
L = nueva(notas="El simulador indica cuántos pacientes harían falta: es un insumo directo para diseñar la validación.").titulo("Líneas futuras")
fut = [("Análisis funcional", "Enriquecimiento de vías y redes de interacción (STRING)"), ("Validación in vitro", "ELISA o Western blot en PBMC de pacientes en distintos estadios"), ("Estudio longitudinal", "Seguimiento de asintomáticos para evaluar el valor pronóstico")]
for i, (a, b) in enumerate(fut):
    x = 0.9 + i * 3.95
    L.caja(x, 2.15, 3.6, 2.9, TINTE); L.texto(x + 0.3, 2.45, 3.0, 0.8, a, size=19, bold=True, color=NARANJA); L.texto(x + 0.3, 3.4, 3.0, 1.5, b, size=16)
    if i < 2: L.texto(x + 3.6, 3.35, 0.35, 0.5, "›", size=28, bold=True, color=NARANJA, align="c", anchor="m")
L.texto(0.9, 5.45, 11.5, 0.8, "Además: calibrar los supuestos del simulador (correlación, variabilidad y datos faltantes) con datos proteómicos reales.", size=16)

# 20 Cierre
L = nueva("image10.jpg", "Agradecer y abrir a preguntas.")
L.texto(0.9, 2.4, 9.0, 1.2, "Muchas gracias", size=54, bold=True, color=BLANCO); L.texto(0.9, 3.7, 9.0, 0.6, "Preguntas", size=26, color=BLANCO)

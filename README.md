# Pipeline de Tesis de Maestría en Ciencia de Datos

Título de la tesis:  
Estudio in silico para la generación de datos proteómicos sintéticos y evaluación de modelos predictivos en la enfermedad de Chagas.  
Trabajo presentado para optar al título de Magíster en Ciencia de Datos.  
Facultad de Ingeniería, Universidad Austral.

El repositorio contiene el pipeline in silico usado en la tesis: generación de un dataset proteómico
sintético a partir de datos publicados (Garg et al., 2016), entrenamiento y evaluación de
modelos de ML e interpretación de proteínas candidatas.

## Estructura

```
notebooks/
├── 01_simulacion_datos.ipynb       # Objetivo específico 1: generación del dataset sintético
├── 02_modelado_ml.ipynb            # Objetivo específico 2: entrenamiento y evaluación de modelos
└── 03_seleccion_candidatas.ipynb   # Objetivo específico 3: selección e interpretación de candidatas
scripts/
├── reproducir_dataset.py           # descarga la Tabla 2 (Europe PMC) y regenera el dataset sintético sin pasos manuales
└── tabla3_sin_fuga.py              # Tabla 3 con el escalado dentro de cada partición de la validación cruzada
eda/
├── eda_192_proteinas.py            # estadística descriptiva y comparaciones entre grupos de las 192 proteínas
├── eda_figuras.py                  # Figuras A1 a A5 del Anexo
├── eda_estadisticas_por_proteina.csv
└── figuras/
simulador/
├── simulador_completo.py           # simulador con verdad conocida (sección 4.4): 12 escenarios x 100 simulaciones
├── tablas_figuras.py               # Tablas 6 a 8 y Figuras 12 a 14
└── resultados/                     # resumen, tablas, figuras y resultados por simulación
presentacion/
├── Defensa - Buonincontro - Trabajo Final MCD.pptx   # presentación de la defensa (20 láminas)
├── armar_defensa.py y contenido_defensa.py          # generan la presentación
└── vista_previa/                                    # miniaturas de las láminas
data/
├── tabla2_garg2016.csv             # Tabla 2 de Garg et al. (2016), CC BY 4.0
└── dataset_sintetico_pbmc.csv      # dataset sintético (83 pacientes x 192 proteínas)
```

## Cómo correrlo

Los notebooks fueron desarrollados en Google Colab y son autocontenidos (incluyen sus propios `pip install`
donde hace falta). Para reproducir localmente:

1. Crear un entorno e instalar dependencias: `pip install -r requirements.txt`
2. Correr `01_simulacion_datos.ipynb` primero — genera el dataset sintético (CSV) usado como input de los
   notebooks 2 y 3.
3. Correr `02_modelado_ml.ipynb` y `03_seleccion_candidatas.ipynb`, subiendo el CSV generado en el paso
   anterior cuando el notebook lo solicite.

Todos los notebooks fijan `random_state=42` / `np.random.seed(42)` para reproducibilidad.

## Fuente de datos

Los datos base (Table 2) provienen de:

> Garg NJ, Soman KV, Zago MP, Koo S-J, Spratt H, Stafford S, et al. (2016). Changes in Proteome Profile of Peripheral Blood Mononuclear Cells in Chronic Chagas Disease. *PLoS Negl Trop Dis* 10(2): e0004490. https://doi.org/10.1371/journal.pntd.0004490

El artículo se publicó bajo licencia [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), que permite reutilizar y adaptar su contenido con atribución. La Tabla 2 está disponible en XML estructurado a través de la API REST de Europe PMC (PMC4769231); `scripts/reproducir_dataset.py` la descarga de ahí.

No se utilizan datos de pacientes reales, el dataset es enteramente sintético.

## Reproducción sin pasos manuales

```bash
pip install -r requirements.txt
python scripts/reproducir_dataset.py      # genera data/tabla2_garg2016.csv y data/dataset_sintetico_pbmc.csv
python scripts/tabla3_sin_fuga.py --grid  # Tabla 3 con y sin fuga de información
python eda/eda_192_proteinas.py data/dataset_sintetico_pbmc.csv eda
python eda/eda_figuras.py data/dataset_sintetico_pbmc.csv eda/eda_estadisticas_por_proteina.csv eda/figuras
python simulador/simulador_completo.py data/tabla2_garg2016.csv 100   # unos 4 minutos en 10 núcleos
python simulador/tablas_figuras.py
```

`reproducir_dataset.py` repite la simulación del notebook 01 con la misma semilla y obtiene el mismo dataset
(media por grupo 99.9 / 171.6 / 179.4; CV promedio 0.47 / 0.64 / 0.73).

## Simulador con verdad conocida

`simulador/simulador_completo.py` reimplementa el simulador de la sección 4.4 (19 biomarcadores verdaderos, 173 proteínas
de efecto débil y 500 nulas, con correlación por bloques) y evalúa regresión logística L1 y L2, Random Forest y Gradient
Boosting en 12 escenarios de 100 simulaciones. `simulador/tablas_figuras.py` genera las Tablas 6 a 8 y las Figuras 12 a 14.
Dos corridas dan resultados idénticos (semilla maestra fija).

La importancia por permutación se calcula por validación cruzada dentro del entrenamiento. Calculada sobre el test
independiente de 200 pacientes recupera más biomarcadores (0.73 frente a 0.35 con 50 pacientes), pero usa 200 pacientes
adicionales con estadio conocido, por lo que no es comparable con los demás criterios; se informa solo como referencia
(`L2_perm_test` en `resultados/resumen.csv`).

Decisiones que la tesis no detalla y que se fijaron en esta reimplementación: la regularización de L1 se busca entre
0.01 y 10, y los datos faltantes se generan con una probabilidad que decrece con la abundancia (función logística,
20% en promedio).

## Pendiente

Falta subir el código original del simulador con verdad conocida, la repetición con 200 semillas (sección 5.3), el
control de calidad del simulador y la verificación de la distribución lognormal (sección 5.5).

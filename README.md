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
├── simulador_verdad_conocida.py    # reimplementación del simulador (sección 4.4): permutación con y sin el test
└── resumen_escenarios.csv          # resultados de 11 escenarios x 100 simulaciones
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
python simulador/simulador_verdad_conocida.py data/tabla2_garg2016.csv 100
```

`reproducir_dataset.py` repite la simulación del notebook 01 con la misma semilla y obtiene el mismo dataset
(media por grupo 99.9 / 171.6 / 179.4; CV promedio 0.47 / 0.64 / 0.73).

## Importancia por permutación con y sin el test

`simulador/simulador_verdad_conocida.py` reimplementa el simulador con verdad conocida para la regresión logística L2
y calcula la importancia por permutación de tres maneras. Recall de los 19 biomarcadores verdaderos (100 simulaciones):

| Pacientes | Coeficientes | Permutación sobre el test | Permutación sobre el entrenamiento | Permutación por validación cruzada |
|---|---|---|---|---|
| 30 | 0.40 | 0.70 | 0.02 | 0.24 |
| 50 | 0.52 | 0.72 | 0.03 | 0.35 |
| 100 | 0.70 | 0.72 | 0.04 | 0.49 |
| 200 | 0.80 | 0.66 | 0.03 | 0.58 |

La ventaja de la permutación con pocos pacientes se debe a los 200 pacientes adicionales del test. No reemplaza al
simulador original: no incluye L1, Random Forest, Gradient Boosting ni el escenario de datos faltantes.

## Pendiente

Falta subir el código del simulador con verdad conocida y de los análisis asociados (secciones 4.4 y 5.5 a 5.8
de la tesis: 12 escenarios x 100 simulaciones, repetición con 200 semillas y verificación de la distribución lognormal).

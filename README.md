# Pipeline de Tesis de Maestría en Ciencia de Datos

Título de la tesis:  
Estudio in silico para la generación de datos proteómicos sintéticos y evaluación de modelos predictivos en la enfermedad de Chagas.  
Trabajo presentado para optar al título de Magíster en Ciencia de Datos  
Facultad de Ingeniería, Universidad Austral

El repositorio contiene el pipeline in silico usado en la tesis: generación de un dataset proteómico
sintético a partir de datos publicados (Garg et al., 2016), entrenamiento y evaluación de
modelos de ML e interpretación de proteínas candidatas.

## Estructura

```
notebooks/
├── 01_simulacion_datos.ipynb       # Objetivo específico 1: generación del dataset sintético
├── 02_modelado_ml.ipynb            # Objetivo específico 2: entrenamiento y evaluación de modelos
└── 03_seleccion_candidatas.ipynb   # Objetivo específico 3: selección e interpretación de candidatas
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

> Garg et al. (2016). Proteomic profiling of PBMCs in Chagas disease patients. *[completar referencia]*

No se utilizan datos de pacientes reales, el dataset es enteramente sintético.


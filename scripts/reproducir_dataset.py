import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd

URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4769231/fullTextXML"
ID_TABLA = "pntd.0004490.t002"
GRUPOS = [("N/H", "NH_", 30, 0.49, None), ("C/A", "CA_", 25, 0.67, "CA"), ("C/S", "CS_", 28, 0.77, "CS")]
MEDIA_BASAL = 100

def descargar_tabla2():
    with urllib.request.urlopen(URL, timeout=60) as r:
        raiz = ET.fromstring(r.read())
    tabla = next(t for t in raiz.iter("table-wrap") if t.get("id") == ID_TABLA)
    texto = lambda e: re.sub(r"\s+", " ", "".join(e.itertext())).strip()
    filas = [[texto(c) for c in tr if c.tag in ("td", "th")] for tr in tabla.iter("tr")]
    return pd.DataFrame(filas[1:], columns=filas[0]).replace("", np.nan)

def generar_valores(media, cv, cantidad):
    varianza_relativa = np.log(1 + cv**2)
    mu = np.log(media) - varianza_relativa / 2
    return np.random.lognormal(mean=mu, sigma=np.sqrt(varianza_relativa), size=cantidad)

def simular(tabla):
    tabla = tabla.copy()
    tabla["CA"] = pd.to_numeric(tabla["C/A-vs-N/H"].str.replace("−", "-"), errors="coerce")
    tabla["CS"] = pd.to_numeric(tabla["C/S-vs-N/H"].str.replace("−", "-"), errors="coerce")
    tabla["Protein name"] = tabla["Protein name"].ffill()
    util = tabla.dropna(subset=["CA", "CS"])

    np.random.seed(42)
    generar_valores(100, 0.49, 5)
    partes = []
    for grupo, prefijo, n, cv, columna in GRUPOS:
        datos = {}
        for _, fila in util.iterrows():
            fc = 1 if columna is None else fila[columna]
            factor = fc if fc > 0 else 1 / abs(fc)
            datos[fila["Protein name"] + "_spot" + str(fila["Spot No."])] = generar_valores(MEDIA_BASAL * factor, cv, n)
        parte = pd.DataFrame(datos)
        parte["Grupo"] = grupo
        parte["Paciente"] = [prefijo + str(i + 1) for i in range(n)]
        partes.append(parte)
    return pd.concat(partes, ignore_index=True)

if __name__ == "__main__":
    salida = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(salida, exist_ok=True)
    tabla = descargar_tabla2()
    tabla.to_csv(os.path.join(salida, "tabla2_garg2016.csv"), index=False)
    dataset = simular(tabla)
    dataset.to_csv(os.path.join(salida, "dataset_sintetico_pbmc.csv"), index=False)
    proteinas = dataset.columns[:-2]
    print(f"Tabla 2: {len(tabla)} filas | dataset: {dataset.shape[0]} pacientes x {len(proteinas)} proteínas")
    for grupo, *_ in GRUPOS:
        sub = dataset.loc[dataset["Grupo"] == grupo, proteinas]
        print(f"{grupo}: media {sub.values.mean():.1f} | DE promedio por proteína {sub.std().mean():.1f} | CV promedio {(sub.std() / sub.mean()).mean():.2f}")

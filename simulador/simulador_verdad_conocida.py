"""Reimplementación del simulador con verdad conocida (sección 4.4 de la tesis) para
evaluar la importancia por permutación SIN usar el conjunto de test.

Variantes de permutación sobre la regresión logística L2:
  perm_test : sobre el test independiente de 200 pacientes (como describe la tesis)
  perm_train: sobre el propio conjunto de entrenamiento
  perm_cv   : validación cruzada de 5 particiones dentro del entrenamiento (fuera de la partición)
No reemplaza al simulador original de la tesis: solo cubre la regresión logística L2 y no incluye
el escenario de datos faltantes. Reproduce las Tablas 6 y 7 con diferencias de hasta 0.06 en recall.

Uso: python simulador/simulador_verdad_conocida.py data/tabla2_garg2016.csv [n_rep] [escenarios] [carpeta_salida]
"""
import os, sys, warnings, itertools
import numpy as np, pandas as pd
from joblib import Parallel, delayed
from scipy.stats import rankdata
from sklearn.linear_model import LogisticRegressionCV, LogisticRegression
from sklearn.model_selection import StratifiedKFold
warnings.filterwarnings("ignore")
N_NULAS, BLOQUE, TOP, N_TEST, N_PERM = 500, 10, 20, 200, 5

def verdad(ruta, umbral=0.5):
    t = pd.read_csv(ruta)
    f = lambda c: pd.to_numeric(t[c].astype(str).str.replace("−", "-"), errors="coerce")
    ca, cs = f("C/A-vs-N/H"), f("C/S-vs-N/H"); ok = ca.notna() & cs.notna()
    l2 = lambda v: np.log2(np.where(v > 0, v, 1 / np.abs(v)))
    mu_ca, delta = l2(ca[ok].values), l2(cs[ok].values) - l2(ca[ok].values)
    return mu_ca, delta, np.abs(delta) >= umbral

def auc(y, s):
    r = rankdata(s); n1 = y.sum(); n0 = len(y) - n1
    return (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)

def auc_cols(y, S):  # AUC por columna de una matriz de puntajes
    r = rankdata(S, axis=0); n1 = y.sum(); n0 = len(y) - n1
    return (r[y == 1].sum(0) - n1 * (n1 + 1) / 2) / (n1 * n0)

def generar(rng, n, mu_ca, delta, cv, efecto, rho, bloques):
    p = len(mu_ca) + N_NULAS; sigma = np.sqrt(np.log(1 + cv**2)) / np.log(2)
    mu = np.concatenate([mu_ca, np.zeros(N_NULAS)]); d = np.concatenate([delta * efecto, np.zeros(N_NULAS)])
    y = np.repeat([0, 1], n // 2)
    z = rng.standard_normal((n, bloques.max() + 1))[:, bloques]
    X = mu + np.outer(y, d) + sigma * (np.sqrt(rho) * z + np.sqrt(1 - rho) * rng.standard_normal((n, p)))
    return X, y

def perm_importancia(rng, X, y, coef, base=None):
    s = X @ coef; base = auc(y, s) if base is None else base; caida = np.zeros(X.shape[1])
    for _ in range(N_PERM):
        Xp = X[rng.permutation(len(y))]
        caida += base - auc_cols(y, s[:, None] + (Xp - X) * coef)
    return caida / N_PERM

def una_simulacion(semilla, n, mu_ca, delta, es_verdad, cv=0.67, efecto=1.0, rho=0.3):
    rng = np.random.default_rng(semilla); p = len(mu_ca) + N_NULAS
    bloques = rng.permutation(p) // BLOQUE
    Xtr, ytr = generar(rng, n, mu_ca, delta, cv, efecto, rho, bloques)
    Xte, yte = generar(rng, N_TEST, mu_ca, delta, cv, efecto, rho, bloques)
    m, s = Xtr.mean(0), Xtr.std(0); Xtr, Xte = (Xtr - m) / s, (Xte - m) / s
    skf = StratifiedKFold(5, shuffle=True, random_state=semilla % (2**31))
    mod = LogisticRegressionCV(Cs=10, cv=skf, penalty="l2", scoring="roc_auc", max_iter=2000).fit(Xtr, ytr)
    b = mod.coef_.ravel()
    imp = {"coef": np.abs(b), "shap": np.abs(b * Xtr).mean(0),
           "perm_test": perm_importancia(rng, Xte, yte, b), "perm_train": perm_importancia(rng, Xtr, ytr, b)}
    acc = np.zeros(p)
    for tr, va in skf.split(Xtr, ytr):
        bk = LogisticRegression(C=mod.C_[0], max_iter=2000).fit(Xtr[tr], ytr[tr]).coef_.ravel()
        if len(np.unique(ytr[va])) == 2: acc += perm_importancia(rng, Xtr[va], ytr[va], bk)
    imp["perm_cv"] = acc / 5
    verd = np.concatenate([es_verdad, np.zeros(N_NULAS, bool)]); nula = np.arange(p) >= len(mu_ca)
    out = {"auc_test": auc(yte, Xte @ b), "auc_train": auc(ytr, Xtr @ b)}
    for k, v in imp.items():
        # desempate aleatorio para no favorecer a las proteínas de la tabla (primeras columnas)
        orden = np.lexsort((rng.random(p), -v)); panel = orden[:TOP]
        out[f"recall_{k}"] = verd[panel].sum() / max(verd.sum(), 1); out[f"prec_{k}"] = verd[panel].mean()
        out[f"nulas_{k}"] = nula[panel].sum(); out[f"aucrank_{k}"] = auc(verd.astype(int), v) if verd.any() else np.nan
        out[f"panel_{k}"] = frozenset(panel.tolist())
    return out

def jaccard(paneles):
    return np.mean([len(a & b) / len(a | b) for a, b in itertools.combinations(paneles, 2)])

def escenario(nombre, n_rep, mu_ca, delta, es_verdad, n=50, **kw):
    r = Parallel(n_jobs=-1)(delayed(una_simulacion)(1000 + i, n, mu_ca, delta, es_verdad, **kw) for i in range(n_rep))
    df = pd.DataFrame(r); fila = {"escenario": nombre, "auc_test": df.auc_test.mean(), "auc_train": df.auc_train.mean()}
    for k in ["coef", "shap", "perm_test", "perm_train", "perm_cv"]:
        fila.update({f"recall_{k}": df[f"recall_{k}"].mean(), f"prec_{k}": df[f"prec_{k}"].mean(), f"nulas_{k}": df[f"nulas_{k}"].mean(),
                     f"aucrank_{k}": df[f"aucrank_{k}"].mean(), f"jaccard_{k}": jaccard(list(df[f"panel_{k}"]))})
    return fila, df

ESCENARIOS = [("n=30", dict(n=30)), ("n=50 (base)", dict(n=50)), ("n=100", dict(n=100)), ("n=200", dict(n=200)),
              ("CV 0.3", dict(cv=0.3)), ("CV 1.0", dict(cv=1.0)), ("Efecto 0.5", dict(efecto=0.5)), ("Efecto 1.5", dict(efecto=1.5)),
              ("rho 0", dict(rho=0.0)), ("rho 0.6", dict(rho=0.6)), ("Efecto 0 (control)", dict(efecto=0.0))]

if __name__ == "__main__":
    ruta = sys.argv[1]; n_rep = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    solo = sys.argv[3].split(",") if len(sys.argv) > 3 and sys.argv[3] else None
    salida = sys.argv[4] if len(sys.argv) > 4 else os.path.dirname(os.path.abspath(__file__))
    for u in (0.3, 0.5, 0.75): print(f"umbral {u}: {verdad(ruta, u)[2].sum()} verdaderas")
    mu_ca, delta, es_verdad = verdad(ruta)
    r = 2 ** np.abs(delta); print(f"diferencia C/S vs C/A: mediana {np.median(r):.2f}, RIC {np.quantile(r,.25):.2f}-{np.quantile(r,.75):.2f}, máx {r.max():.2f}")
    filas = []
    for nombre, kw in ESCENARIOS:
        if solo and not any(s in nombre for s in solo): continue
        fila, df = escenario(nombre, n_rep, mu_ca, delta, es_verdad, **kw); filas.append(fila)
        print(nombre, {k: round(float(v), 2) for k, v in fila.items() if k != "escenario" and (k.startswith(("recall", "auc_")))}, flush=True)
    pd.DataFrame(filas).round(3).to_csv(os.path.join(salida, "resumen_escenarios.csv" if not solo else "resumen_parcial.csv"), index=False)

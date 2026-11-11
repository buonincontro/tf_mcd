"""Simulador con verdad conocida (sección 4.4 de la tesis), reimplementación completa.

Métodos: regresión logística L1 (coef != 0) y L2 (|coef|, SHAP, permutación por validación
cruzada dentro del entrenamiento y, como referencia, permutación sobre el test), Random Forest
y Gradient Boosting (importancia por impureza). 12 escenarios x 100 simulaciones.

Uso: python simulador/simulador_completo.py data/tabla2_garg2016.csv [n_rep] [carpeta_salida]
"""
import os, sys, warnings, itertools
import numpy as np, pandas as pd
from joblib import Parallel, delayed
from scipy.stats import rankdata
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV
from sklearn.model_selection import StratifiedKFold
warnings.filterwarnings("ignore")
N_NULAS, BLOQUE, TOP, N_TEST, N_PERM, SEMILLA_MAESTRA = 500, 10, 20, 200, 5, 20261111
METODOS = ["L1", "L2_coef", "L2_perm_cv", "L2_shap", "RF", "GB", "L2_perm_test"]

def verdad(ruta, umbral=0.5):
    t = pd.read_csv(ruta)
    f = lambda c: pd.to_numeric(t[c].astype(str).str.replace("−", "-"), errors="coerce")
    ca, cs = f("C/A-vs-N/H"), f("C/S-vs-N/H"); ok = ca.notna() & cs.notna()
    l2 = lambda v: np.log2(np.where(v > 0, v, 1 / np.abs(v)))
    mu_ca = l2(ca[ok].values); delta = l2(cs[ok].values) - mu_ca
    return mu_ca, delta, np.abs(delta) >= umbral

def auc(y, s):
    r = rankdata(s); n1 = y.sum(); n0 = len(y) - n1
    return (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)

def auc_cols(y, S):
    r = rankdata(S, axis=0); n1 = y.sum(); n0 = len(y) - n1
    return (r[y == 1].sum(0) - n1 * (n1 + 1) / 2) / (n1 * n0)

def generar(rng, n, mu, d, cv, rho, bloques, p_falt):
    sigma = np.sqrt(np.log(1 + cv**2)) / np.log(2); p = len(mu)
    y = np.repeat([0, 1], n // 2)
    z = rng.standard_normal((n, bloques.max() + 1))[:, bloques]
    X = mu + np.outer(y, d) + sigma * (np.sqrt(rho) * z + np.sqrt(1 - rho) * rng.standard_normal((n, p)))
    if p_falt:  # faltantes no aleatorios: más probables cuanto menor es la abundancia (logística, media ~ p_falt)
        z = (X - X.mean()) / X.std(); X[rng.random((n, p)) < 1 / (1 + np.exp(-(np.log(p_falt / (1 - p_falt)) - 0.234 - z)))] = np.nan
    return X, y

def perm_importancia(rng, X, y, coef):
    s = X @ coef; base = auc(y, s); caida = np.zeros(X.shape[1])
    for _ in range(N_PERM):
        Xp = X[rng.permutation(len(y))]
        caida += base - auc_cols(y, s[:, None] + (Xp - X) * coef)
    return caida / N_PERM

def una_simulacion(semilla, n, mu_ca, delta, es_verdad, cv=0.67, efecto=1.0, rho=0.3, faltantes=0.0):
    rng = np.random.default_rng(semilla); p = len(mu_ca) + N_NULAS
    mu = np.concatenate([mu_ca, np.zeros(N_NULAS)]); d = np.concatenate([delta * efecto, np.zeros(N_NULAS)])
    bloques = rng.permutation(p) // BLOQUE
    p_falt = faltantes
    Xtr, ytr = generar(rng, n, mu, d, cv, rho, bloques, p_falt)
    Xte, yte = generar(rng, N_TEST, mu, d, cv, rho, bloques, p_falt)
    if faltantes > 0:  # imputación: mínimo observado en el entrenamiento menos 1 (log2)
        relleno = np.nanmin(Xtr, axis=0) - 1; relleno = np.where(np.isnan(relleno), 0.0, relleno)
        Xtr = np.where(np.isnan(Xtr), relleno, Xtr); Xte = np.where(np.isnan(Xte), relleno, Xte)
    m, s = Xtr.mean(0), Xtr.std(0); s[s == 0] = 1; Xtr, Xte = (Xtr - m) / s, (Xte - m) / s
    sem = int(semilla % (2**31)); skf = StratifiedKFold(5, shuffle=True, random_state=sem)
    l2 = LogisticRegressionCV(Cs=10, cv=skf, penalty="l2", scoring="roc_auc", max_iter=2000).fit(Xtr, ytr); b = l2.coef_.ravel()
    l1 = LogisticRegressionCV(Cs=np.logspace(-2, 1, 10), cv=skf, penalty="l1", solver="liblinear", max_iter=2000, random_state=sem).fit(Xtr, ytr); b1 = l1.coef_.ravel()  # grilla acotada: reproduce el tamaño de panel de la tesis
    rf = RandomForestClassifier(n_estimators=300, max_depth=None, random_state=sem).fit(Xtr, ytr)
    gb = GradientBoostingClassifier(n_estimators=200, learning_rate=0.1, max_depth=2, random_state=sem).fit(Xtr, ytr)
    acc = np.zeros(p)
    for tr, va in skf.split(Xtr, ytr):
        bk = LogisticRegression(C=l2.C_[0], max_iter=2000).fit(Xtr[tr], ytr[tr]).coef_.ravel()
        acc += perm_importancia(rng, Xtr[va], ytr[va], bk)
    imp = {"L1": np.abs(b1), "L2_coef": np.abs(b), "L2_perm_cv": acc / 5, "L2_shap": np.abs(b * Xtr).mean(0),
           "RF": rf.feature_importances_, "GB": gb.feature_importances_, "L2_perm_test": perm_importancia(rng, Xte, yte, b)}
    auc_l2 = auc(yte, Xte @ b)
    auc_mod = {"L1": auc(yte, Xte @ b1), "L2_coef": auc_l2, "L2_perm_cv": auc_l2, "L2_shap": auc_l2, "L2_perm_test": auc_l2,
               "RF": auc(yte, rf.predict_proba(Xte)[:, 1]), "GB": auc(yte, gb.predict_proba(Xte)[:, 1])}
    verd = np.concatenate([es_verdad, np.zeros(N_NULAS, bool)]) & (efecto > 0); nula = np.arange(p) >= len(mu_ca)
    out = {}
    for k, v in imp.items():
        orden = np.lexsort((rng.random(p), -v))  # desempate aleatorio
        panel = np.flatnonzero(v != 0) if k == "L1" else orden[:TOP]
        tp = verd[panel].sum(); rec = tp / verd.sum() if verd.any() else np.nan; pre = tp / len(panel) if len(panel) else 0.0
        out[f"recall_{k}"] = rec; out[f"prec_{k}"] = pre
        out[f"f1_{k}"] = 2 * pre * rec / (pre + rec) if verd.any() and pre + rec > 0 else (0.0 if verd.any() else np.nan)
        out[f"nulas_{k}"] = nula[panel].sum(); out[f"tam_{k}"] = len(panel)
        out[f"aucrank_{k}"] = auc(verd.astype(int), v) if verd.any() else np.nan
        out[f"auctest_{k}"] = auc_mod[k]; out[f"panel_{k}"] = frozenset(panel.tolist())
    return out

def jaccard(paneles):
    return np.mean([len(a & b) / len(a | b) if a | b else 1.0 for a, b in itertools.combinations(paneles, 2)])

ESCENARIOS = [("n30", dict(n=30)), ("base", dict(n=50)), ("n100", dict(n=100)), ("n200", dict(n=200)),
              ("cv03", dict(cv=0.3)), ("cv10", dict(cv=1.0)), ("ef05", dict(efecto=0.5)), ("ef15", dict(efecto=1.5)),
              ("rho0", dict(rho=0.0)), ("rho06", dict(rho=0.6)), ("falt20", dict(faltantes=0.2)), ("ef0", dict(efecto=0.0))]

if __name__ == "__main__":
    ruta = sys.argv[1]; n_rep = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    salida = sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")
    os.makedirs(salida, exist_ok=True)
    mu_ca, delta, es_verdad = verdad(ruta); print("biomarcadores verdaderos:", int(es_verdad.sum()), flush=True)
    semillas = np.random.SeedSequence(SEMILLA_MAESTRA).generate_state(n_rep)  # mismas semillas en todos los escenarios
    resumen = []
    for nombre, kw in ESCENARIOS:
        kw = dict(kw); n = kw.pop("n", 50)
        r = Parallel(n_jobs=-1)(delayed(una_simulacion)(int(s), n, mu_ca, delta, es_verdad, **kw) for s in semillas)
        df = pd.DataFrame(r)
        for k in METODOS:
            fila = {"escenario": nombre, "metodo": k, "estabilidad": jaccard(list(df[f"panel_{k}"]))}
            for m in ["recall", "prec", "f1", "nulas", "tam", "aucrank", "auctest"]:
                v = df[f"{m}_{k}"]; fila[m] = v.mean(); fila[f"{m}_p025"] = v.quantile(.025); fila[f"{m}_p975"] = v.quantile(.975)
                fila[f"{m}_p25"] = v.quantile(.25); fila[f"{m}_p75"] = v.quantile(.75)
            resumen.append(fila)
        df.drop(columns=[c for c in df if c.startswith("panel_")]).to_csv(os.path.join(salida, f"sim_{nombre}.csv"), index=False)
        print(nombre, {k: round(float(df[f'recall_{k}'].mean()), 2) for k in METODOS}, "| AUC L2/RF/GB/L1:",
              [round(float(df[f'auctest_{k}'].mean()), 2) for k in ("L2_coef", "RF", "GB", "L1")], flush=True)
    pd.DataFrame(resumen).round(4).to_csv(os.path.join(salida, "resumen.csv"), index=False)

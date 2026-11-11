"""Sección 5.3 y Figura 6: el diseño exploratorio (25 C/A, 28 C/S; partición 80/20) repetido con 200 semillas.

En cada repetición se simula una cohorte nueva y una partición distinta, y se mide el AUC de los tres
modelos en el conjunto de validación (11 pacientes).
Uso: python scripts/semillas_200.py data/tabla2_garg2016.csv [carpeta_salida]
"""
import os, sys, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from joblib import Parallel, delayed
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

t = pd.read_csv(sys.argv[1])
salida = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")
os.makedirs(salida, exist_ok=True)
fc = lambda c: pd.to_numeric(t[c].astype(str).str.replace("−", "-"), errors="coerce")
ca, cs = fc("C/A-vs-N/H"), fc("C/S-vs-N/H"); ok = ca.notna() & cs.notna()
factor = lambda v: np.where(v > 0, v, 1 / np.abs(v))
MEDIA_CA, MEDIA_CS = 100 * factor(ca[ok].values), 100 * factor(cs[ok].values)

def lognormal(media, cv, size, rng):
    s2 = np.log(1 + cv**2); return rng.lognormal(np.log(media) - s2 / 2, np.sqrt(s2), size)

def una(semilla):
    rng = np.random.default_rng(semilla); p = len(MEDIA_CA)
    X = np.vstack([lognormal(MEDIA_CA, 0.67, (25, p), rng), lognormal(MEDIA_CS, 0.77, (28, p), rng)]); y = np.r_[np.zeros(25), np.ones(28)]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=semilla)
    e = StandardScaler().fit(Xtr); Xtr, Xte = e.transform(Xtr), e.transform(Xte)
    modelos = {"Regresión logística": LogisticRegression(max_iter=2000),
               "Random Forest": RandomForestClassifier(n_estimators=200, random_state=semilla, n_jobs=1),
               "Gradient Boosting": GradientBoostingClassifier(n_estimators=200, random_state=semilla)}
    return {k: roc_auc_score(yte, m.fit(Xtr, ytr).predict_proba(Xte)[:, 1]) for k, m in modelos.items()}

df = pd.DataFrame(Parallel(n_jobs=-1)(delayed(una)(s) for s in range(200)))
tab = pd.DataFrame({"media": df.mean(), "desvío": df.std(), "mínimo": df.min(), "% con AUC=1": (df == 1).mean() * 100}).round(3)
print(tab); tab.to_csv(os.path.join(salida, "semillas_200.csv"))
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(figsize=(5.9, 3.9))
bp = ax.boxplot([df[c] for c in df], patch_artist=True, medianprops=dict(color="black"))
ax.set_xticks([1, 2, 3], list(df.columns))
for b, c in zip(bp["boxes"], ["#4d4d4d", "#969696", "#d9d9d9"]): b.set_facecolor(c); b.set_edgecolor("black")
ax.set_ylabel("AUC en el conjunto de validación (n=11)"); fig.tight_layout(); fig.savefig(os.path.join(salida, "figura6.png"), dpi=200)

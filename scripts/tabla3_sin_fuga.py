import os
import sys
import warnings

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")
args = [a for a in sys.argv[1:] if not a.startswith("--")]
ruta = args[0] if args else os.path.join(os.path.dirname(__file__), "..", "data", "dataset_sintetico_pbmc.csv")

datos = pd.read_csv(ruta)
np.random.seed(42)
proteinas = datos.columns[:-2]
datos = datos[datos["Grupo"].isin(["C/A", "C/S"])]
X, y = datos[proteinas], datos["Grupo"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
X_train_esc = StandardScaler().fit_transform(X_train)

modelos = {
    "Regresión logística": lambda: LogisticRegression(penalty="l2", max_iter=1000, random_state=42),
    "Random Forest": lambda: RandomForestClassifier(n_estimators=200, random_state=42),
    "Gradient Boosting": lambda: GradientBoostingClassifier(n_estimators=200, random_state=42),
}
print(f"{'Modelo':22s} {'con fuga':>16s} {'sin fuga':>16s}")
for nombre, crear in modelos.items():
    con = cross_val_score(crear(), X_train_esc, y_train, cv=cv, scoring="roc_auc")
    sin = cross_val_score(make_pipeline(StandardScaler(), crear()), X_train, y_train, cv=cv, scoring="roc_auc")
    print(f"{nombre:22s} {con.mean():8.3f} ± {con.std():.3f} {sin.mean():8.3f} ± {sin.std():.3f}")

if "--grid" in sys.argv:
    grillas = [
        ("Random Forest", RandomForestClassifier(random_state=42), {"n_estimators": [100, 200, 300], "max_depth": [None, 5, 10]}),
        ("Gradient Boosting", GradientBoostingClassifier(random_state=42),
         {"n_estimators": [50, 100, 200], "learning_rate": [0.01, 0.1, 0.3], "max_depth": [2, 3, 5]}),
    ]
    for nombre, modelo, grilla in grillas:
        con = GridSearchCV(modelo, grilla, cv=cv, scoring="roc_auc").fit(X_train_esc, y_train)
        paso = type(modelo).__name__.lower()
        sin = GridSearchCV(make_pipeline(StandardScaler(), modelo), {f"{paso}__{k}": v for k, v in grilla.items()}, cv=cv, scoring="roc_auc").fit(X_train, y_train)
        print(f"GridSearchCV {nombre}: con fuga {con.best_score_:.3f} {con.best_params_} | sin fuga {sin.best_score_:.3f}")

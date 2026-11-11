import os, sys, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
res = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")
R = pd.read_csv(os.path.join(res, "resumen.csv")).set_index(["escenario", "metodo"])
MET = ["L1", "L2_coef", "L2_perm_cv", "L2_shap", "RF", "GB"]
NOM = {"L1": "L1 (coef≠0)", "L2_coef": "L2 (|coef|)", "L2_perm_cv": "L2 (permutación)", "L2_shap": "L2 (SHAP)", "RF": "Random Forest", "GB": "Gradient Boosting"}
LEY = {"L1": "Logística L1 (coef≠0)", "L2_coef": "Logística L2 (|coef|)", "L2_perm_cv": "Logística L2 (permutación, validación cruzada)",
       "L2_shap": "Logística L2 (SHAP)", "RF": "Random Forest (importancia)", "GB": "Gradient Boosting (importancia)"}
EST = {"L1": ("-", "o"), "L2_coef": ("-", "s"), "L2_perm_cv": ("--", "^"), "L2_shap": (":", "v"), "RF": ("-.", "D"), "GB": ("--", "X")}

t6 = pd.DataFrame([{"n": n, "Método": NOM[m], "Sensibilidad": R.loc[(e, m), "recall"], "Precisión": R.loc[(e, m), "prec"], "Nulas sel.": R.loc[(e, m), "nulas"],
                    "AUC ranking": R.loc[(e, m), "aucrank"], "AUC test": R.loc[(e, m), "auctest"], "Estabilidad": R.loc[(e, m), "estabilidad"]}
                   for n, e in [(30, "n30"), (50, "base"), (100, "n100"), (200, "n200")] for m in MET])
t6.to_csv(os.path.join(res, "tabla6.csv"), index=False)

ESC7 = [("base", "Base"), ("cv03", "CV 0.3"), ("cv10", "CV 1.0"), ("ef05", "Efecto 0.5"), ("ef15", "Efecto 1.5"), ("rho0", "ρ = 0"), ("rho06", "ρ = 0.6"), ("falt20", "Falt. 20%")]
t7 = pd.DataFrame({"Método": [NOM[m] for m in MET], **{nom: [R.loc[(e, m), "recall"] for m in MET] for e, nom in ESC7}})
t7.to_csv(os.path.join(res, "tabla7.csv"), index=False)

base = pd.read_csv(os.path.join(res, "sim_base.csv")); ref = max(MET, key=lambda m: base[f"recall_{m}"].mean())
filas = []
for met, col in [("Sensibilidad", "recall"), ("F1", "f1")]:
    for m in MET:
        if m == ref: continue
        dif = base[f"{col}_{m}"] - base[f"{col}_{ref}"]; ee = dif.std(ddof=1) / np.sqrt(len(dif))
        filas.append({"Métrica": met, "Método": NOM[m], "Diferencia media": dif.mean(), "IC inf": dif.mean() - 1.96 * ee, "IC sup": dif.mean() + 1.96 * ee})
t8 = pd.DataFrame(filas); t8.to_csv(os.path.join(res, "tabla8.csv"), index=False)
pd.set_option("display.width", 220)
print("referencia Tabla 8:", ref); print(t6.round(2).to_string(index=False)); print(t7.round(2).to_string(index=False)); print(t8.round(2).to_string(index=False))
print("perm sobre test (referencia):", {e: round(float(R.loc[(e, 'L2_perm_test'), 'recall']), 2) for e in R.index.get_level_values(0).unique() if e != "ef0"})
print("control negativo AUC test:", {m: round(float(R.loc[('ef0', m), 'auctest']), 3) for m in ["L1", "L2_coef", "RF", "GB"]})
print("tamaño panel L1:", {e: round(float(R.loc[(e, 'L1'), 'tam']), 1) for e in ["n30", "base", "n100", "n200"]})
print("rango P2.5-P97.5 recall base:", {m: (round(float(R.loc[('base', m), 'recall_p025']), 2), round(float(R.loc[('base', m), 'recall_p975']), 2)) for m in MET})
print("F1 base:", {m: round(float(base[f'f1_{m}'].mean()), 2) for m in MET})

plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": 200, "savefig.bbox": "tight"})
def curva(ax, xs, escs, col, banda=True):
    for m in MET:
        y = [R.loc[(e, m), col] for e in escs]; ls, mk = EST[m]
        if banda and f"{col}_p25" in R.columns:
            ax.fill_between(xs, [R.loc[(e, m), f"{col}_p25"] for e in escs], [R.loc[(e, m), f"{col}_p75"] for e in escs], color="#000", alpha=.07, lw=0)
        ax.plot(xs, y, color="black", ls=ls, marker=mk, ms=4.5, lw=1.1, label=LEY[m])
N, EN = [30, 50, 100, 200], ["n30", "base", "n100", "n200"]

fig, ax = plt.subplots(2, 2, figsize=(7.2, 7.1))
for a, (col, tit, yl, lim) in zip(ax.ravel(), [("recall", "A. Recall (verdaderos recuperados)", "Recall", (0, 1.02)), ("prec", "B. Precisión del panel", "Precisión", (0, 1.02)),
                                               ("aucrank", "C. AUC de ranking", "AUC de ranking", (0, 1.02)), ("auctest", "D. AUC del modelo (test independiente)", "AUC del modelo en test", (0.7, 1.008))]):
    curva(a, N, EN, col); a.set_title(tit, fontsize=10); a.set_xlabel("n (pacientes)"); a.set_ylabel(yl); a.set_ylim(*lim)
h, l = ax[0, 0].get_legend_handles_labels(); fig.legend(h, l, loc="lower center", ncol=2, frameon=False, fontsize=8.2, bbox_to_anchor=(.5, -.075))
fig.tight_layout(); fig.savefig(os.path.join(res, "figura12.png")); plt.close(fig)

fig, a = plt.subplots(figsize=(6.2, 4.6))
for m in MET:
    ls, mk = EST[m]; a.plot(N, [R.loc[(e, m), "estabilidad"] for e in EN], color="black", ls=ls, marker=mk, ms=4.5, lw=1.1, label=LEY[m])
a.set_xlabel("n (pacientes)"); a.set_ylabel("Estabilidad (índice de Jaccard medio)"); a.set_ylim(0, 1.02); a.legend(frameon=False, fontsize=8.2, loc="upper left")
fig.tight_layout(); fig.savefig(os.path.join(res, "figura13.png")); plt.close(fig)

fig, ax = plt.subplots(2, 2, figsize=(7.2, 6.1))
for a, (xs, escs, tit, xl) in zip(ax.ravel(), [([.3, .67, 1.0], ["cv03", "base", "cv10"], "A. Variabilidad (CV)", "Coeficiente de variación (CV)"),
                                               ([.5, 1.0, 1.5], ["ef05", "base", "ef15"], "B. Tamaño del efecto", "Tamaño del efecto (× el reportado)"),
                                               ([0, .3, .6], ["rho0", "base", "rho06"], "C. Correlación", "Correlación intrabloque (ρ)")]):
    curva(a, xs, escs, "recall"); a.set_title(tit, fontsize=10); a.set_xlabel(xl); a.set_ylabel("Recall"); a.set_ylim(0, 1.02)
ax[1, 1].axis("off"); h, l = ax[0, 0].get_legend_handles_labels(); ax[1, 1].legend(h, l, loc="center", frameon=False, fontsize=8.2)
fig.tight_layout(); fig.savefig(os.path.join(res, "figura14.png")); plt.close(fig)

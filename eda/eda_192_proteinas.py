"""EDA de las 192 proteínas del dataset sintético (Objetivo específico 1).
Uso: python eda/eda_192_proteinas.py data/dataset_sintetico_pbmc.csv eda"""
import sys, os, warnings
import numpy as np, pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests
warnings.filterwarnings("ignore")
src = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(src))
d = pd.read_csv(src); prot = list(d.columns[:-2]); G = ["N/H", "C/A", "C/S"]
grp = {g: d.loc[d["Grupo"] == g, prot] for g in G}
L = {g: np.log2(grp[g]) for g in G}

# 1) Estadística descriptiva por proteína y grupo
desc = pd.DataFrame(index=prot)
for g in G:
    s = grp[g]
    desc[f"media_{g}"] = s.mean(); desc[f"mediana_{g}"] = s.median(); desc[f"DE_{g}"] = s.std()
    desc[f"CV_{g}"] = s.std() / s.mean(); desc[f"min_{g}"] = s.min(); desc[f"max_{g}"] = s.max()
    desc[f"asimetria_{g}"] = s.skew()

# 2) Comparaciones univariadas (Welch sobre log2, Mann-Whitney, FDR de Benjamini-Hochberg)
def comparar(a, b, nombre):
    r = pd.DataFrame(index=prot)
    r[f"log2FC_{nombre}"] = L[a].mean() - L[b].mean()
    r[f"p_welch_{nombre}"] = stats.ttest_ind(L[a], L[b], equal_var=False).pvalue
    r[f"p_mw_{nombre}"] = [stats.mannwhitneyu(grp[a][p], grp[b][p]).pvalue for p in prot]
    r[f"q_welch_{nombre}"] = multipletests(r[f"p_welch_{nombre}"], method="fdr_bh")[1]
    r[f"q_mw_{nombre}"] = multipletests(r[f"p_mw_{nombre}"], method="fdr_bh")[1]
    sd = np.sqrt((L[a].var() + L[b].var()) / 2)
    r[f"d_cohen_{nombre}"] = r[f"log2FC_{nombre}"] / sd
    return r
comp = pd.concat([comparar("C/A", "N/H", "CA_vs_NH"), comparar("C/S", "N/H", "CS_vs_NH"), comparar("C/S", "C/A", "CS_vs_CA")], axis=1)
kw = [stats.kruskal(*[grp[g][p] for g in G]).pvalue for p in prot]
comp["p_kruskal_3grupos"] = kw; comp["q_kruskal_3grupos"] = multipletests(kw, method="fdr_bh")[1]
tabla = pd.concat([desc, comp], axis=1); tabla.index.name = "proteina_spot"
tabla.to_csv(os.path.join(out, "eda_estadisticas_por_proteina.csv"), float_format="%.6g")

# 3) Resúmenes
print("== Distribución, entre las 192 proteínas, de los estadísticos por proteína ==")
q = lambda s: f"mediana {s.median():.2f} (P25–P75 {s.quantile(.25):.2f}–{s.quantile(.75):.2f}; mín {s.min():.2f}; máx {s.max():.2f})"
for g in G:
    print(g, "| media:", q(desc[f"media_{g}"]), "| DE:", q(desc[f"DE_{g}"]), "| CV:", q(desc[f"CV_{g}"]), "| asimetría:", q(desc[f"asimetria_{g}"]))
print("\n== Proteínas con diferencia significativa (de 192) ==")
for n in ["CA_vs_NH", "CS_vs_NH", "CS_vs_CA"]:
    fc = comp[f"log2FC_{n}"]
    print(n, "| Welch p<0.05:", (comp[f"p_welch_{n}"] < .05).sum(), "| Welch q<0.05:", (comp[f"q_welch_{n}"] < .05).sum(),
          "| MW q<0.05:", (comp[f"q_mw_{n}"] < .05).sum(), "| ambos q<0.05:", ((comp[f"q_welch_{n}"] < .05) & (comp[f"q_mw_{n}"] < .05)).sum(),
          "| q<0.05 y |log2FC|>=0.5:", ((comp[f"q_welch_{n}"] < .05) & (fc.abs() >= .5)).sum(),
          "| arriba/abajo (q<0.05):", ((comp[f"q_welch_{n}"] < .05) & (fc > 0)).sum(), "/", ((comp[f"q_welch_{n}"] < .05) & (fc < 0)).sum(),
          "| |log2FC| mediana:", round(fc.abs().median(), 2), "| |d| mediana:", round(comp[f"d_cohen_{n}"].abs().median(), 2))
print("Kruskal-Wallis 3 grupos q<0.05:", (comp["q_kruskal_3grupos"] < .05).sum())
top = comp.sort_values("q_welch_CS_vs_CA").head(12)[["log2FC_CS_vs_CA", "d_cohen_CS_vs_CA", "p_welch_CS_vs_CA", "q_welch_CS_vs_CA", "q_mw_CS_vs_CA"]]
print("\n== 12 proteínas con menor q (C/S vs C/A) =="); print(top.round(4).to_string())
# correlaciones entre proteínas (dentro de cada grupo, en log2)
for g in G:
    c = L[g].corr().values; iu = np.triu_indices_from(c, 1); v = c[iu]
    print(f"correlación entre proteínas {g}: mediana {np.median(v):.3f}, P2.5–P97.5 {np.quantile(v,.025):.2f}–{np.quantile(v,.975):.2f}, |r|>0.7: {(abs(v)>.7).sum()} de {len(v)}")
# normalidad en log2 por proteína y grupo
for g in G:
    pv = np.array([stats.shapiro(L[g][p]).pvalue for p in prot]); print(f"Shapiro-Wilk log2 {g}: rechaza (p<0.05) en {(pv<.05).mean()*100:.1f}% de las proteínas")
print("faltantes:", int(d[prot].isna().sum().sum()), "| valores <= 0:", int((d[prot] <= 0).sum().sum()))

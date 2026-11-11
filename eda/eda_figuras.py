"""Figuras del EDA de las 192 proteínas (Anexo, Figuras A1 a A5).
Uso: python eda/eda_figuras.py data/dataset_sintetico_pbmc.csv eda/eda_estadisticas_por_proteina.csv eda/figuras"""
import os, sys, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.linewidth": .8, "axes.edgecolor": "#444", "xtick.color": "#444", "ytick.color": "#444", "savefig.dpi": 300, "savefig.bbox": "tight"})
OUT = sys.argv[3] if len(sys.argv) > 3 else "."; os.makedirs(OUT, exist_ok=True)
d = pd.read_csv(sys.argv[1]); t = pd.read_csv(sys.argv[2], index_col=0); prot = list(d.columns[:-2]); G = ["N/H", "C/A", "C/S"]
L = np.log2(d[prot]); grupo = d["Grupo"]
GRIS = {"N/H": "#b8b8b8", "C/A": "#767676", "C/S": "#1a1a1a"}; MARC = {"N/H": "o", "C/A": "s", "C/S": "^"}
corto = lambda s: s.replace("_spot", " (spot ") + ")"

# Figura A1: distribución de media y CV por proteína
fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.2))
for a, (col, lab, logy) in zip(ax, [("media", "Media por proteína (unidades arbitrarias)", True), ("CV", "CV por proteína", False)]):
    datos = [t[f"{col}_{g}"].values for g in G]
    bp = a.boxplot(datos, widths=.5, patch_artist=True, showfliers=False, medianprops=dict(color="white", lw=1.6))
    for b, g in zip(bp["boxes"], G): b.set(facecolor=GRIS[g], edgecolor="#333", lw=.8)
    rng = np.random.default_rng(0)
    for i, (v, g) in enumerate(zip(datos, G), 1):
        a.scatter(i + rng.uniform(-.2, .2, len(v)), v, s=5, color="#000", alpha=.25, lw=0, zorder=3)
    a.set_xticks([1, 2, 3], G); a.set_ylabel(lab); a.grid(axis="y", color="#e5e5e5", lw=.6); a.set_axisbelow(True)
    if logy: a.set_yscale("log"); a.set_yticks([25, 50, 100, 200, 400, 800], ["25", "50", "100", "200", "400", "800"]); a.minorticks_off()
for g, y in zip(G, [.49, .67, .77]): ax[1].plot([G.index(g) + .65, G.index(g) + 1.35], [y, y], color="#000", lw=1, ls=(0, (4, 2)))
ax[1].text(3.42, .77, "CV nominal", fontsize=7.5, va="center", ha="left", color="#333")
ax[0].set_title("A", loc="left", fontweight="bold"); ax[1].set_title("B", loc="left", fontweight="bold")
fig.tight_layout(); fig.savefig(OUT + "/eda_fig_A1_distribucion.png"); plt.close(fig)

# Figura A2: volcanes
fig, ax = plt.subplots(1, 3, figsize=(7.2, 3.1), sharex=True, sharey=True)
for a, (n, tit) in zip(ax, [("CA_vs_NH", "C/A vs. N/H"), ("CS_vs_NH", "C/S vs. N/H"), ("CS_vs_CA", "C/S vs. C/A")]):
    fc, p, q = t[f"log2FC_{n}"], t[f"p_welch_{n}"], t[f"q_welch_{n}"]; s = q < .05
    a.scatter(fc[~s], -np.log10(p[~s]), s=11, facecolor="white", edgecolor="#8a8a8a", lw=.7)
    a.scatter(fc[s], -np.log10(p[s]), s=11, color="#1a1a1a", lw=0)
    a.axvline(0, color="#bbb", lw=.6, zorder=0); a.set_title(f"{tit}\n{int(s.sum())} de 192 con q < 0.05", fontsize=9)
    a.set_xlabel("log2 (cociente de medias)"); a.grid(color="#eee", lw=.5); a.set_axisbelow(True)
ax[0].set_ylabel("−log10 (p)")
ax[2].scatter([], [], s=11, color="#1a1a1a", label="q < 0.05"); ax[2].scatter([], [], s=11, facecolor="white", edgecolor="#8a8a8a", lw=.7, label="q ≥ 0.05")
ax[2].legend(frameon=False, fontsize=7.5, loc="upper right", handletextpad=.2)
fig.tight_layout(); fig.savefig(OUT + "/eda_fig_A2_volcanes.png"); plt.close(fig)

# Figura A3: mapa de calor (z por proteína respecto de N/H, en log2)
ref = L[grupo == "N/H"]; Z = (L - ref.mean()) / ref.std()
orden_p = t["log2FC_CS_vs_NH"].sort_values().index; orden_pac = np.concatenate([np.where(grupo == g)[0] for g in G])
M = Z.loc[orden_pac, orden_p].T.values
cmap = LinearSegmentedColormap.from_list("div", ["#2166ac", "#9ec3e0", "#eeeeee", "#f0a58a", "#b2182b"])
fig, a = plt.subplots(figsize=(7.2, 5.2))
im = a.imshow(M, aspect="auto", cmap=cmap, vmin=-4, vmax=4, interpolation="nearest")
lim = np.cumsum([(grupo == g).sum() for g in G])
for x in lim[:-1]: a.axvline(x - .5, color="white", lw=2.5)
a.set_xticks([lim[0] / 2 - .5, (lim[0] + lim[1]) / 2 - .5, (lim[1] + lim[2]) / 2 - .5], [f"{g} (n = {(grupo == g).sum()})" for g in G]); a.tick_params(axis="x", length=0)
a.set_yticks([]); a.set_ylabel("192 proteínas (ordenadas por log2 del cociente C/S vs. N/H)")
for s in a.spines.values(): s.set_visible(False)
cb = fig.colorbar(im, ax=a, fraction=.03, pad=.02, extend="both"); cb.set_label("Abundancia estandarizada (z respecto de N/H, log2)"); cb.outline.set_visible(False)
fig.tight_layout(); fig.savefig(OUT + "/eda_fig_A3_heatmap.png"); plt.close(fig)

# Figura A4: 12 proteínas con menor q en C/S vs. C/A
top = t.sort_values("q_welch_CS_vs_CA").head(12).index
fig, axs = plt.subplots(3, 4, figsize=(7.2, 6.3), sharex=True)
rng = np.random.default_rng(1)
for a, p in zip(axs.ravel(), top):
    datos = [L.loc[grupo == g, p].values for g in G]
    bp = a.boxplot(datos, widths=.55, patch_artist=True, showfliers=False, medianprops=dict(color="white", lw=1.5))
    for b, g in zip(bp["boxes"], G): b.set(facecolor=GRIS[g], edgecolor="#333", lw=.7)
    for i, v in enumerate(datos, 1): a.scatter(i + rng.uniform(-.18, .18, len(v)), v, s=4, color="#000", alpha=.35, lw=0, zorder=3)
    nombre, spot = p.split("_spot"); nombre = nombre if len(nombre) <= 30 else nombre[:28] + "…"
    a.set_title(f"{nombre}\nspot {spot} · q = {t.loc[p, 'q_welch_CS_vs_CA']:.3f}", fontsize=7.2); a.set_xticks([1, 2, 3], G)
    a.grid(axis="y", color="#e8e8e8", lw=.5); a.set_axisbelow(True); a.tick_params(labelsize=7.5)
for a in axs[:, 0]: a.set_ylabel("log2 (abundancia)", fontsize=8)
fig.tight_layout(); fig.savefig(OUT + "/eda_fig_A4_boxplots_top12.png"); plt.close(fig)

# Figura A5: PCA sobre log2 estandarizado
X = StandardScaler().fit_transform(L); pca = PCA(n_components=2, random_state=42); C = pca.fit_transform(X)
fig, a = plt.subplots(figsize=(4.6, 3.8))
for g in G:
    f = (grupo == g).values; a.scatter(C[f, 0], C[f, 1], s=26, marker=MARC[g], color=GRIS[g], edgecolor="white", lw=.6, label=g)
a.set_xlabel(f"Componente 1 ({pca.explained_variance_ratio_[0]*100:.1f}%)"); a.set_ylabel(f"Componente 2 ({pca.explained_variance_ratio_[1]*100:.1f}%)")
a.legend(frameon=False, title="Grupo"); a.grid(color="#eee", lw=.5); a.set_axisbelow(True)
fig.tight_layout(); fig.savefig(OUT + "/eda_fig_A5_pca_estandarizado.png"); plt.close(fig)
print("PCA var:", pca.explained_variance_ratio_.round(3), "| z fuera de ±4:", round((abs(M) > 4).mean() * 100, 2), "%")

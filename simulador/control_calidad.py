import os, sys, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from simulador_completo import verdad, generar, N_NULAS, BLOQUE

ruta = sys.argv[1]
salida = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")
os.makedirs(salida, exist_ok=True)
mu_ca, delta, es_verdad = verdad(ruta)
mu = np.concatenate([mu_ca, np.zeros(N_NULAS)]); d = np.concatenate([delta, np.zeros(N_NULAS)]); p = len(mu)
rng = np.random.default_rng(1)
bloques = rng.permutation(p) // BLOQUE
nula = np.arange(p) >= len(mu_ca)

X, y = generar(rng, 1000, mu, d, 0.67, 0.5, bloques, 0)
C = np.corrcoef(X.T); iu = np.triu_indices(p, 1); mismo = (bloques[:, None] == bloques[None, :])[iu]
print(f"proteínas: {p} | verdaderas: {es_verdad.sum()} | débiles: {(~es_verdad).sum()} | nulas: {N_NULAS}")
print(f"correlación media intrabloque: {C[iu][mismo].mean():.2f} (teórico 0.5) | entre bloques: {C[iu][~mismo].mean():.2f}")
print(f"diferencia media C/S - C/A en nulas (log2): {X[y == 1][:, nula].mean() - X[y == 0][:, nula].mean():.3f}")
print(f"pares con |r| > 0.9: {(np.abs(C[iu]) > 0.9).sum()} de {len(iu[0])}")

cv = 0.67; sigma = np.sqrt(np.log(1 + cv**2)) / np.log(2)
L, _ = generar(rng, 2000, mu, np.zeros(p), cv, 0.3, bloques, 0)
Z = (L - mu) / sigma
ks = np.mean([stats.kstest(Z[:, j], "norm").pvalue < .05 for j in range(p)])
sw = np.mean([stats.shapiro(L[:, j]).pvalue < .05 for j in range(p)])
O = 2.0 ** L; cvo = O.std(0, ddof=1) / O.mean(0)
print(f"rechazo de normalidad en log2 (p < 0.05): Kolmogorov-Smirnov {ks:.1%} | Shapiro-Wilk {sw:.1%}")
print(f"CV en escala original: mediana {np.median(cvo):.3f} (nominal {cv}); P2.5-P97.5 {np.percentile(cvo, 2.5):.3f}-{np.percentile(cvo, 97.5):.3f}")
print(f"asimetría: escala original {np.median(stats.skew(O)):.2f} | log2 {np.median(stats.skew(L)):.2f}")

plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": 200, "savefig.bbox": "tight"})
fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.2))
zs = (L - L.mean(0)) / L.std(0, ddof=1); q = np.sort(zs[:, rng.choice(p, 50, replace=False)].ravel())
teo = stats.norm.ppf((np.arange(1, len(q) + 1) - .5) / len(q)); k = np.linspace(0, len(q) - 1, 400).astype(int)
ax[0].plot(teo[k], q[k], "o", ms=2.5, color="0.35"); ax[0].plot([-4, 4], [-4, 4], color="black", lw=.8)
ax[0].set_title("A. Gráfico Q-Q"); ax[0].set_xlabel("Cuantiles teóricos (normal)"); ax[0].set_ylabel("Cuantiles observados (log2)")
j = int(np.argmin(np.abs(mu))); v = 100 * O[:, j]; m = 100 * 2.0 ** mu[j] * np.exp(sigma**2 * np.log(2)**2 / 2)
tope = np.percentile(v, 99.5); ax[1].hist(v[v <= tope], bins=40, density=True, color="0.8", edgecolor="black", lw=.4)
xs = np.linspace(1e-3, tope, 300); s2 = np.log(1 + cv**2)
ax[1].plot(xs, stats.lognorm.pdf(xs, np.sqrt(s2), scale=np.exp(np.log(m) - s2 / 2)), color="black")
ax[1].set_title("B. Una proteína simulada"); ax[1].set_xlabel("Abundancia (escala original)"); ax[1].set_ylabel("Densidad")
fig.tight_layout(); fig.savefig(os.path.join(salida, "figura11.png")); plt.close(fig)

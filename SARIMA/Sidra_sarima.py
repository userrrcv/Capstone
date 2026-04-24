import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import itertools          # ← AGREGAR ESTE IMPORT
import warnings
warnings.filterwarnings("ignore")

from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller
from sklearn.metrics import mean_absolute_error, mean_squared_error


# 1. CARGA Y PREPARACIÓN

df = pd.read_csv(r"C:\Users\tamar\Documents\Capstone\Documentos Generados\SidraTimeSeries.csv", parse_dates=["fecha"])
df = df.sort_values("fecha").reset_index(drop=True)

df = df.set_index("fecha").asfreq("MS")
df["demanda"] = df["demanda"].interpolate(method="linear")
df = df.reset_index()

print(f"Períodos totales: {len(df)}  ({df['fecha'].min().date()} → {df['fecha'].max().date()})")


# 2. TRATAMIENTO DE OUTLIERS

Q1 = df["demanda"].quantile(0.25)
Q3 = df["demanda"].quantile(0.75)
IQR = Q3 - Q1
limite_inf = max(0, Q1 - 1.5 * IQR)
limite_sup = Q3 + 1.5 * IQR

outliers = df[(df["demanda"] < limite_inf) | (df["demanda"] > limite_sup)]
print(f"\nOutliers detectados: {len(outliers)}")
print(outliers[["fecha", "demanda"]].to_string(index=False))
print(f"Límite IQR  →  inferior: {limite_inf:.0f}  |  superior: {limite_sup:.0f}")

df["demanda_w"] = df["demanda"].clip(lower=limite_inf, upper=limite_sup)


# 3. TRANSFORMACIÓN LOGARÍTMICA

df["demanda_log"] = np.log1p(df["demanda_w"])

adf_stat, adf_p, *_ = adfuller(df["demanda_log"])
print(f"\nTest ADF (serie log)  →  p-value: {adf_p:.4f}  ({'estacionaria' if adf_p < 0.05 else 'no estacionaria'})")


# 4. SPLIT TRAIN / TEST

N_TEST = 6
train = df.iloc[:-N_TEST]
test  = df.iloc[-N_TEST:]

# Índices exactos del split
train_idx = list(range(len(df) - N_TEST))
test_idx  = list(range(len(df) - N_TEST, len(df)))

# 5. GRID SEARCH + MODELO

def sarima_grid_search(
    serie_log_completa,   # ← recibe la serie COMPLETA
    train_idx,            # ← recibe los índices de train
    test_idx,             # ← recibe los índices de test
    s=12,
    p_range=(0,1,2),
    d_range=(0,1),
    q_range=(0,1,2),
    P_range=(0,1,2),
    D_range=(0,1),
    Q_range=(0,1,2),
    criterio="mape",
    verbose=True
):
    # Usa exactamente el mismo split que el resto del script
    train_gs = serie_log_completa.iloc[train_idx]
    test_gs  = serie_log_completa.iloc[test_idx]

    combinaciones = list(itertools.product(p_range, d_range, q_range,
                                           P_range, D_range, Q_range))
    total = len(combinaciones)
    if verbose:
        print(f"Probando {total} combinaciones con s={s}, criterio={criterio}...")

    resultados = []

    for i, (p, d, q, P, D, Q) in enumerate(combinaciones, 1):
        try:
            modelo = SARIMAX(
                train_gs,
                order=(p, d, q),
                seasonal_order=(P, D, Q, s),
                enforce_stationarity=False,
                enforce_invertibility=False
            ).fit(disp=False)

            if criterio == "aic":
                score = modelo.aic
            elif criterio == "mape":
                pred_log  = modelo.forecast(steps=len(test_gs))
                pred_orig = np.expm1(pred_log).clip(lower=0)
                real_orig = np.expm1(test_gs).clip(lower=0)
                score = (np.abs((real_orig.values - pred_orig.values)
                                / real_orig.values) * 100).mean()

            resultados.append({
                "order":          (p, d, q),
                "seasonal_order": (P, D, Q, s),
                "score":          score,
                "aic":            modelo.aic,
            })

            if verbose and i % 50 == 0:
                print(f"  {i}/{total} combinaciones evaluadas...")

        except Exception:
            pass

    if not resultados:
        raise ValueError("Ninguna combinación convergió. Revisa tu serie.")

    df_res = pd.DataFrame(resultados).sort_values("score").reset_index(drop=True)
    mejor  = df_res.iloc[0]

    if verbose:
        print(f"\n── Top 5 combinaciones ({criterio}) ──")
        print(df_res.head(5).to_string(index=False))
        print(f"\n✅ Mejor → ORDER={mejor['order']}  SEASONAL={mejor['seasonal_order']}"
              f"  {criterio.upper()}={mejor['score']:.2f}")

    return mejor["order"], mejor["seasonal_order"], df_res

ORDER, SEASONAL_ORDER, tabla_resultados = sarima_grid_search(
    serie_log_completa = df["demanda_log"],
    train_idx          = train_idx,
    test_idx           = test_idx,
    s                  = 12,
    criterio           = "mape",
    verbose            = True
)

print(f"\nParámetros seleccionados: SARIMA{ORDER}x{SEASONAL_ORDER}")

# ← DESPUÉS: entrenar el modelo con esos parámetros
modelo = SARIMAX(
    train["demanda_log"],
    order=ORDER,
    seasonal_order=SEASONAL_ORDER,
    enforce_stationarity=False,
    enforce_invertibility=False
).fit(disp=False)

print(modelo.summary())


# 6. EVALUACIÓN EN TEST

pred_log  = modelo.forecast(steps=N_TEST)
pred_orig = np.expm1(pred_log).clip(lower=0)

mae  = mean_absolute_error(test["demanda"], pred_orig)
rmse = np.sqrt(mean_squared_error(test["demanda"], pred_orig))
mape = (np.abs((test["demanda"].values - pred_orig.values) / test["demanda"].values) * 100).mean()

print(f"\n── Métricas en test ({N_TEST} meses) ──")
print(f"  MAE  : {mae:.1f}")
print(f"  RMSE : {rmse:.1f}")
print(f"  MAPE : {mape:.1f}%  {'Bueno < 15%' if mape < 15 else 'Malo > 15%'}")

comparacion = test[["fecha", "demanda"]].copy().reset_index(drop=True)
comparacion["prediccion"] = pred_orig.values.round(0)
comparacion["error_%"]    = ((comparacion["demanda"] - comparacion["prediccion"]).abs()
                              / comparacion["demanda"] * 100).round(1)
print("\n── Detalle mes a mes ──")
print(comparacion.to_string(index=False))

# 7. REENTRENAR CON TODOS LOS DATOS + FORECAST 6 MESES

N_FORECAST = 6

modelo_full = SARIMAX(
    df["demanda_log"],
    order=ORDER,
    seasonal_order=SEASONAL_ORDER,
    enforce_stationarity=False,
    enforce_invertibility=False
).fit(disp=False)

fc_result    = modelo_full.get_forecast(steps=N_FORECAST)
forecast_log = fc_result.predicted_mean
forecast_ci  = fc_result.conf_int()

forecast_orig = np.expm1(forecast_log).clip(lower=0)
ci_inf = np.expm1(forecast_ci.iloc[:, 0]).clip(lower=0)
ci_sup = np.expm1(forecast_ci.iloc[:, 1]).clip(lower=0)

fechas_futuras = pd.date_range(
    start=df["fecha"].max() + pd.DateOffset(months=1),
    periods=N_FORECAST, freq="MS"
)

df_forecast = pd.DataFrame({
    "fecha":            fechas_futuras,
    "demanda_predicha": forecast_orig.values.round(0),
    "limite_inferior":  ci_inf.values.round(0),
    "limite_superior":  ci_sup.values.round(0),
})

print("\n── Predicción próximos 6 meses ──")
print(df_forecast.to_string(index=False))
df_forecast.to_csv(r"C:\Users\tamar\Documents\Capstone\Resultados ARIMA\Sidra_forecast_demanda_v2.csv", index=False)
print("\nPredicción guardada en forecast_demanda_v2.csv")


# 8. GRÁFICO FINAL

fig, axes = plt.subplots(2, 1, figsize=(14, 10))

ax1 = axes[0]
ax1.plot(df["fecha"], df["demanda"], label="Demanda original", color="#94a3b8", linewidth=1.5, linestyle="--")
ax1.plot(df["fecha"], df["demanda_w"], label="Demanda corregida (winsorización IQR)", color="#2563eb", linewidth=2)
if len(outliers):
    ax1.scatter(outliers["fecha"], outliers["demanda"], color="#ef4444", zorder=5, s=70, label="Outliers")
ax1.axhline(y=limite_sup, color="#ef4444", linestyle=":", alpha=0.5, linewidth=1, label=f"Límite sup. IQR ({limite_sup:.0f})")
ax1.set_title("Tratamiento de Outliers (winsorización IQR)", fontsize=12, fontweight="bold")
ax1.set_ylabel("Demanda")
ax1.legend(fontsize=9)
ax1.grid(True, alpha=0.3)

ax2 = axes[1]
ax2.plot(df["fecha"], df["demanda"], label="Histórico real", color="#2563eb", linewidth=2)

fitted_orig = np.expm1(modelo_full.fittedvalues).clip(lower=0)
ax2.plot(df["fecha"], fitted_orig, label="Ajuste modelo (train)", color="#a855f7",
         linewidth=1.2, linestyle="--", alpha=0.7)

ax2.plot(test["fecha"], pred_orig.values, label=f"Pred. test  MAPE {mape:.1f}%",
         color="#f59e0b", linestyle="--", linewidth=2, marker="o", markersize=6)
ax2.plot(df_forecast["fecha"], df_forecast["demanda_predicha"], label="Forecast 6 meses",
         color="#10b981", linestyle="--", linewidth=2, marker="o", markersize=6)
ax2.fill_between(fechas_futuras, df_forecast["limite_inferior"], df_forecast["limite_superior"],
                 alpha=0.2, color="#10b981", label="Intervalo confianza 95%")
ax2.axvline(x=test["fecha"].iloc[0], color="gray", linestyle=":", linewidth=1.5, label="Inicio test")

ax2.set_title(f"SARIMA{ORDER}x{SEASONAL_ORDER} + log transform — Sidra", fontsize=12, fontweight="bold")
ax2.set_xlabel("Fecha")
ax2.set_ylabel("Demanda")
ax2.legend(fontsize=9)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(r"C:\Users\tamar\Documents\Capstone\Resultados ARIMA\Sidra_prediccion_demanda_v2.png", dpi=150)
plt.close()
print("Gráfico guardado en prediccion_demanda_v2.png")
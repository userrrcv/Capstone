import pandas as pd
import os

# ─────────────────────────────────────────────
# CARGA DE DATOS    
# ─────────────────────────────────────────────
ARCHIVO_VENTAS = r"C:\Users\tamar\OneDrive\Documentos\Capstone\ventasSemanales.csv"
PRODUCTOS      = [105302070, 63630175, 219140001, 181913006, 281670015]  # ← IDs de productos
CARPETA_SALIDA = r"C:\Users\tamar\Documents\Capstone\Documentos Generados Semanales"
# ─────────────────────────────────────────────

df = pd.read_csv(ARCHIVO_VENTAS)
df["Semana"]   = pd.to_datetime(df["Semana"])
df["Producto"] = df["Producto"].astype(float)

productos_disponibles = sorted(df["Producto"].astype(int).unique().tolist())

for producto_id in PRODUCTOS:
    df_prod = df[df["Producto"] == float(producto_id)].copy()

    if df_prod.empty:
        print(f"Producto {producto_id} no encontrado — saltando.")
        print(f"   Disponibles: {productos_disponibles[:10]} ...")
        continue

    # Negativos → 0
    df_prod["Demanda"] = df_prod["Demanda"].clip(lower=0)

    # Sumar todas las sucursales por semana y rellenar huecos con 0
    semanas = pd.date_range(df_prod["Semana"].min(), df_prod["Semana"].max(), freq="W-MON")
    df_ts = df_prod.groupby("Semana")["Demanda"].sum().reset_index()
    df_ts = df_ts.set_index("Semana").reindex(semanas).fillna(0).reset_index()
    df_ts.columns = ["Fecha", "Demanda"]

    salida = os.path.join(CARPETA_SALIDA, f"Producto_{producto_id}_semanal.csv")
    df_ts.to_csv(salida, index=False)
    print(f"Producto {producto_id} — {len(df_ts)} semanas — Guardado: {salida}")

    salida2 = os.path.join(CARPETA_SALIDA, f"Producto_{producto_id}_semanal.xlsx")
    df_ts.to_excel(salida2, index=False)
    print(f"Producto {producto_id} — {len(df_ts)} semanas — Guardado: {salida2}")
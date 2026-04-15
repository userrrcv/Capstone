import pandas as pd

# =====================================
# CONFIGURACIÓN
# =====================================
producto_objetivo = "105302070"

ruta_archivo = r"C:\Users\tamar\OneDrive\Documentos\Python\Capstone\Ventas_mensuales.csv"

ruta_salida_csv = r"C:\Users\tamar\OneDrive\Documentos\Python\Capstone\Documentos Generados\Producto_filtrado_vino.csv"
ruta_serie_csv = r"C:\Users\tamar\OneDrive\Documentos\Python\Capstone\Documentos Generados\Serie_temporal_vino.csv"
ruta_salida_excel = r"C:\Users\tamar\OneDrive\Documentos\Python\Capstone\Documentos Generados\Producto_filtrado_vino.xlsx"


# =====================================
# 1. CARGAR DATOS
# =====================================
df = pd.read_csv(ruta_archivo)

print("Dataset cargado")
print(df.head())


# =====================================
# 2. LIMPIEZA DE DATOS
# =====================================
df["Producto"] = pd.to_numeric(df["Producto"], errors="coerce")
df = df.dropna(subset=["Producto"])
df["Producto"] = df["Producto"].astype(int).astype(str)


# =====================================
# 3. FILTRAR PRODUCTO
# =====================================
df_producto = df[df["Producto"] == producto_objetivo].copy()

print(f"\nDatos filtrados para producto: {producto_objetivo}")
print(df_producto.head())


# =====================================
# 4. FORMATO DE FECHA
# =====================================
df_producto["Mes"] = pd.to_datetime(df_producto["Mes"])

# ordenar por fecha
df_producto = df_producto.sort_values("Mes")


# =====================================
# 5. CREAR SERIE TEMPORAL
# =====================================
serie = df_producto.groupby("Mes")["Demanda"].sum().reset_index()

# convertir a índice temporal
serie = serie.set_index("Mes")


# =====================================
# 6. ASEGURAR FRECUENCIA MENSUAL
# =====================================
serie = serie.asfreq('MS')  # MS = inicio de mes

# rellenar meses faltantes (importante)
serie["Demanda"] = serie["Demanda"].fillna(0)


print("\nSerie temporal lista para modelos:")
print(serie.head())


# =====================================
# 7. GUARDAR ARCHIVOS
# =====================================

# dataset completo del producto
df_producto.to_csv(ruta_salida_csv, index=False, encoding="utf-8")

# serie temporal (principal)
serie.to_csv(ruta_serie_csv, encoding="utf-8")

# excel con ambas hojas
with pd.ExcelWriter(ruta_salida_excel) as writer:
    df_producto.to_excel(writer, sheet_name="Datos Producto", index=False)
    serie.to_excel(writer, sheet_name="Serie Temporal")

print("\nArchivos guardados correctamente")


# =====================================
# 8. RESUMEN
# =====================================
print("\nResumen:")
print(f"Total registros: {len(df_producto)}")
print(f"Demanda total: {df_producto['Demanda'].sum()}")
print(f"Promedio: {df_producto['Demanda'].mean():.2f}")


# =====================================
# 9. (OPCIONAL) FEATURES PARA ML / XGBOOST
# =====================================
# Esto te deja listo para machine learning

serie_ml = serie.copy()

# Lags (muy importante)
serie_ml["lag_1"] = serie_ml["Demanda"].shift(1)
serie_ml["lag_2"] = serie_ml["Demanda"].shift(2)
serie_ml["lag_3"] = serie_ml["Demanda"].shift(3)

# Promedios móviles
serie_ml["rolling_3"] = serie_ml["Demanda"].rolling(3).mean()
serie_ml["rolling_6"] = serie_ml["Demanda"].rolling(6).mean()

# eliminar nulos generados por lag
serie_ml = serie_ml.dropna()

# guardar dataset para ML
ruta_ml = r"C:\Users\tamar\OneDrive\Documentos\Python\Capstone\Documentos Generados\Serie_ML_vino.csv"
serie_ml.to_csv(ruta_ml)

print("\nDataset listo para Machine Learning guardado")

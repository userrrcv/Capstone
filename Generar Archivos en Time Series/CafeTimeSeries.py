import pandas as pd

INPUT_FILE = r"C:\Users\tamar\Documents\Capstone\Documentos Generados\CafeBelen_Limpio.xlsx"
OUTPUT_FILE = r"C:\Users\tamar\Documents\Capstone\Documentos Generados\CafeBelenTimeSeries.csv"

df = pd.read_excel(INPUT_FILE, sheet_name="Serie Temporal", header=0)
df.columns = ["fecha", "demanda_original", "demanda_limpia", "diferencia"]
df["fecha"] = pd.to_datetime(df["fecha"])

# Usar demanda_limpia si existe, si no usar demanda_original
df["demanda"] = df["demanda_limpia"].combine_first(df["demanda_original"])

# Filtrar filas con demanda nula o negativa
df = df[df["demanda"] > 0].sort_values("fecha").reset_index(drop=True)

result = df[["fecha", "demanda"]].copy()

result.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

print(f"Archivo generado: {OUTPUT_FILE} — {len(result)} períodos")
print(result.to_string(index=False))
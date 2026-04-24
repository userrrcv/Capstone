import pandas as pd

INPUT_FILE = "CafeBelen_Limpio.xlsx"
OUTPUT_FILE = "timeseries_demanda.xlsx"

df = pd.read_excel(INPUT_FILE, sheet_name="Serie Temporal", header=0)
df.columns = ["fecha", "demanda_original", "demanda_limpia", "diferencia"]
df["fecha"] = pd.to_datetime(df["fecha"])

# Usar demanda_limpia si existe, si no usar demanda_original
df["demanda"] = df["demanda_limpia"].combine_first(df["demanda_original"])

# Filtrar filas con demanda nula o negativa
df = df[df["demanda"] > 0].sort_values("fecha").reset_index(drop=True)

result = df[["fecha", "demanda"]].copy()

with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl", datetime_format="YYYY-MM-DD") as writer:
    result.to_excel(writer, sheet_name="Serie_Temporal", index=False)

print(f"✅ Archivo generado: {OUTPUT_FILE} — {len(result)} períodos")
print(result.to_string(index=False))

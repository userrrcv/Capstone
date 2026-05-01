import pandas as pd
from pyxlsb import open_workbook

print("Script iniciado")

archivo = r"C:\Users\tamar\OneDrive\Documentos\Capstone\Sell In Biggie por dia.xlsb"

# meses en español → inglés
meses = {
    "Enero": "January", "Febrero": "February", "Marzo": "March",
    "Abril": "April", "Mayo": "May", "Junio": "June",
    "Julio": "July", "Agosto": "August", "Septiembre": "September",
    "Octubre": "October", "Noviembre": "November", "Diciembre": "December"
}

# Leer las primeras 3 filas para construir columnas
fila_año = []
fila_mes = []
fila_header = []

with open_workbook(archivo) as wb:
    with wb.get_sheet(1) as ws:
        for i, row in enumerate(ws.rows()):
            vals = [c.v for c in row]
            if i == 0:
                fila_año = vals
            elif i == 1:
                fila_mes = vals
            elif i == 2:
                fila_header = vals
                break

print("Archivo leído")

# Construir columnas
columnas = []
for i in range(len(fila_header)):
    if i < 3:
        columnas.append(str(fila_header[i]).strip() if fila_header[i] is not None else f"col_{i}")
    else:
        try:
            año = str(fila_año[i]).strip() if fila_año[i] is not None else ""
            mes = str(fila_mes[i]).strip() if fila_mes[i] is not None else ""
            dia = str(fila_header[i]).strip() if fila_header[i] is not None else ""

            # saltar columnas de totales
            if "Total" in año or "Total" in mes or not dia.replace(".", "").isdigit():
                columnas.append(None)
                continue

            dia_int = int(float(dia))
            mes_en = meses.get(mes, mes)
            año_int = int(float(año))

            fecha = pd.to_datetime(f"{dia_int} {mes_en} {año_int}", dayfirst=True, errors="coerce")
            columnas.append(fecha)
        except:
            columnas.append(None)

print("Columnas listas")

# Índices de columnas de fecha válidas
date_indices = [
    (i, columnas[i]) for i in range(3, len(columnas))
    if columnas[i] is not None and columnas[i] is not pd.NaT
]

# Leer datos en streaming (sin cargar todo en memoria)
records = []

with open_workbook(archivo) as wb:
    with wb.get_sheet(1) as ws:
        for row_idx, row in enumerate(ws.rows()):
            if row_idx < 3:
                continue

            vals = [c.v for c in row]

            cliente = vals[0] if len(vals) > 0 else None
            producto = vals[1] if len(vals) > 1 else None
            desc = vals[2] if len(vals) > 2 else None

            # eliminar filas de totales
            if cliente is None or "Total" in str(cliente):
                continue

            for col_idx, fecha in date_indices:
                if col_idx >= len(vals):
                    continue
                val = vals[col_idx]
                if val is None:
                    continue
                try:
                    demanda = float(val)
                except:
                    continue

                records.append({
                    "NomClienteAlter": str(cliente).strip(),
                    "Producto": producto,
                    "Producto Desc": desc,
                    "Fecha": fecha,
                    "Demanda": demanda
                })

print("Time series lista")

df_long = pd.DataFrame(records)

# eliminar filas de totales en descripción
df_long = df_long[~df_long["Producto Desc"].astype(str).str.contains("Total", na=False)]

# eliminar nulos
df_long = df_long.dropna(subset=["Demanda", "Fecha"])

#CREAR COLUMNA SEMANA
df_long["Semana"] = df_long["Fecha"].dt.to_period("W")  # semanas lunes→domingo

#AGRUPAR POR SEMANA
df_semanal = df_long.groupby(
    ["NomClienteAlter", "Producto", "Producto Desc", "Semana"]
)["Demanda"].sum().reset_index()

print("Dataset semanal listo")
print(df_semanal.head())

# Convertir Semana a fecha (inicio de semana = lunes)
df_semanal["Semana"] = df_semanal["Semana"].dt.to_timestamp()

# Guardar
salida_csv = r"C:\Users\tamar\OneDrive\Documentos\Capstone\ventasSemanales.csv"

df_semanal.to_csv(salida_csv, index=False)

print("Archivos guardados:")
print(salida_csv)
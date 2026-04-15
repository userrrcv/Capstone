import pandas as pd

print("Script iniciado")

archivo = r"G:\My Drive\A capstone Clari\Datos Documentos Excel\Documentos 2021-2026\Ventas_mensuales.csv"

# leer todo sin header
df_raw = pd.read_csv(archivo, header=None)

print("Archivo leído")

#filas clave donde se encuentran divididas las fechas 
fila_año = df_raw.iloc[0]
fila_mes = df_raw.iloc[1]
fila_header = df_raw.iloc[2]

#diccionario de meses
meses = {
    "Enero": "January",
    "Febrero": "February",
    "Marzo": "March",
    "Abril": "April",
    "Mayo": "May",
    "Junio": "June",
    "Julio": "July",
    "Agosto": "August",
    "Septiembre": "September",
    "Octubre": "October",
    "Noviembre": "November",
    "Diciembre": "December"
}

#construir columna de fecha 
columnas = []

for i in range(len(df_raw.columns)):

    if i < 3:
        columnas.append(str(fila_header[i]).strip())
    else:
        try:
            año = str(fila_año[i]).strip()
            mes = str(fila_mes[i]).strip()
            dia = str(fila_header[i]).strip()

            # traducir mes
            mes_en = meses.get(mes, mes)

            fecha = pd.to_datetime(
                f"{dia} {mes_en} {año}",
                dayfirst=True,
                errors="coerce"
            )

            columnas.append(fecha)

        except:
            columnas.append(pd.NaT)

# crear dataframe limpio
df = df_raw.iloc[3:].copy()
df.columns = columnas

print("Columnas asignadas correctamente")

#columnas base
base = df.columns[:3].tolist()
print("Columnas base:", base)

#columnas de fechas
cols = df.columns[3:]

print("Total columnas de fechas:", len(cols))

#convertir a formato largo
df_long = df.melt(
    id_vars=base,
    value_vars=cols,
    var_name="Fecha",
    value_name="Demanda"
)

#convertir demanda a número
df_long["Demanda"] = pd.to_numeric(df_long["Demanda"], errors="coerce")

# DEBUG (IMPORTANTE)
print("Total filas:", len(df_long))
print("NaN en Fecha:", df_long["Fecha"].isna().sum())
print("NaN en Demanda:", df_long["Demanda"].isna().sum())

# eliminar demanda nula
df_long = df_long.dropna(subset=["Demanda"])

# ahora sí eliminar fechas inválidas
df_long = df_long.dropna(subset=["Fecha"])

# ordenar
df_long = df_long.sort_values(by=base + ["Fecha"])

print("Dataset listo")
print(df_long.head())

# guardar
salida = r"C:\Users\tamar\OneDrive\Documentos\Python\Capstone\Documentos Generados\Productos2021-2026Format.csv"
salida2 = r"C:\Users\tamar\OneDrive\Documentos\Python\Capstone\Documentos Generados\Productos2021-2026Format.xlsx"
df_long.to_csv(salida, index=False)
df_long.to_excel(salida2, index=False)

print("Archivo guardado:", salida)
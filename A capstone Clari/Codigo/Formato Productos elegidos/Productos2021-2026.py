# import pandas as pd
# import numpy as np


# #Cargar dataset

# df = pd.read_csv(r"C:\Users\tamar\OneDrive\Documentos\Python\Capstone\Ventas_mensuales.csv")
# print("Primeras filas del dataset:")
# print(df.head())

# # Cambiar formato de la fecha

# df["Fecha"] = pd.to_datetime(df["Fecha"])
# df["Mes"] = df["Fecha"].dt.to_period("M")

# #Demanda mensual por producto

# monthly = df.groupby(["Producto", "Mes"])["Demanda"].sum().reset_index()

# print("\nDatos mensuales:")
# print(monthly.head())

# #Calcular métricas

# def calculate_metrics(group):

#     mean_demand = group["Demanda"].mean()
#     std_demand = group["Demanda"].std()

#     if mean_demand == 0:
#         cv = np.nan
#     else:
#         cv = std_demand / mean_demand

#     zero_months = (group["Demanda"] == 0).sum()
#     total_months = len(group)

#     zero_ratio = zero_months / total_months

#     total_demand = group["Demanda"].sum()

#     return pd.Series({
#         "mean_demand": mean_demand,
#         "std_demand": std_demand,
#         "cv": cv,
#         "zero_ratio": zero_ratio,
#         "total_demand": total_demand
#     })

# product_metrics = monthly.groupby("Producto").apply(calculate_metrics).reset_index()

# #Clasificar tipo de demanda

# def classify_demand(row):

#     if row["zero_ratio"] > 0.4:
#         return "Intermittent"

#     elif row["cv"] < 0.5:
#         return "Stable"

#     elif row["cv"] < 1:
#         return "Moderate variability"

#     else:
#         return "Highly variable"

# product_metrics["Demand_Type"] = product_metrics.apply(classify_demand, axis=1)


# #Ordenar productos

# product_metrics = product_metrics.sort_values(
#     by="total_demand",
#     ascending=False
# )

# #Mostrar resultados

# print("\nTop 20 productos:")
# print(product_metrics.head(20))

# #Productos por tipo
# print("\nProductos ESTABLES:")
# print(product_metrics[product_metrics["Demand_Type"]=="Stable"].head())

# print("\nProductos MODERADOS:")

# print(product_metrics[product_metrics["Demand_Type"]=="Moderate variability"].head())

# print("\nProductos INTERMITENTES:")
# print(product_metrics[product_metrics["Demand_Type"]=="Intermittent"].head())


# product_metrics.to_excel(r"C:\Users\tamar\OneDrive\Documentos\Python\Capstone\Documentos Generados\analisis_productos_demanda_2021-2026.xlsx", index=False)
# print("\nArchivo guardado: analisis_productos_demanda.xlsx")
# #nombre del archivo.info()
# #nombre del archivo.describe()

import pandas as pd
import numpy as np

print("Cargando dataset")

#poner la direccion donde guardaron el archivo
df = pd.read_csv(r"Datos Documentos Excel\Documentos 2021-2026\Ventas_mensuales.csv")

print("Primeras filas:")
print(df.head())

# convertir Mes a fecha 
df["Mes"] = pd.to_datetime(df["Mes"])
monthly = df.copy()

print("\n Dataset mensual listo:")
print(monthly.head())

# MÉTRICAS POR PRODUCTO (opción 1: global)
def calculate_metrics(group):

    mean_demand = group["Demanda"].mean()
    std_demand = group["Demanda"].std()

    if mean_demand == 0:
        cv = np.nan
    else:
        cv = std_demand / mean_demand

    zero_months = (group["Demanda"] == 0).sum()
    total_months = len(group)

    zero_ratio = zero_months / total_months

    total_demand = group["Demanda"].sum()

    return pd.Series({
        "mean_demand": mean_demand,
        "std_demand": std_demand,
        "cv": cv,
        "zero_ratio": zero_ratio,
        "total_demand": total_demand
    })

# AGRUPAR POR PRODUCTO
product_metrics = monthly.groupby("Producto").apply(calculate_metrics).reset_index()

# CLASIFICACIÓN DE DEMANDA
def classify_demand(row):

    if row["zero_ratio"] > 0.4:
        return "Intermittent"

    elif row["cv"] < 0.5:
        return "Stable"

    elif row["cv"] < 1:
        return "Moderate variability"

    else:
        return "Highly variable"

product_metrics["Demand_Type"] = product_metrics.apply(classify_demand, axis=1)

# ordenar por demanda total
product_metrics = product_metrics.sort_values(
    by="total_demand",
    ascending=False
)

# RESULTADOS
print("\nTop 20 productos:")
print(product_metrics.head(20))

print("\nProductos ESTABLES:")
print(product_metrics[product_metrics["Demand_Type"]=="Stable"].head())

print("\nProductos MODERADOS:")
print(product_metrics[product_metrics["Demand_Type"]=="Moderate variability"].head())

print("\nProductos INTERMITENTES:")
print(product_metrics[product_metrics["Demand_Type"]=="Intermittent"].head())

# GUARDAR RESULTADO poner la direccion donde quieren guardar el archivo
salida = r"G:\My Drive\A capstone Clari\Datos Documentos Excel\Documentos 2021-2026\analisis_productos_demanda-2021-2026.xlsx"

product_metrics.to_excel(salida, index=False)

print("\n Archivo guardado:", salida)
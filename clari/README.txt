Notebooks generados para probar XGBoost por separado.

Usarlos así:
1. Copia los .ipynb dentro de tu carpeta local: Capstone/clari
2. Verifica que estén ahí también:
   - G:\My Drive\ElCapstone\Capstone\clari\CafeBelenTotal.xlsx
   - Producto_281670015_semanal.csv
   - carpeta resultados/ (si no existe, el notebook la crea)
3. Abrí cada notebook y corré celda por celda.

Casos:
- mensual_caso_1_xgboost.ipynb: negativos a 0, nulls a 0, ceros quedan.
- mensual_caso_2_xgboost.ipynb: negativos a 0, nulls a 0, eliminar ceros.
- mensual_caso_3_xgboost.ipynb: netear devoluciones.
- semanal_caso_1_xgboost.ipynb: negativos a 0, nulls a 0, ceros quedan.
- semanal_caso_2_xgboost.ipynb: negativos a 0, nulls a 0, eliminar ceros.
- semanal_caso_3_xgboost.ipynb: netear devoluciones.

Recomendación metodológica:
El caso 1 suele ser el más correcto para forecasting porque preserva la continuidad temporal.
El caso 2 es experimental y puede sesgar el modelo, porque elimina períodos sin demanda.
El caso 3 sirve para comparar si tratar las devoluciones como demanda neta ayuda o empeora.

from Parametros import *
import pandas
import re
import csv

def corregir_formato_tiempo(valor):
    # Si el valor tiene más de un punto (separador de miles incorrecto), corregirlo
    if isinstance(valor, str) and valor.count('.') > 1:
        # Eliminar los puntos que actúan como separador de miles y mantener el decimal
        partes = valor.split('.')
        valor_corregido = partes[0] + ''.join(partes[1:])
        return float(valor_corregido)  # Convertir a float si es necesario
    return valor


#Extraer el archivo#
data = pandas.read_csv("resultados_domingo.csv", encoding='ISO-8859-1', sep=';')

#Crear variables#
x_ = {(i,k): 0 for i in I+M+E+H+H_ for k in K}
z1_ = {k: 0 for k in K}
z2_ = {k: 0 for k in K}
z3_ = {k: 0 for k in K}
y_ = {(i,j,k): 0 for i in I+M+E+H+H_ for j in I+M+E+H+H_ for k in K}
t_ = {(i,k): 0 for i in I+M+E+H+H_ for k in K}
n_ = {(i,j,k): 0 for i in M for j in I_M for k in K}
r_ = {(i,j,k): 0 for i in I_E+I_P for j in E for k in K}

#Se guardan los valores del archivo en las varibales#
for index, row in data.iterrows():
    variable = row["Variable"]
    valor_optimo = row["Valor Óptimo"]
    
    match = re.match(r"([a-zA-Z]+[0-9]*)\((\d+)(?:, *(\d+))?(?:, *(\d+))?\)", variable)
    
    if match:
        var_type = match.group(1)  # Tipo de variable (por ejemplo, z1, z2, x, y, etc.)
        index1 = int(match.group(2))  # Primer número dentro de los paréntesis
        index2 = match.group(3)  # Segundo número (si existe)
        index3 = match.group(4)  # Tercer número (si existe)
        
        # Determinar la llave según la cantidad de índices
        if index3 is not None:
            key = (index1, int(index2), int(index3))  # Tupla con tres índices
        elif index2 is not None:
            key = (index1, int(index2))  # Tupla con dos índices
        else:
            key = index1  # Un solo índice
        
        # Añadir al diccionario correspondiente#
        if var_type in "z1":
            z1_[key] = valor_optimo
        elif var_type in "z2":
            z2_[key] = valor_optimo
        elif var_type in "z3":
            z3_[key] = valor_optimo
        elif var_type in "x":
            x_[key] = valor_optimo
        elif var_type in "t":
            valor_optimo = corregir_formato_tiempo(valor_optimo)
            t_[key] = valor_optimo
        elif var_type in "y":
            y_[key] = valor_optimo
        elif var_type in "n":
            n_[key] = valor_optimo
        elif var_type in "r":
            r_[key] = valor_optimo

##########
###KPIs###
##########

#Cantidad de pacientes atendidos por cada enfermero#
pac_atendidos = {k: sum(x_[i,k] for i in I) for k in K}

#Costos asociados a cada enfermero#
costo_enf = {k: cf*z1_[k] + sum(c[i]*x_[i,k] for i in I) + sum(sum(B*d[i,j]*y_[i,j,k] for i in I+M+E+H+H_) for j in I+M+E+H+H_) if k in K_E else sum(sum(B*d[i,j]*y_[i,j,k] for i in I+M+E+H+H_) for j in I+M+E+H+H_) for k in K}

#Tiempo en que enfermero atiende a pacientes#
atencion_enf = {k: sum(l[i]*x_[i,k] for i in I) for k in K}

#Tiempo en que enfermero estuvo viajando#
viaje_enf = {k: round(sum(sum(t[i,j]*y_[i,j,k] for i in I+M+E+H+H_) for j in I+M+E+H+H_),3) for k in K}

#Busca el tiempo en que se acaba turno de enfermero#
fin_enf = {}
for k in K:
    max = 0
    for i in I+M+E:
        if t_[i,k] > max:
            max = t_[i,k]
            id_ = i
    
    fin_enf[k] = round(t_[id_,k] + l[id_] + t[id_,H_[0]],3) if z1_[k] > 0 else 0

#Tiempo sobrante de cada enfermero#
sobrante_enf = {k: round(s[k] - fin_enf[k],3) if z1_[k] > 0 else 0 for k in K}

#Tiempo de espera de cada enfermero#
espera_enf = {k: round(fin_enf[k] - a[k] - sum(l[i]*x_[i,k] for i in I+M+E) - sum(sum(t[i,j]*y_[i,j,k] for i in I+M+E+H+H_) for j in I+M+E+H+H_),3) if z1_[k] > 0 else 0 for k in K}

#Distancia recorrida por cada enfermero#
dist_enf = {k: round(sum(sum(d[i,j]*y_[i,j,k] for i in I+M+E+H+H_) for j in I+M+E+H+H_),3) for k in K}

#Guardar KPIs en un archivo#
with open("KPI_Domingo_final.csv", "w", newline="") as file:
    escribir = csv.writer(file, delimiter=',')

    escribir.writerow(["Enfermero", "Tipo", "Costo", "Cant. Atend.", "Tiempo Atención", "Tiempo Viaje", "Tiempo Espera", "Tiempo Sobrante", "Dist. Recorrida"])

    for k in K:
        if k in K_1:
            tipo = "Interno 1"
        elif k in K_2:
            tipo = "Interno 2"
        else:
            tipo = "Externo"

        escribir.writerow([k,tipo, costo_enf[k], pac_atendidos[k], atencion_enf[k], viaje_enf[k], espera_enf[k], sobrante_enf[k], dist_enf[k]])
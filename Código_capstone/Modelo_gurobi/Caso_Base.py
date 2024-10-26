from Parametros import *
from Funciones import *
from itertools import product
import csv
import time

operadores = True #Se aplican operadores de mejoras para el caso base#
guardar_datos = False #Guarda el resultado en un archivo csv#

###############
###CASO BASE###
###############
tiempo_inicial = time.time()

#Definimos las "variables"#
x_ = {(i,k): 0 for i in I+M+E+H+H_ for k in K}
z1_ = {k: 0 for k in K}
z2_ = {k: 0 for k in K}
z3_ = {k: 0 for k in K}
y_ = {(i,j,k): 0 for i in I+M+E+H+H_ for j in I+M+E+H+H_ for k in K}
t_ = {(i,k): 0 for i in I+M+E+H+H_ for k in K}
n_ = {(i,j,k): 0 for i in M for j in I_M for k in K}
r_ = {(i,j,k): 0 for i in I_E+I_P for j in E for k in K}

#Se asignan los valore predeterminados#
for k in K:
    for i in H+H_:
        x_[i,k] = 1

#Guardamos en una lista a las personas que ya fueron atendidas#
lista_atendidos = []

#Iteramos sobre los enfermeros#
for k in K:
    #Asignamos su tiempo inicial y su pocisión inicial#
    z1_[k] = 1
    tiempo_enf = a[k]
    poci = H[0]

    t_[H[0],k] = a[k]
    t_[H_[0],k] = s[k]

    #Guardamos una lista de las UM y UE que ya visito el enfermero#
    unidades = []

    #Variable para determinar si pudo atender a alguien#
    atendio = False

    #Iteramos hasta que el enfermero no pueda atnder a más pacientes con necesidades extra#
    for i in list(set(I_M + I_E + I_P)):
        if i not in lista_atendidos:
            minimo = 100000

            #Dependiendo del grupo en que se encuentre se asignan distintas restricciones#
            if i in I_M and i not in I_E+I_P:
                #Buscamos la unidad medica más cercana que cumpla las condiciones#
                for m in M:
                    t_unidad = max(tiempo_enf + t[poci,m],b[m])
                    t_paciente = max(t_unidad + l[m] + t[m,i],b[i])

                    if m not in unidades and t_unidad <= f[m] and t_paciente <= f[i] and t_paciente - t_unidad - l[m] <= 60 and t_paciente + l[i] + t[i,H_[0]] <= s[k]:
                        if t_paciente < minimo:
                            minimo = t_paciente
                            unidad = m

                #Si se encontro alguna opcion valida, agregamos al paciente a los atendidos, la unidad a unidades usadas y actualizamos el valor de las variables#
                if minimo != 100000:
                    lista_atendidos.append(i)
                    unidades.append(unidad)
                    atendio = True

                    z2_[k] = 1
                    x_[unidad,k] = 1
                    x_[i,k] = 1
                    y_[poci,unidad,k] = 1
                    y_[unidad,i,k] = 1
                    t_[unidad,k] = max(tiempo_enf + t[poci,unidad],b[unidad])
                    t_[i,k] = max(max(tiempo_enf + t[poci,unidad],b[unidad]) + l[unidad] + t[unidad,i],b[i])
                    n_[unidad,i,k] = 1

                    #Actualizamos tiempo y pocision#
                    tiempo_enf = max(max(tiempo_enf + t[poci,unidad],b[unidad]) + l[unidad] + t[unidad,i],b[i]) + l[i]
                    poci = i

            elif i not in I_M and i in I_E+I_P:
                #Buscamos la unidad examen mas cercana que cumpla condiciones#
                for e in E:
                    t_paciente = max(tiempo_enf + t[poci,i],b[i])
                    t_unidad = max(t_paciente + l[i] + t[i,e], b[e])

                    if e not in unidades and t_paciente <= f[i] and t_unidad <= f[e] and t_unidad + l[e] + t[e,H_[0]] <= s[k]:
                        if i in I_P:
                            if t_unidad - t_paciente - l[i] <= 60:
                                if t_unidad < minimo:
                                    minimo = t_unidad
                                    unidad = e

                        else:
                            if t_unidad < minimo:
                                minimo = t_unidad
                                unidad = e

                #Si se encontro alguna opcion valida, agregamos al paciente a los atendidos, la unidad a unidades usadas y actualizamos el valor de las variables#
                if minimo != 100000:
                    lista_atendidos.append(i)
                    unidades.append(unidad)
                    atendio = True

                    z3_[k] = 1
                    x_[i,k] = 1
                    x_[unidad,k] = 1
                    y_[poci,i,k] = 1
                    y_[i,unidad,k] = 1
                    t_[i,k] = max(tiempo_enf + t[poci,i],b[i])
                    t_[unidad,k] = max(max(tiempo_enf + t[poci,i],b[i]) + l[i] + t[i,unidad],b[unidad])
                    r_[i,unidad,k] = 1

                    #Actualizamos tiempo y pocision#
                    tiempo_enf = max(max(tiempo_enf + t[poci,i],b[i]) + l[i] + t[i,unidad],b[unidad]) + l[unidad]
                    poci = unidad
            
            elif i in I_M and i in I_E+I_P:
                #Buscamos la combinación entre unidad medica y unidad examen mas cercanas que cumplan condiciones#
                for m, e in product(M,E):

                    t_unidad_m = max(tiempo_enf + t[poci,m],b[m])
                    t_paciente = max(t_unidad_m + l[m] + t[m,i],b[i])
                    t_unidad_e = max(t_paciente + l[i] + t[i,e],b[e])

                    if m not in unidades and e not in unidades and t_unidad_m <= f[m] and t_paciente <= f[i] and t_unidad_e <= f[e] and t_paciente - t_unidad_m - l[m] <= 60 and t_unidad_e + l[e] + t[e,H_[0]] <= s[k]:
                        if i in I_P:
                            if t_unidad_e - t_paciente - l[i] <= 60:
                                if t_unidad_e < minimo:
                                    minimo = t_unidad_e
                                    unidad_m = m
                                    unidad_e = e

                        else:
                            if t_unidad_e < minimo:
                                minimo = t_unidad_e
                                unidad_m = m
                                unidad_e = e
            
                #Si se encontro alguna opcion valida, agregamos al paciente a los atendidos, la unidad a unidades usadas y actualizamos el valor de las variables#
                if minimo != 100000:
                    lista_atendidos.append(i)
                    unidades.append(unidad_m)
                    unidades.append(unidad_e)
                    atendio = True

                    z2_[k] = 1
                    z3_[k] = 1
                    x_[unidad_m,k] = 1
                    x_[i,k] = 1
                    x_[unidad_e,k] = 1
                    y_[poci,unidad_m,k] = 1
                    y_[unidad_m,i,k] = 1
                    y_[i,unidad_e,k] = 1
                    t_[unidad_m,k] = max(tiempo_enf + t[poci,unidad_m],b[unidad_m])
                    t_[i,k] = max(max(tiempo_enf + t[poci,unidad_m],b[unidad_m]) + l[unidad_m] + t[unidad_m,i],b[i])
                    t_[unidad_e,k] = max(max(max(tiempo_enf + t[poci,unidad_m],b[unidad_m]) + l[unidad_m] + t[unidad_m,i],b[i]) + l[i] + t[i,unidad_e], b[unidad_e])
                    n_[unidad_m,i,k] = 1
                    r_[i,unidad_e,k] = 1

                    #Actualizamos tiempo y pocision#
                    tiempo_enf = max(max(max(tiempo_enf + t[poci,unidad_m],b[unidad_m]) + l[unidad_m] + t[unidad_m,i],b[i]) + l[i] + t[i,unidad_e], b[unidad_e]) + l[unidad_e]
                    poci = unidad_e

        
    #Cuando se termina de verificar si el enfermero puede atender a más pacientes con necesidades se verifica si puede atender a pacientes normales#
    while True:
        minimo = 100000

        #Se busca al paciente normal más cercano que cumpla condiciones#
        for i in I_N:
            t_paciente = max(tiempo_enf + t[poci,i],b[i])

            if i not in lista_atendidos and t_paciente <= f[i] and t_paciente + l[i]+ t[i,H_[0]] <= s[k]:
                if t_paciente < minimo:
                    minimo = t_paciente
                    paciente = i

        #Si no hay ningún paciente normal al q se pueda atender, se termina el bucle sobre pacientes normales para el enfermero#
        if minimo == 100000:
            break
        
        #Agregamos al paciente a los atendidos, y actualizamos el valor de las variables#
        lista_atendidos.append(paciente)
        atendio = True

        x_[paciente,k] = 1
        y_[poci,paciente,k] = 1
        t_[paciente,k] = max(tiempo_enf + t[poci,paciente], b[paciente])

        #Se actualiza el tiempo y pocision del enfermero#
        tiempo_enf = max(tiempo_enf + t[poci,paciente], b[paciente]) + l[paciente]
        poci = paciente

    #Cuando no puede atender a más pacientes se termina su ciclo y se revisa si falta atender pacientes para mandar a otro enfermero#
    y_[poci,H_[0],k] = 1
    if sorted(I) == sorted(lista_atendidos):
        #Si no falta atender pacientes se termina el bucle#
        break

    #Si no atendio se ponen a 0 los valores#
    if atendio == False:
        z1_[k] = 0
        t_[H[0],k] = 0
        t_[H_[0],k] = 0

#Para los enfermeros que no se usan se asigna el unico camino posible#
for k in K:
    if z1_[k] == 0:
        y_[H[0],H_[0],k] = 1


#Implementación de operadores de mejora lambda interchange y 2-opt#
if operadores == True: 
    print(f"El costo total es de: {funcion_objetivo(x_,z1_,y_)}")   
    y_, t_ = k_opt(x_,z1_, y_, t_, n_, r_)

#Se reordenan los enfermeros de manera que en cada subgrupo el enfermero con menor enumeración tenga el nodo con menor enumeración de cada ruta#
def ordenar(conj):
    for k, p in product(conj,conj):

        #Revisamos todas las parejas de este grupo de enfermeros que hayan atendido a pacientes#
        if k < p and z1_[k] == 1 and z1_[p] == 1:
            pacientes_k = []
            pacientes_p = []

            #Se guardan los indices de los pacientes que atendio cada uno#
            for i in I:
                if x_[i,k] == 1:
                    pacientes_k.append(i)
                if x_[i,p] == 1:
                    pacientes_p.append(i)

            #Si el enfermero p atendio a un paciente con enumeración menor que el enfermero k se cambias sus rutas#
            if min(pacientes_k) > min(pacientes_p):
                for i in I+M+E:
                    x_[i,k],x_[i,p] = x_[i,p],x_[i,k]
                    t_[i,k],t_[i,p] = t_[i,p],t_[i,k]
                z2_[k],z2_[p] = z2_[p],z2_[k]
                z3_[k],z3_[p] = z3_[p],z3_[k]
                for i in I+M+E+H+H_:
                    for j in I+M+E+H+H_:
                        y_[i,j,k],y_[i,j,p] = y_[i,j,p],y_[i,j,k]
                for i in M:
                    for j in I_M:
                        n_[i,j,k],n_[i,j,p] = n_[i,j,p],n_[i,j,k]
                for i in I_E+I_P:
                    for j in E:
                        r_[i,j,k],r_[i,j,p] = r_[i,j,p],r_[i,j,k]

#Se aplican los ordenes para cada grupo de enfermeros#
ordenar(K_1)
ordenar(K_2)
ordenar(K_E)

#Evaluación#
print(f"Tiempo de ejecución: {time.time()-tiempo_inicial}")
print(f"El costo total es de: {funcion_objetivo(x_,z1_,y_)}")

#Se guardan las respuestas de gurobi en un archivo externo#
if guardar_datos == True:
    with open("hola.csv", "w", newline="") as file:
        escribir = csv.writer(file, delimiter=';')
        
        escribir.writerow(["Variable", "Valor Óptimo"])

        for k in K:            
            if z1_[k] > 0:
                escribir.writerow([f"z1({k})",round(z1_[k],1)])

            if z2_[k] > 0:
                escribir.writerow([f"z2({k})", round(z2_[k],1)])

            if z3_[k] > 0:
                escribir.writerow([f"z3({k})", round(z3_[k],1)])

            for i in I+M+E+H+H_:
                if x_[i,k] > 0:
                    escribir.writerow([f"x{i,k}", round(x_[i,k],1)])

            for i in I+M+E+H+H_:
                for j in I+M+E+H+H_:
                    if y_[i,j,k] > 0:
                        escribir.writerow([f"y{i,j,k}", round(y_[i,j,k],1)])

            for i in I+M+E+H+H_:
                if t_[i,k] > 0:
                    escribir.writerow([f"t{i,k}", round(t_[i,k],3)])

            for i in M:
                for j in I_M:
                    if n_[i,j,k] > 0:
                        escribir.writerow([f"n{i,j,k}", round(n_[i,j,k],1)])

            for i in I_P+I_E:
                for j in E:
                    if r_[i,j,k] > 0:
                        escribir.writerow([f"r{i,j,k}", round(r_[i,j,k],1)])
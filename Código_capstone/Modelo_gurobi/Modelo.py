from gurobipy import *
from Parametros import *
from Caso_Base import *
import csv

############
###MODELO###
############
#Consideramos complejidades del modelo#
ventanas = True #Apreta las ventanas de tiempo#
simetria = True #Aplica las restricciones de simetria#
caso_base = True #Implementa caso base como solución factible inicial
guardar_datos = True #Guarda el resultado en un archivo csv
#Crear Modelo#
modelo = Model()

#Variables#
X = modelo.addVars(I+M+E+H+H_, K, vtype=GRB.BINARY, name="x") #1 si k pasa por nodo i#
Z1 = modelo.addVars(K, vtype=GRB.BINARY, name="z1") #AUX#
Z2 = modelo.addVars(K, vtype=GRB.BINARY, name="z2") #AUX#
Z3 = modelo.addVars(K, vtype=GRB.BINARY, name="z3") #AUX#
Y = modelo.addVars(I+M+E+H+H_, I+M+E+H+H_, K, vtype=GRB.BINARY, name="y") #1 si k va desde i a j#
T = modelo.addVars(I+M+E+H+H_, K, name="t") #tiempo en que k llega a i#
N = modelo.addVars(M, I_M, K, vtype=GRB.BINARY, name="n") #si k lleva medicamento desde i a j#
R = modelo.addVars(I_E+I_P, E, K, vtype=GRB.BINARY, name="r") #si k lleva examen desde i a j#


#Restricciones#
#enfermeros empiezan y terminan en hospital#
modelo.addConstrs(((X[i,k] == 1) for i in H+H_ for k in K), name="restriccion 1")
#Solo 1 enfermero atiende a cada paciente#
modelo.addConstrs(((sum(X[i,k] for k in K) == 1) for i in I), name="restriccion 2")
#Activación Z1#
modelo.addConstrs(((Z1[k] <= sum(X[i,k] for i in I)) for k in K), name="restriccion 3")
modelo.addConstrs(((G1*Z1[k] >= sum(X[i,k] for i in I)) for k in K), name="restriccion 4")
#Activación Z2#
modelo.addConstrs(((Z2[k] <= sum(X[i,k] for i in I_M)) for k in K), name="restriccion 5")
modelo.addConstrs(((G2*Z2[k] >= sum(X[i,k] for i in I_M)) for k in K), name="restriccion 6")
#Activación Z3#
modelo.addConstrs(((Z3[k] <= sum(X[i,k] for i in I_E+I_P)) for k in K), name="restriccion 7")
modelo.addConstrs(((G3*Z3[k] >= sum(X[i,k] for i in I_E+I_P)) for k in K), name="restriccion 8")
#Si enfermero k atiende a paciente i con requerimiento medicamentos debe pasar entre 1 y n veces a unidades medicas#
modelo.addConstrs(((sum(X[i,k] for i in M) <= sum(X[i,k] for i in I_M)) for k in K), name="restriccion 9")
modelo.addConstrs(((sum(X[i,k] for i in M) >= Z2[k]) for k in K), name="restriccion 10")
#Si enfermero k atiende a paciente i con requerimiento examen debe pasar entre 1 y n veces a unidad examen#
modelo.addConstrs(((sum(X[i,k] for i in E) <= sum(X[i,k] for i in I_E+I_P)) for k in K), name="restriccion 11")
modelo.addConstrs(((sum(X[i,k] for i in E) >= Z3[k]) for k in K), name="restriccion 12")
#Si enfermero k pasa por nodo i ocupa solo un arco de entrada y uno de salida#
modelo.addConstrs(((sum(Y[i,j,k] for j in I+M+E+H+H_) == X[i,k]) for i in I+M+E+H for k in K), name="restriccion 13")
modelo.addConstrs(((sum(Y[j,i,k] for j in I+M+E+H+H_) == X[i,k]) for i in I+M+E+H_ for k in K), name="restriccion 14")
#No se puede salir de hospital final#
modelo.addConstrs(((sum(Y[H_[0],j,k] for j in I+M+E+H+H_) == 0) for k in K), name="restriccion 15")
#No se puede llegar a hospital inicial#
modelo.addConstrs(((sum(Y[j,H[0],k] for j in I+M+E+H+H_) == 0) for k in K), name="restriccion 16")
#Si enfermero k atiende a paciente con requerimiento medicamento debe llevar el medicamento desde una unidad medica#
modelo.addConstrs(((sum(N[j,i,k] for j in M) == X[i,k]) for i in I_M for k in K), name="restriccion 17")
#Si se lleva medicamento desde unidad medica debe pasar por ese nodo#
modelo.addConstrs(((sum(N[i,j,k] for j in I_M) >= X[i,k]) for i in M for k in K), name="restriccion 18")
modelo.addConstrs(((sum(N[i,j,k] for j in I_M) <= G2*X[i,k]) for i in M for k in K), name="restriccion 19")
#Si enfermero k atiende a paciente con requerimiento examen debe llevar el examen hasta una unidad examen#
modelo.addConstrs(((sum(R[i,j,k] for j in E) == X[i,k]) for i in I_E+I_P for k in K), name="restriccion 20")
#Si se lleva examen hasta unidad examen debe pasar por ese nodo#
modelo.addConstrs(((sum(R[j,i,k] for j in I_E+I_P) >= X[i,k]) for i in E for k in K), name="restriccion 21") 
modelo.addConstrs(((sum(R[j,i,k] for j in I_E+I_P) <= G3*X[i,k]) for i in E for k in K), name="restriccion 22")
#Si el enfermero pasa por un nodo debe pasar entre los tiempos disponibles
if ventanas == True:
    modelo.addConstrs(((T[i,k] <= min(s[k]-t[i,H_[0]]-l[i],f[i])*X[i,k]) for i in I+M+E for k in K), name="restriccion 23")
    modelo.addConstrs(((T[i,k] >= max(a[k]+t[H[0],i],b[i])*X[i,k]) for i in I+M+E for k in K), name="restriccion 24")
else:
    modelo.addConstrs(((T[i,k] <= f[i]*X[i,k]) for i in I+M+E for k in K), name="restriccion 23")
    modelo.addConstrs(((T[i,k] >= b[i]*X[i,k]) for i in I+M+E for k in K), name="restriccion 24")
#Relación lógica de tiempos entre 2 nodos consecutivos
modelo.addConstrs(((T[i,k] + l[i] + t[i,j] <= T[j,k] + G4[i,j,k]*(1-Y[i,j,k])) for i in I+M+E+H+H_ for j in I+M+E+H+H_ for k in K), name="restriccion 25")
#Hora de inicio de cada enfermero
modelo.addConstrs(((T[i,k] >= a[k]*Z1[k]) for i in H for k in K), name="restriccion 26")
#Hora de salida de cada enfermero
modelo.addConstrs(((T[i,k] <= s[k]*Z1[k]) for i in H_ for k in K), name="restriccion 27")
#Si un enfermero lleva medicamento debe entregarlo después de pasar por U.E. y antes de 1 hora
modelo.addConstrs(((T[i,k] <= T[j,k] + G5[i]*(1-N[i,j,k])) for i in M for j in I_M for k in K), name="restriccion 28")
modelo.addConstrs(((T[i,k] + l[i] + 60 >= T[j,k] - G6[i,j]*(1-N[i,j,k])) for i in M for j in I_M for k in K), name="restriccion 29")
#Si un efermero lleva examen debe entregarlo después de pasar por el paciente
modelo.addConstrs(((T[i,k] <= T[j,k] + G7[i]*(1-R[i,j,k])) for i in I_E+I_P for j in E for k in K), name="restriccion 30")
#Si un enfermero lleva examen perecible debe entregarlo antes de 1 hora#
modelo.addConstrs(((T[i,k] + l[i] + 60 >= T[j,k] - G8[i,j]*(1-R[i,j,k])) for i in I_P for j in E for k in K), name="restriccion 31")

#Restricción de simetría:# 
if simetria == True:
    #Manda a enfermeros en orden (no se puede mandar al 7 si es que no se mando al 6)#
    modelo.addConstrs(((Y[H[0],H_[0],k] >= Y[H[0],H_[0],k-1]) for k in K_1[1:]+K_2[1:]+K_E[1:]), name="restriccion 32")
    #Enfermeros seleccionados tomas rutas en orden (el enfermero 1 toma ruta que contenga a nodo 1, enfermero 2 toma ruta con siguiente numero más pequeño)
    modelo.addConstrs(((X[i,k] <= sum(X[j,k-1] for j in I if j < i)) for i in I for k in K_1[1:]+K_2[1:]+K_E[1:]), name="restriccion 33")

#Funcion Objetivo#
modelo.setObjective(sum(cf*Z1[k] + (sum(c[i]*X[i,k] for i in I)) for k in K_E) + quicksum(B*d[i,j]*Y[i,j,k] for i in I+M+E+H+H_ for j in I+M+E+H+H_ for k in K))
#modelo.setParam(GRB.Param.MIPFocus, 2)
#modelo.setParam(GRB.Param.Symmetry, 2)
modelo.setParam(GRB.Param.TimeLimit, 28800)

#Caso Base#
if caso_base == True:
    for k in K:
        #Variables X y T#
        for i in I+M+E+H+H_:
            X[i,k].Start = x_[i,k]
            T[i,k].Start = t_[i,k]
        
        #Variables Z#
        Z1[k].Start = z1_[k]
        Z2[k].Start = z2_[k]
        Z3[k].Start = z3_[k]

        #Variables Y#
        for i in I+M+E+H+H_:
            for j in I+M+E+H+H_:
                Y[i,j,k].Start = y_[i,j,k]

        #Variables N#
        for i in M:
            for j in I_M:
                N[i,j,k].Start = n_[i,j,k]

        #Variables R#
        for i in I_E+I_P:
            for j in E:
                R[i,j,k].Start = r_[i,j,k]

modelo.optimize()

print(modelo.objVal)

#Se guardan las respuestas de gurobi en un archivo externo#
if guardar_datos == True:
    with open("Lunes_4.csv", "w", newline="") as file:
        escribir = csv.writer(file, delimiter=';')

        escribir.writerow(["Variable", "Valor Óptimo"])
        for k in K:            
            if Z1[k].x > 0:
                escribir.writerow([f"z1({k})", round(Z1[k].x,1)])

            if Z2[k].x > 0:
                escribir.writerow([f"z2({k})", round(Z2[k].x,1)])

            if Z3[k].x > 0:
                escribir.writerow([f"z3({k})", round(Z3[k].x,1)])

            for i in I+M+E+H+H_:
                if X[i,k].x > 0:
                    escribir.writerow([f"x{i,k}", round(X[i,k].x,1)])

            for i in I+M+E+H+H_:
                for j in I+M+E+H+H_:
                    if Y[i,j,k].x > 0:
                        escribir.writerow([f"y{i,j,k}", round(Y[i,j,k].x,1)])

            for i in I+M+E+H+H_:
                if T[i,k].x > 0:
                    escribir.writerow([f"t{i,k}", round(T[i,k].x,3)])

            for i in M:
                for j in I_M:
                    if N[i,j,k].x > 0:
                        escribir.writerow([f"n{i,j,k}", round(N[i,j,k].x,1)])

            for i in I_P+I_E:
                for j in E:
                    if R[i,j,k].x > 0:
                        escribir.writerow([f"r{i,j,k}", round(R[i,j,k].x,1)])
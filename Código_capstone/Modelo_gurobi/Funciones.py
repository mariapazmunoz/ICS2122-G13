from Parametros import *
from itertools import product

###############
###FUNCIONES###
###############

#Retorna el valor de la función objtivo#
def funcion_objetivo(x_,z1_,y_):
    return sum(cf*z1_[k] + (sum(c[i]*x_[i,k] for i in I)) for k in K_E) + sum(sum(sum(B*d[i,j]*y_[i,j,k] for i in I+M+E+H+H_) for j in I+M+E+H+H_) for k in K)

#Obtiene la ruta del enfermero#
def rutas(k, x_, t_):
    visitas = []
    #Se extraen los nodos por los que pasa#
    for i in I+M+E+H+H_:
        if x_[i,k] == 1:
            visitas.append(i)
    #Se ordenan#
    rutas_tiempos = [(i,t_[i,k]) for i in visitas]
    ordenado = sorted(rutas_tiempos, key=lambda x: x[1])
    ruta = [i for i, tiempo in  ordenado]
    return ruta

#Genera los tiempos de llegada a cada nodo para la ruta indicada#
def tiempos_rutas(k,ruta):
    #Generamos una lista que guarde los tiempos#
    t_aux = {}
    #Vemos los tiempos en los que se llegan a los nodos#
    t_aux[4000,k] = a[k]
    for nodo in range(len(ruta)-2):
        t_aux[ruta[nodo+1],k] = max(t_aux[ruta[nodo],k] + l[ruta[nodo]] + t[ruta[nodo],ruta[nodo+1]], b[ruta[nodo+1]])
    t_aux[4001,k] = max(t_aux[ruta[-2],k] + l[ruta[-2]] + t[ruta[-2],4001],s[k])

    #Generamos una lista con los arcos correspondientes#
    y_aux = {(i,j,k): 0 for i in I+M+E+H+H_ for j in I+M+E+H+H_}
    for i in range(len(ruta)-1):
        y_aux[ruta[i],ruta[i+1],k] = 1 

    return y_aux, t_aux
  
#Revisa si la ruta es factible#
def ruta_factible(k, ruta, n_, r_):
    #Generamos los tiempos de las nuevas rutas
    y_aux, t_aux = tiempos_rutas(k, ruta)

    #Se verifica si estos tiempos y rutas y son factibles#
    fact = True

    for i in ruta[1:-1]:
        if t_aux[i,k] > min(s[k]-t[i,H_[0]]-l[i],f[i]):
            fact = False

        if t_aux[i,k] < max(a[k]+t[H[0],i],b[i]):
            fact = False

    if t_aux[H_[0],k] > s[k]:
        fact = False

    for i,j in product(ruta,ruta):
        if t_aux[i,k] + l[i] + t[i,j] > t_aux[j,k] + G4[i,j,k]*(1-y_aux[i,j,k]):
            fact = False

    for i,j in product(M,I_M):
        if i in ruta and j in ruta:
            if t_aux[i,k] > t_aux[j,k] + G5[i]*(1-n_[i,j,k]):
                fact = False

            if t_aux[i,k] + l[i] + 60 < t_aux[j,k] - G6[i,j]*(1-n_[i,j,k]):
                fact = False

    for i,j in product(I_E+I_P,E):
        if i in ruta and j in ruta:
            if t_aux[i,k] > t_aux[j,k] + G7[i]*(1-r_[i,j,k]):
                fact = False

    for i,j in product(I_P,E):
        if i in ruta and j in ruta:
            if t_aux[i,k] + l[i] + 60 < t_aux[j,k] - G8[i,j]*(1-r_[i,j,k]):
                fact = False

    #Se retornan las variables#
    return fact, y_aux, t_aux


#Aplica lambda 1-0#
def lambda_10(k1,k2,ruta_1,ruta_2,x_):

    #Iteramos por cada nodo en la ruta 1 y ruta 2#
    for i,j in product(range(1, len(ruta_1) - 1),range(1, len(ruta_2))):
        if ruta_1[i] in I_N:                                    
            #Tomamos un nodo entre ruta_1 y lo pasamos a ruta_2
            nueva_ruta_1 = ruta_1[:i] +  ruta_1[i+1:]
            nueva_ruta_2 = ruta_2[:j] + [ruta_1[i]] + ruta_2[j:]

            #Actualizamos valor de variables auxiliares#

#Aplica lambda 1-1#
def lambda_11(k1,k2,ruta_1,ruta_2,x_,y_,t_,n_,r_, opt):
    mejor = False
    # Iteramos por cada nodo de la ruta 1 y la ruta 2
    for i,j in product(range(1, len(ruta_1) - 1),range(1, len(ruta_2) - 1)):
        if (ruta_1[i] in M and ruta_2[j] in M) or (ruta_1[i] in E and ruta_2[j] in E) or (ruta_1[i] in I and ruta_2[j] in I):
                                    
            # Intercambiamos un nodo entre ruta_1 y ruta_2
            nueva_ruta_1 = ruta_1[:i] + [ruta_2[j]] + ruta_1[i+1:]
            nueva_ruta_2 = ruta_2[:j] + [ruta_1[i]] + ruta_2[j+1:]
            print(f"nuevo {k1}: {nueva_ruta_1}")
            print(f"nuevo {k2}: {nueva_ruta_2}")

            #Actualizamos el valor de variables auxiliares#
            x_aux = x_
            x_aux[ruta_1[i],k1], x_aux[ruta_2[j],k1] = x_aux[ruta_2[j],k1], x_aux[ruta_1[i],k1]
            x_aux[ruta_1[i],k2], x_aux[ruta_2[j],k2] = x_aux[ruta_2[j],k2], x_aux[ruta_1[i],k2]

            n_aux = n_
            r_aux = r_
            #Actualizamos valores de n_ y r_ si es necesario#
            if ruta_1[i] in I_M and ruta_2[j] in I_M:
                for p in M:
                    if n_aux[p,ruta_1[i],k1] == 1 or n_aux[p,ruta_2[j],k2] == 1:
                        n_aux[p,ruta_1[i],k1], n_aux[p,ruta_2[j],k2] = n_aux[p,ruta_2[j],k2], n_aux[p,ruta_1[i],k1]

            elif ruta_1[i] in M and ruta_2[j] in M:
                for p in I_M:
                    if n_aux[ruta_1[i],p,k1] == 1 or n_aux[ruta_2[j],p,k2] == 1:
                        n_aux[ruta_1[i],p,k1], n_aux[ruta_2[j],p,k2] = n_aux[ruta_2[j],p,k2], n_aux[ruta_1[i],p,k1]

            elif ruta_1[i] in I_E+I_P and ruta_2[j] in I_E+I_P:
                for p in E:
                    if r_aux[ruta_1[i],p,k1] == 1 or r_aux[ruta_2[j],p,k2] == 1:
                        r_aux[ruta_1[i],p,k1], r_aux[ruta_2[j],p,k2] = r_aux[ruta_2[j],p,k2],r_aux[ruta_1[i],p,k1]
                                
            elif ruta_1[i] in E and ruta_2[j] in E:
                for p in I_E+I_P:
                    if r_aux[p,ruta_1[i],k1] == 1 or r_aux[p,ruta_2[j],k2] == 1:
                        r_aux[p,ruta_1[i],k1], r_aux[p,ruta_2[j],k2] = r_aux[p,ruta_2[j],k2],r_aux[p,ruta_1[i],k1]

            fact_1, y_aux_1, t_aux_1 = ruta_factible(k1, nueva_ruta_1, n_aux, r_aux)
            fact_2, y_aux_2, t_aux_2 = ruta_factible(k2, nueva_ruta_2, n_aux, r_aux) 

            #Verificamos si son factibles las nuevas rutas#
            if fact_1 == True and fact_2 == True:
                optimo_1 = sum(sum(B*d[i,j]*y_aux_1[i,j,k1] for i in I+M+E+H+H_) for j in I+M+E+H+H_) + (0 if k1 not in K_E else cf + sum(c[i]*x_aux[i,k1] for i in I))
                optimo_2 = sum(sum(B*d[i,j]*y_aux_2[i,j,k2] for i in I+M+E+H+H_) for j in I+M+E+H+H_) + (0 if k2 not in K_E else cf + sum(c[i]*x_aux[i,k2] for i in I))

                #Si es una solución mejor se actualiza#
                if optimo_1 + optimo_2 < opt:
                    mejor = True
                    print("mejor")
                    for i,j in product(I+M+E+H+H_, I+M+E+H+H_):
                        y_[i,j,k1] = y_aux_1[i,j,k1]
                        y_[i,j,k2] = y_aux_2[i,j,k2]
                    for i in nueva_ruta_1:
                        t_[i,k1] = t_aux_1[i,k1]
                    for i in nueva_ruta_2:
                        t_[i,k2] = t_aux_2[i,k2]
                    x_ = x_aux
                    n_ = n_aux
                    r_ = r_aux


                    #Se cierra el bucle 1-1#
                    break
    
    return mejor,x_,y_,t_,n_,r_

#Intercambia a pacientes entre enfermeros y busca mejor solución#
def lambda_interchange(x_,z1_,z2_,z3_,y_,t_,n_,r_):
    for k1,k2 in product(K,K):
        if k1 != k2:
            while True:
                cont = False

                while True:
                    optimo_1 = sum(sum(B*d[i,j]*y_[i,j,k1] for i in I+M+E+H+H_) for j in I+M+E+H+H_) + (0 if k1 not in K_E else cf + sum(c[i]*x_[i,k1] for i in I))
                    optimo_2 = sum(sum(B*d[i,j]*y_[i,j,k2] for i in I+M+E+H+H_) for j in I+M+E+H+H_) + (0 if k2 not in K_E else cf + sum(c[i]*x_[i,k2] for i in I))

                    #Se toman las rutas de ambos#
                    ruta_1 = rutas(k1, x_, t_)
                    ruta_2 = rutas(k2, x_, t_)
                    print(f"{k1}: {ruta_1}")
                    print(f"{k2}: {ruta_2}")

                    if len(ruta_1) > 2 and len(ruta_2) > 2:
                        mejor, x_, y_, t_, n_, r_ = lambda_11(k1,k2,ruta_1,ruta_2,x_,y_,t_,n_,r_,optimo_1+optimo_2)
                        if mejor == True:
                            cont = True
                            break

                        break


                    elif len(ruta_1) > 2 or len(ruta_2) > 2:
                        break

                #Si es que no se encontro ninguna mejor solucion se termina el bucle para el par de enfermeros#
                if cont == False:
                    break

    return x_,y_,t_,n_,r_


#intercambia rutas dentro de cada enfermero y busca la mejor solución#
def k_opt(x_,z1_,y_,t_,n_,r_):
    
    #Se itera sobre cada enfermero#
    for k in K:
        if z1_[k] == 1:

            #Iteramos hasta que no haya mejoria#
            while True:
                cont = False
                #Se guarda el costo que posee cada enfermero#
                optimo = sum(sum(B*d[i,j]*y_[i,j,k] for i in I+M+E+H+H_) for j in I+M+E+H+H_) 

                #Se crea la ruta para el enfermero#
                ruta = rutas(k, x_, t_)

                #Generamos todas las nuevas posibles combinaciones de rutas#
                for i,j in product(range(len(ruta)-1),range(len(ruta)-1)):
                    if j > i and i != 0 and j != 0 and i != len(ruta) and j != len(ruta):
                        nueva_ruta = ruta[:]
                        nueva_ruta[i], nueva_ruta[j] = nueva_ruta[j], nueva_ruta[i]

                        n_aux = n_
                        r_aux = r_

                        #Actualizamos valores de n_ y r_ si es necesario#
                        if ruta[i] in I_M and ruta[j] in I_M:
                            for p in M:
                                n_aux[p,ruta[i],k], n_aux[p,ruta[j],k] = n_[p,ruta[j],k],n_[p,ruta[i],k]

                        elif ruta[i] in M and ruta[j] in M:
                            for p in I_M:
                                n_aux[ruta[i],p,k], n_aux[ruta[j],p,k] = n_[ruta[j],p,k],n_[ruta[i],p,k]
                        
                        elif ruta[i] in I_E+I_P and ruta[j] in I_E+I_P:
                            for p in E:
                                r_aux[ruta[i],p,k], r_aux[ruta[j],p,k] = r_[ruta[j],p,k],r_[ruta[i],p,k]
                                
                        elif ruta[i] in E and ruta[j] in E:
                            for p in I_E+I_P:
                                r_aux[p,ruta[i],k], r_aux[p,ruta[j],k] = r_[p,ruta[j],k],r_[p,ruta[i],k]
                
                        #Para cada nueva ruta verificamos sus tiempos de atención#
                        fact, y_aux, t_aux = ruta_factible(k,nueva_ruta, n_aux, r_aux)

                        #Verificamos si es factible#
                        if fact == True:
                            nuevo = sum(sum(B*d[i,j]*y_aux[i,j,k] for i in I+M+E+H+H_) for j in I+M+E+H+H_) 

                            #Si posee una mejor solución se actualiza#
                            if nuevo < optimo:
                                cont = True
                                for i,j in product(I+M+E+H+H_, I+M+E+H+H_):
                                    y_[i,j,k] = y_aux[i,j,k]
                                for i in ruta:
                                    t_[i,k] = t_aux[i,k]
                                n_ = n_aux
                                r_ = r_aux
                                #Se cierra el bucle sobre las combinaciones#
                                break
                #Si no se encontro ninguna solucion mejor en las combinaciones se pasa al siguiente enfermero#
                if cont == False:
                    break                       

    return y_, t_

            
#Determina si la solución encontrada es factible para el modelo#
def factibilidad(x_,z1_,z2_,z3_,y_,t_,n_,r_):

    factible = True
    for i in I:
        if sum(x_[i,k] for k in K) != 1:
            factible = False
            print(1)

    for k in K:
        for i in H+H_:        
            if x_[i,k] != 1:
                factible = False
                print(2)

        if z1_[k] > sum(x_[i,k] for i in I):
            factible = False
            print(3)
            
        if G1*z1_[k] < sum(x_[i,k] for i in I):
            factible = False
            print(4)

        if z2_[k] > sum(x_[i,k] for i in I_M):
            factible = False
            print(5)

        if G2*z2_[k] < sum(x_[i,k] for i in I_M):
            factible = False
            print(6)

        if z3_[k] > sum(x_[i,k] for i in I_E+I_P):
            factible = False
            print(7)

        if G3*z3_[k] < sum(x_[i,k] for i in I_E+I_P):
            factible = False
            print(8)

        if sum(x_[i,k] for i in M) > sum(x_[i,k] for i in I_M):
            factible = False
            print(9)

        if sum(x_[i,k] for i in M) < z2_[k]:
            factible = False
            print(10)

        if sum(x_[i,k] for i in E) > sum(x_[i,k] for i in I_E+I_P):
            factible = False
            print(11)

        if sum(x_[i,k] for i in E) < z3_[k]:
            factible = False
            print(12)

        for i in I+M+E+H:
            if sum(y_[i,j,k] for j in I+M+E+H+H_) != x_[i,k]:
                factible = False
                print(13)

        for i in I+M+E+H_:
            if sum(y_[j,i,k] for j in I+M+E+H+H_) != x_[i,k]:
                factible = False
                print(14)

        if sum(y_[H_[0],j,k] for j in I+M+E+H+H_) != 0:
            factible = False
            print(15)
            
        if sum(y_[j,H[0],k] for j in I+M+E+H+H_) != 0:
            factible = False
            print(16)

        for i in I_M:
            if sum(n_[j,i,k] for j in M) != x_[i,k]:
                factible = False
                print(17)

        for i in M:
            if sum(n_[i,j,k] for j in I_M) < x_[i,k]:
                factible = False
                print(18)

            if sum(n_[i,j,k] for j in I_M) > G2*x_[i,k]:
                factible = False
                print(19)

        for i in I_E+I_P:
            if sum(r_[i,j,k] for j in E) != x_[i,k]:
                factible = False
                print(20)
        
        for i in E:
            if sum(r_[j,i,k] for j in I_E+I_P) < x_[i,k]:
                factible = False
                print(21)

            if sum(r_[j,i,k] for j in I_E+I_P) > G3*x_[i,k]:
                factible = False
                print(22)

        for i in I+M+E:
            if t_[i,k] > min(s[k]-t[i,H_[0]]-l[i],f[i])*x_[i,k]:
                factible = False
                print(23,k)

            if t_[i,k] < max(a[k]+t[H[0],i],b[i])*x_[i,k]:
                factible = False
                print(24)

        for i,j in product(I+M+E+H+H_,I+M+E+H+H_):
            if t_[i,k] + l[i] +t[i,j] > t_[j,k] + G4[i,j,k]*(1-y_[i,j,k]):
                factible = False
                print(25,i,j,k)
                print(x_[i,k])
                print(t_[i,k], t_[j,k], y_[i,j,k])

        if t_[H[0],k] < a[k]*z1_[k]:
            factible = False
            print(26)

        if t_[H_[0],k] > s[k]*z1_[k]:
            factible = False
            print(27,k)

        for i,j in product(M,I_M):
            if t_[i,k] > t_[j,k] + G5[i]*(1-n_[i,j,k]):
                factible = False
                print(28,i,j,k)
                print(n_[i,j,k])

            if t_[i,k] + l[i] + 60 < t_[j,k] - G6[i,j]*(1-n_[i,j,k]):
                factible = False
                print(29,i,j,k)
                print(n_[i,j,k])

        for i,j in product(I_E+I_P,E):
            if t_[i,k] > t_[j,k] + G7[i]*(1-r_[i,j,k]):
                factible = False
                print(30)

        for i,j in product(I_P,E):
            if t_[i,k] + l[i] + 60 < t_[j,k] - G8[i,j]*(1-r_[i,j,k]):
                factible = False 
                print(31)

    for k in K_1[1:]+K_2[1:]+K_E[1:]:
        if y_[H[0],H_[0],k] < y_[H[0],H_[0],k-1]:
            factible = False
            print(32)     

        for i in I:
           if x_[i,k] > sum(x_[j,k-1] for j in I if j < i):
               factible = False 
               print(33)

    return factible
import funciones
import pandas as pd
import ast

from funciones import actualizar_json
from Parametros import x, y, dia, caso

nombre_archivo = f"dias/{dia}/resultados{caso}_{dia}.csv"
data = pd.read_csv(nombre_archivo, encoding='latin1', delimiter=';')

trayectos = {}
trayecto_coord = {}
tiempo_dic = {}
cliente = funciones.client 

y_var = data[data["Variable"].str.contains("y")].copy()
y_var = y_var["Variable"].tolist()

for binaria in y_var:
    lista_str = binaria[binaria.find("("):]
    lista = ast.literal_eval(lista_str)
    origen = lista[0]
    destino = lista[1]
    enfermero = lista[2] 
    if enfermero in trayectos.keys():
        trayectos[enfermero].append([origen, destino])
    else:
        trayectos[enfermero] = [[origen, destino]]

for enfermero in trayectos:
    for trayecto in trayectos[enfermero]:
        origen = int(trayecto[0])
        destino = int(trayecto[1])
        directions_coordinates = [(y[origen], x[origen]), (y[destino], x[destino])]  
        route = cliente.directions(coordinates=directions_coordinates, profile='driving-car', format='geojson')
        routes_coords= [list(reversed(coord)) for coord in route['features'][0]['geometry']['coordinates']]
        if enfermero in trayecto_coord:
            trayecto_coord[enfermero].append([routes_coords, (origen, destino)])
        else:
            trayecto_coord[enfermero] = [[routes_coords, (origen, destino)]]
    actualizar_json(f"dias/{dia}/trayectos{caso}.json", {enfermero: trayecto_coord[enfermero]})

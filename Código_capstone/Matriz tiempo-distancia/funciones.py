import openrouteservice
import os.path
import json

client = openrouteservice.Client(key='5b3ce3597851110001cf624815274b1ff2eb4f6b85751e05aa36fac9')

def tiempo_distancia_api(coord1, coord2, idx1, idx2):
    try: 
        route = client.directions(coordinates=[coord1, coord2],  profile='driving-car', format='geojson')
        tiempo = route['features'][0]['properties']['segments'][0]['duration'] / 60  # en minutos
        distancia = route['features'][0]['properties']['segments'][0]['distance'] / 1000  # en km
        return [tiempo, distancia]
    except openrouteservice.exceptions.ApiError as e: #error de la api que no encuentra ruta
        print(f'El error es {e} con la coordenada {idx1} y {idx2}')
        return e
    except openrouteservice.exceptions.HTTPError as e:
        print(f'El error es {e} con la coordenada {idx1} y {idx2}')
        return e
    except openrouteservice.exceptions.Timeout as e:
        print(f'El error es {e} con la coordenada {idx1} y {idx2}')
        return e
    except Exception as e:
        print(f'El error es {e} con la coordenada {idx1} y {idx2}')
        return e

def actualizar_json(archivo, dic):
    if os.path.exists(archivo):
        try:
            with open(archivo, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = {}
    else:
        data = {}
    
    data.update(dic)
    
    with open(archivo, 'w') as f:
        json.dump(data, f, indent=4)

def eliminar_error(diccionarios, coordenada, archivo_nombre):
    del diccionarios[(coordenada[0], coordenada[1])]
    mi_diccionario = {str(clave): valor for clave, valor in diccionarios.items() if isinstance(clave, tuple)}
    mi_diccionario.update({clave: valor for clave, valor in diccionarios.items() if not isinstance(clave, tuple)})
    with open(archivo_nombre, 'w') as archivo:
        json.dump(mi_diccionario, archivo, indent=4)

        
def buscar_id(coordenada, x, y):
    for idx in x:
        if x[idx] == coordenada[0] and y[idx] == coordenada[1]:
            return idx
    return None
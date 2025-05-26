import requests
from bs4 import BeautifulSoup
import pandas as pd
from sqlalchemy import create_engine

# URL principal para el scraping
URL_RAIZ = "https://es.wikipedia.org"

# Datos de conexión a SQL Server
SERVER = 'MSI'
DATABASE = 'TRABAJOS'
engine = create_engine(f'mssql+pyodbc://{SERVER}/{DATABASE}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes')




def obtenerEnlaces(url):
    """
    Extrae todos los enlaces (href) de una página web dada.
    
    Args:
        url (str): URL de la página web
    
    Returns:
        list: Lista de enlaces únicos encontrados en la página
    """
    try:
        respuesta = requests.get(url) # Se realiza la conexión a la página 
        respuesta.raise_for_status() # Retorna el Status de la conexión
    except Exception as e:
        print(f"Error al acceder a {url}: {e}")
        return []

    html = BeautifulSoup(respuesta.text, 'html.parser')  # Se procesa la respuesta para poder buscar y extraer elementos de forma sencilla
    enlaces = [a['href'] for a in html.find_all('a', href=True)] # Para todos las etiquetas 'a', se extrae el atributo 'href'
    return list(dict.fromkeys(enlaces)) # Se retorna una lista de enlaces eliminando los duplicados




def descomponerInformacion(url):
    """
    Recorre los enlaces internos de una página y extrae títulos y subtítulos.

    Args:
        url (str): URL raíz para iniciar la recolección

    Returns:
        dict: Diccionario con las columnas Enlace, Texto y Tipo
    """
    enlaces = obtenerEnlaces(url) # Se obtienen todos los enlaces a partir de un primer enlace
    datos = {'Enlace': [], 'Texto': [], 'Tipo': []} # Se crea el diccionario que almacena la información

    for enlace in enlaces: # Se recorren todos los enlaces
        if (enlace[0]=='/'): # Se verifica el formato del enlace 
            enlace_completo = url + enlace  
            
            try:
                respuesta = requests.get(enlace_completo) # Se realiza la conexión a la página 
                respuesta.raise_for_status() # Retorna el Status de la conexión
                html = BeautifulSoup(respuesta.text, 'html.parser') # Se procesa la respuesta para poder buscar y extraer elementos de forma sencilla
                
                for etiqueta, tipo in [('h1', 'Titulo'), ('h2', 'Subtitulo')]: 
                    for item in html.find_all(etiqueta):
                        texto = item.get_text(strip=True)                           #Para todas las etiquetas 'h1' y 'h2' se extrae la información
                        if texto:                                                   #Dicha información se almacena en el diccionario
                            datos['Enlace'].append(enlace_completo)
                            datos['Texto'].append(texto)
                            datos['Tipo'].append(tipo)
            except Exception as e:
                print(f"No se pudo ingresar al enlace {enlace_completo}: {e}")
    
    return datos




def almacenarDatos(dic, engine):
    """
    Almacena un diccionario de datos en una tabla SQL llamada 'Busquedas'.

    Args:
        dic (dict): Diccionario con las claves Enlace, Texto y Tipo
        engine (sqlalchemy.engine.base.Engine): Motor de conexión a la base de datos

    Returns:
        bool: True si se insertó correctamente, False si hubo error
    """
    if not dic['Enlace']:
        print("No hay datos para insertar en la base de datos.")
        return False

    try:
        df = pd.DataFrame(dic) # Se crea el Dataframe con los datos a partir del diccionario creado en la función 'descomponerInformacion'
        df.to_sql('Busquedas', con=engine, if_exists='replace', index=False) # Se almacenan los datos en la tabla 'Busquedas' utilizando un replace si ya existe la tabla
        print("Datos insertados correctamente en la base de datos.")
    except Exception as e:
        print(f"Error al almacenar los datos: {e}")
        return False

    return True




if __name__ == '__main__':
    datos = descomponerInformacion(URL_RAIZ)
    almacenarDatos(datos, engine)

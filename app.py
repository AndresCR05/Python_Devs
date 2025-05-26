from flask import Flask, render_template, request
import pandas as pd
from sqlalchemy import create_engine, text

app = Flask(__name__)


# Datos de conexión a SQL Server
SERVER = 'MSI'
DATABASE = 'TRABAJOS'

engine = create_engine(f'mssql+pyodbc://{SERVER}/{DATABASE}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes')



def consultaPersonalizada(texto, categoria, engine):
    """
    Realiza consultas individuales a la tabla 'Busquedas'mediante Pandas.

    Args:
        texto (String): Texto a buscar en la consulta
        categoria (String): Tipo de información a consultar (título o subtitulo)
        engine (sqlalchemy.engine.base.Engine): Motor de conexión a la base de datos

    Returns:
        object: Dataframe con los resultados de la consulta
    """
    try:
        if categoria == "Categoria":
            query = text("SELECT Enlace, Texto, Tipo FROM TRABAJOS.DBO.Busquedas WHERE Texto LIKE :texto") # Se define el query de la consulta de la base de datos
            return pd.read_sql(query, engine, params={"texto": f"%{texto}%"}) # Se añaden los parámetros y se ejecuta la consulta, retornando el Dataframe resultante
        else:
            query = text("SELECT Enlace, Texto, Tipo FROM TRABAJOS.DBO.Busquedas WHERE Tipo = :categoria AND Texto LIKE :texto") # Se define el query de la consulta de la base de datos
            return pd.read_sql(query, engine, params={"categoria": categoria, "texto": f"%{texto}%"}) # Se añaden los parámetros y se ejecuta la consulta, retornando el Dataframe resultante
    except Exception as e:
        print(f"Error al consultar los datos: {e}")
        return pd.DataFrame({'Enlace': [], 'Texto': [], 'Tipo': []})  # En caso de error en la conexión, se crea un Dataframe vacío con las columnas y se retorna




def consultaGlobal(engine):
    """
    Realiza la consulta global de la tabla 'Busquedas' mediante Pandas.

    Args:
        engine (sqlalchemy.engine.base.Engine): Motor de conexión a la base de datos

    Returns:
        object: Dataframe con los resultados de la consulta
    """
    try:
        query = "SELECT Enlace, Texto, Tipo FROM TRABAJOS.DBO.Busquedas" # Se define el query de la consulta de la base de datos
        return pd.read_sql(query, engine) # Se ejecuta la consulta, retornando el Dataframe resultante
    except Exception as e:
        print(f"Error al consultar los datos: {e}")
        return pd.DataFrame({'Enlace': [], 'Texto': [], 'Tipo': []}) # En caso de error en la conexión, se crea un Dataframe vacío con las columnas y se retorna



def getFormulario():
    """Obtener los valores enviados desde el formulario HTML

    Returns:
        [tuple]: Retorna una tupla con los valores obtenidos de los campos 'Texto' y 'Categoria'
    """
    texto = request.form.get('texto')   # Se obtienen los valores del request
    categoria = request.form.get('categoria')
    return (texto, categoria)





@app.route('/', methods=['GET', 'POST']) #Métodos que se utilizaran por la función index
def index():
    """
    Ruta principal de la aplicación Flask. Muestra el formulario y procesa los resultados.

    Returns:
        Response: Renderiza la plantilla HTML con los resultados de la búsqueda
                  o con todos los datos si es una solicitud GET.
    """
    if request.method == 'POST':
        texto, categoria = getFormulario()
        df = consultaPersonalizada(texto, categoria, engine)
        return render_template('index.html', columnas=df.columns, filas=df.values.tolist())
    else:
        df = consultaGlobal(engine)
        return render_template('index.html', columnas=df.columns, filas=df.values.tolist())


if __name__ == '__main__':
    app.run(debug=True)


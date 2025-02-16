import os
import difflib
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import tweepy
import datetime
import time


load_dotenv()  # Carga las variables de entorno desde un archivo .env

# Validar que todas las variables necesarias estén presentes en las variables de entorno
required_env_vars = ['API_KEY', 'API_SECRET', 'BEARER_TOKEN', 'ACCESS_TOKEN', 'ACCESS_TOKEN_SECRET']
for var in required_env_vars:
    if not os.getenv(var):
        raise ValueError(f"Falta la variable de entorno: {var}")
    
# Configuración de carga de crednciales
api_key = os.getenv('API_KEY')
api_secret = os.getenv('API_SECRET')
bearer_token = os.getenv('BEARER_TOKEN')
access_token = os.getenv('ACCESS_TOKEN')
access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')

# Archivos para guardar títulos
archivo_antiguo = "titulos_formateados.txt"
archivo_nuevo = "titulos_formateados_temporal.txt"  # Temporal, se sobrescribe diariamente

# URL del sitio web para buscar los títulos
url = "https://firstatack.github.io/"  # Reemplace con su URL real

# Función para comparar archivos
def comparar_archivos():
    # Lee los archivos antiguo y nuevo
    try:
        with open(archivo_antiguo, 'r', encoding='utf-8') as f:
            lineas_antiguas = f.readlines()
    except FileNotFoundError:
        lineas_antiguas = []

    with open(archivo_nuevo, 'r', encoding='utf-8') as f:
        lineas_nuevas = f.readlines()

    # Compara línea por línea
    diferencia = list(difflib.unified_diff(lineas_antiguas, lineas_nuevas, fromfile=archivo_antiguo, tofile=archivo_nuevo))

    # Obtén los nuevos posts (los que están en el archivo nuevo, pero no en el antiguo)
    if lineas_nuevas:
        nuevos_posts = [linea.strip() for linea in lineas_nuevas if linea not in lineas_antiguas]
    else:
        print(f"No hay títulos en el archivo nuevo ({archivo_nuevo}).")
        return

    # Verifica si hay nuevos posts y envía un tweet para cada uno
    if nuevos_posts:
        for post in nuevos_posts:
            enviar_tweet(post)
    else:
        print(f"No hay nuevos títulos para hoy.")

    # Actualiza el archivo antiguo para la próxima comparación
    with open(archivo_antiguo, 'w', encoding='utf-8') as f:
        f.writelines(lineas_nuevas)


# Función para enviar un tweet
def enviar_tweet(ultimo_post):
    # Autentíquese con la API de Twitter
    cliente = tweepy.Client(bearer_token, api_key, api_secret, access_token, access_token_secret)

    # Formatee el tweet con el contenido personalizado
    mensaje_tweet = (f"#NoTePierdasNada \nOtro manual tutorial sobre seguridad informática, automatización, #CTF #writeUp \n\n"
                     f"{ultimo_post} \n\n#Pentesting #kali_linux #auto_tweet_bot #Hacking \n\n¡Sígueme para estar al día!")

    # Envíe el tweet con el mensaje formateado
    try:
        cliente.create_tweet(text=mensaje_tweet)
        print("Tweet enviado!")
    except Exception as e:
        print(f"Error al enviar tweet: {e}")

# Función para obtener y guardar títulos
def obtener_titulos():
    # Obtenga el contenido del sitio web
    respuesta = requests.get(url)
    sopa = BeautifulSoup(respuesta.content, 'html.parser')

    # Obtenga los últimos 5 elementos de enlace
    ultimos_5_enlaces = sopa.find_all('a', href=lambda href: href and href.startswith('/posts/'))[-5:]

    # Abrir el archivo de salida en modo de escritura para limpiar el archivo antes de añadir los nuevos títulos
    with open(archivo_nuevo, 'w', encoding='utf-8') as file:
        for enlace in ultimos_5_enlaces:
            titulo = enlace.text.strip()

            # Divida el título en la primera coma
            partes_titulo = titulo.split(',')

            # Extraer y formatear la primera cadena
            primera_cadena = partes_titulo[0].strip().lower()  # Convertir a minúsculas
            titulo_formateado = f"https://firstatack.github.io/posts/{primera_cadena}"

            # Escriba el título formateado en el archivo
            file.write(titulo_formateado + '\n')

    print(f"Títulos formateados guardados en: {archivo_nuevo}")

# Ejecución principal
def trabajo_diario():
    obtener_titulos()  # Obtenga y guarde los títulos iniciales al ejecutar el script por primera vez
    comparar_archivos()  # Comparar los archivos y enviar el tweet si es necesario

# Ejecutar las funciones una vez y finalizar el script
trabajo_diario()

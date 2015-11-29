# -*- coding: utf-8 -*-
import calendar
import datetime
import urllib
import urllib2
import re
from flask import Flask
app = Flask(__name__)

# código para parar el servidor elegantemente con CTRL C (se puede borrar
# en versión final )
import signal
import sys


def signal_handler(signal, frame):
    print("\nParando Servidor al recibir señal: " + str(signal))
    sys.exit()
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
# FIN código para parar el servidor...

# definición de ruta raíz.


@app.route('/')
def root():
    return app.send_static_file('index.html')

# definición de ruta con fecha de consulta


@app.route('/<fecha>/<numero_jugado_str>/<serie_jugada_str>')
def numero_premiado(fecha, numero_jugado_str, serie_jugada_str):
    # texto respuesta ante error de formato
    ERROR_FORMATO = 'Fecha Incorrecta. Por favor especifique la fecha a consultar con formato AAAA-MM-DD,' + \
        ' el número y serie a consultar. Ejemplo : http://127.0.0.1:5000/2015-11-13/98190/007'
    # chequear longitud de fecha, numero y serie correcta
    if len(fecha) == 10 and len(numero_jugado_str) == 5 and len(serie_jugada_str) == 3:
        # intentar leer año mes dia, numero y serie, si no se puede, hay error de
        # formato
        try:
            anyo = int(fecha[0:4])
            mes = int(fecha[5:7])
            dia = int(fecha[8:10])
            numero_jugado = int(numero_jugado_str)
            serie_jugada = int(serie_jugada_str)
            # chequear logica de fecha (1996 primer año registrado en página de
            # resultados)
            if mes > 12 or dia > 31 or mes < 1 or dia < 1 or anyo < 1996:
                return ERROR_FORMATO
            fecha_actual = datetime.datetime.now()
            if anyo > fecha_actual.year or (anyo == fecha_actual.year and mes > fecha_actual.month) or (anyo == fecha_actual.year and mes == fecha_actual.month and dia >= fecha_actual.day):
                return 'Fecha futura o actual, sorteo aún no realizado'
        except:
            return ERROR_FORMATO

        # POR HACER: Comprobar si el número premiado para esta fecha está en
        # base de datos (mongodb (parte avanzada)? o online) y sacarlo de ahi
        # sin hacer petición a página de resultados

        # hacer una request HTTP GET a la página de resultados, indicando
        # fecha.
        url = 'http://www.euromillon.net/cupononce/index-cupononce.php?vista=ver-escrutinio.php&fecha=' + \
            str(fecha)
        # almacenar respuesta en variable
        respuesta = urllib2.urlopen(url).read()
        # buscar expresión regular de 5 dígitos con guiones intercalados en la
        # respuesta
        numero = re.search(r'\d-\d-\d-\d-\d', respuesta)
        # buscar expresión regular de serie (texto HTML seguido de entre uno y tres
        # dígitos seguidos de un guión) en la respuesta
        serie = re.search(
            r'<td> Serie - Series adicionales </td> <td>\d{1,3}-', respuesta)

        # si hay coincidencia, comprobar numero jugado
        if numero and serie:
            # extraer coincidencia
            numero = numero.group()
            serie = serie.group()
            # eliminar todo menos dígitos
            numero = re.sub(r'\D', "", numero)
            serie = re.sub(r'\D', "", serie)
            # pasar a entero
            numero = int(numero)
            serie = int(serie)

            # comprobar si la fecha es viernes y por tanto cuponazo
            cuponazo = False
            if calendar.weekday(anyo, mes, dia) == 4:
                cuponazo = True

            premio = "0"
            if numero == numero_jugado:
                if serie == serie_jugada and cuponazo:
                    premio = "9.000.000"
                elif cuponazo:
                    premio = "30.000"
                else:
                    premio = "35.000"
            elif numero == numero_jugado + 1 or numero == numero_jugado - 1 and not cuponazo:
                premio = "500"
            elif str(numero)[1:5] == str(numero_jugado)[1:5]:
                if cuponazo:
                    premio = "500"
                else:
                    premio = "200"
            elif str(numero)[2:5] == str(numero_jugado)[2:5]:
                if cuponazo:
                    premio = "50"
                else:
                    premio = "20"
            elif (str(numero)[0] == str(numero_jugado)[0] and not cuponazo) or str(numero)[4] == str(numero_jugado)[4]:
                return "El número " + str(numero_jugado) + " fue premiado el día " + str(fecha) + " con el reintegro"

            if premio != "0":
                return "Enhorabuena, el número " + str(numero_jugado) + " con serie " + str(serie_jugada) + " fue premiado el día " + str(fecha) + " con " + premio + " euros"
            else:
                return "El número " + str(numero_jugado) + " con serie " + str(serie_jugada) + " no fue premiado el día " + str(fecha)

        else:
            return 'En esta fecha no hubo número premiado o ha ocurrido un error con el servicio de resultados'
    else:
        return ERROR_FORMATO

# PARA PARTE AVANZADA (opcional):

# definición de ruta para poblar base de datos


@app.route('/poblarbasededatos')
def poblar():
    # POR HACER: HACER ESTO EN BUCLE PARA AÑOS 1996-2015 y almacenar
    # en BD (mongoDB? o online)

    # hacer una request HTTP POST a la página de resultados con los datos
    # solicitados
    url = 'http://www.euromillon.net/cupononce/index-cupononce.php?vista=listado-sorteos.php'
    valores = {'year': '1996',
               'dia': 'I',
               'enviado': 'Ok'}
    # codificar valores: 'enviado=Ok&dia=I&year=2015'
    datos = urllib.urlencode(valores)
    # realizar petición POST con la url y los datos en el body de a
    # petición
    peticion = urllib2.Request(url, datos)
    # almacenar respuesta
    respuesta = urllib2.urlopen(peticion).read()

    # PROCESAR RESPUESTA (EN BUCLE 1996-2015), EXTRAER NUMEROS Y ALMACENAR EN
    # BD

    return 'Base de datos poblada (1996-2015)'


# FIN PARA PARTE AVANZADA


# ejecución de app (añadido el host nulo para que se pueda acceder en red,
# no solo localmente)
if __name__ == '__main__':
    app.run(host='0.0.0.0')

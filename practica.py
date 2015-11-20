# -*- coding: utf-8 -*-
import calendar, datetime
import urllib2
from flask import Flask
app = Flask(__name__)

#código para parar el servidor elegantemente con CTRL C (se puede borrar en versión final)
import signal
import sys
def signal_handler(signal, frame):
	print("\nParando Servidor al recibir señal: " + str(signal));
	sys.exit()
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
#FIN código para parar el servidor...

NUMERO_JUGADO = 98190

#definición de ruta raíz.
@app.route('/')
def root():
    return 'Por favor especifique la fecha a consultar con formato AAAA-MM-DD. Ejemplo : http://127.0.0.1:5000/2015-11-13'

#definición de ruta con fecha de consulta
@app.route('/<fecha>')
def numero_premiado(fecha):
	# chequear longitud de fecha correcta
	if len(fecha) == 10:
		#intentar leer año mes y dia, si no se puede, hay error de formato
		try:
			anyo = int(fecha[0:4])
			mes = int(fecha[5:7])
			dia = int(fecha[8:10])
			#chequear logica de fecha (1939 primer sorteo de la ONCE, usado para evitar años absurdos)
			if mes > 12 or dia > 31 or mes < 1 or dia < 1 or anyo < 1939:
				return 'Fecha Incorrecta. Por favor especifique la fecha a consultar con formato AAAA-MM-DD. Ejemplo : http://127.0.0.1:5000/2015-11-13'
			fecha_actual = datetime.datetime.now()
			if anyo > fecha_actual.year or (anyo == fecha_actual.year and mes > fecha_actual.month) or  (anyo == fecha_actual.year and mes == fecha_actual.month and dia >= fecha_actual.day):
				return 'Fecha futura o actual, sorteo aún no realizado, McFly.'
		except:
			return 'Por favor especifique la fecha a consultar con formato AAAA-MM-DD. Ejemplo : http://127.0.0.1:5000/2015-11-13'
		#con el año, mes y dia, sacar el dia de la semana (cuponazo el viernes). Si no es posible, hay error de formato
		if calendar.weekday(anyo, mes, dia) == 0:
			diadelasemana = "Lunes"
		elif calendar.weekday(anyo, mes, dia) == 1:
			diadelasemana = "Martes"
		elif calendar.weekday(anyo, mes, dia) == 2:
			diadelasemana = "Miercoles"
		elif calendar.weekday(anyo, mes, dia) == 3:
			diadelasemana = "Jueves"
		elif calendar.weekday(anyo, mes, dia) == 4:
			diadelasemana = "cuponazo-once"
		elif calendar.weekday(anyo, mes, dia) == 5:
			diadelasemana = "Sabado"
		elif calendar.weekday(anyo, mes, dia) == 6:
			diadelasemana = "Domingo"
		else :
			return 'Por favor especifique la fecha a consultar con formato AAAA-MM-DD. Ejemplo : http://127.0.0.1:5000/2015-11-13'
		#hacer una request HTTP GET a la página de resultados, indicando fecha y dia de la semana para que funcione su script.
		url = 'http://www.resultados11.es/' + diadelasemana +'.php?del-dia=' + str(fecha)
		# almacenar respuesta en variable
		respuesta = urllib2.urlopen(url).read()
		# encontrar seccion de la respuesta en HTML donde está el número premiado del día
		indice_numero = respuesta.find('<div id="bolas">')
		# si existe, eliminar el código alrededor del número (espacios y tags HTML). Si no hay error o no hay numero premiado.
		if indice_numero > 0:
			numero = respuesta[indice_numero+20:indice_numero+90]
			numero = numero.strip()
			numero = numero.replace(" ", "")
			numero = numero.replace("<li>", "")
			numero = numero.replace("</li>", "")
			# comprobar que es un numero
			numero_int = -1
			try:
				numero_int = int(numero)
			except :
				return 'No hay datos para esta fecha, pruebe otra'	
			# si lo es compararlo con el número que se juega (definido arriba en NUMERO_JUGADO) y otros premios
			if numero_int == NUMERO_JUGADO:
				return "Enhorabuena, el número " + str(NUMERO_JUGADO) + " fue premiado el día " + str(fecha) + " con 35.000 euros"
			elif numero_int == NUMERO_JUGADO + 1 or numero_int == NUMERO_JUGADO - 1 :
				return "Enhorabuena, el número " + str(NUMERO_JUGADO) + " fue premiado el día " + str(fecha) + " con 500 euros"
			elif numero[1:5] == str(NUMERO_JUGADO)[1:5] :
				return "Enhorabuena, el número " + str(NUMERO_JUGADO) + " fue premiado el día " + str(fecha) + " con 200 euros"
			elif numero[2:5] == str(NUMERO_JUGADO)[2:5] :
				return "El número " + str(NUMERO_JUGADO) + " fue premiado el día " + str(fecha) + " con 20 euros"
			elif numero[0] == str(NUMERO_JUGADO)[0] or numero[4] == str(NUMERO_JUGADO)[4] :
				return "El número " + str(NUMERO_JUGADO) + " fue premiado el día " + str(fecha) + " con el reintegro (1.50 euros)"
			else:
				return "El número " + str(NUMERO_JUGADO) + " no fue premiado el día " + str(fecha)
					
		else :
			return 'En esta fecha no hubo número premiado o ha ocurrido un error con el servicio de resultados'
	else :
		return 'Por favor especifique la fecha a consultar con formato AAAA-MM-DD. Ejemplo : http://127.0.0.1:5000/2015-11-13'

#ejecución de app
if __name__ == '__main__':
    app.run()
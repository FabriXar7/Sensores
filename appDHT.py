import time
import sqlite3
import Adafruit_DHT
import smtplib
import sys
import os
import spidev
import glob
import time
import csv
from datetime import datetime
import gspread
from email.mime.text import MIMEText
from pysnmp.hlapi import *


dbname = 'sensorsData.db'
sampleFreq = 73 # tiempo en segundos
highTemp = 32
lowSignal = 1
email = 'nombre@email.com'
password = '##########'


# obtener los datos de los sensores

def getDHTdata():	
	DHT22Sensor = Adafruit_DHT.DHT22
	DHTpin1 = 22
	DHTpin2 = 3
	DHTpin3 = 2
	DHTpin4 = 27
	hum1, temp1 = Adafruit_DHT.read_retry(DHT22Sensor, DHTpin1)
	hum2, temp2 = Adafruit_DHT.read_retry(DHT22Sensor, DHTpin2)
	hum3, temp3 = Adafruit_DHT.read_retry(DHT22Sensor, DHTpin3)
	hum4, temp4 = Adafruit_DHT.read_retry(DHT22Sensor, DHTpin4)
	db = '0'
	other = '0'

# obtener datos del decoder satelital Cisco D9854
	iterator = getCmd(SnmpEngine(),
					CommunityData('public'),
					UdpTransportTarget(('192.168.0.99', 161)),
					ContextData(),
					ObjectType(ObjectIdentity('1.3.6.1.4.1.1429.2.2.6.5.11.1.1.4.0')))

	errorIndication, errorStatus, errorIndex, varBinds = iterator

	for varBind in varBinds:  
			texto = str(varBind)
			db = '0'
			db = adjustDb(texto[-3:])
			other = texto[-3:]
		
	
	if hum1 is not None and temp1 is not None and temp2 is not None and hum2 is not None and temp3 is not None and hum3 is not None and temp4 is not None and hum4 is not None and db is not None and other is not None:
		hum1 = adjustHum(abs(round(hum1, 1)))
		temp1 = adjustValue(abs(round(temp1, 1)))
		hum2 = adjustHum(abs(round(hum2, 1)))
		temp2 = adjustValue(abs(round(temp2, 1)))
		hum3 = adjustHum(abs(round(hum3, 1)))
		temp3 = adjustValue(abs(round(temp3, 1)))
		hum4 = adjustHum(abs(round(hum4, 1)))
		temp4 = adjustValue(abs(round(temp4, 1)))
		db = db
		other = other		
		logData (temp1, hum1, temp2, hum2,temp3, hum3, temp4, hum4, db, other)
		logGData (temp1, hum1, temp2, hum2,temp3, hum3, temp4, hum4, db, other)
		temp = (temp1 + temp2 + temp3 + temp4) / 4 
		
	#	if (temp > highTemp):
	#		sendMail(temp, db)
			
	#	if (int(float(db)) < lowSignal):
	#		sendMail(temp, db)

# Enviar correo si la temperatura es muy alta o la señal muy baja
def sendEmail (temp, db):
	
	if (temp > highTemp):
		subject = "ALERTA! La temperatura del DataCenter es: {} ".format(temp)
		body = "ALERTA! Temperatura actual muy alta: {} ".format(temp)
	else:	
		subject = "ALERTA! La Señal del TelePuerto es: {} ".format(db)
		body = "ALERTA! Señal del telepuerto actual muy baja: {} ".format(db)
		
		
	try:
		server = smtplib.SMTP('smtp.gmail.com', 587) 
		server.ehlo()
		server.starttls()
		server.ehlo
		# Login
		server.login(email, password)
    
		sender = email
		recipients = ['nombre1@email.com', 'nombre2@email.com']
		msg = MIMEText(body)
		msg['Subject'] = subject
		msg['From'] = sender
		msg['To'] = ", ".join(recipients) 

		# Enviar el correo
		server.sendmail(sender, recipients, msg.as_string())
		server.quit()
	except:
		print("failed to send mail")		
		
# guardar datos de los sensores en la base de datos
def logData (temp1, hum1, temp2, hum2,temp3, hum3, temp4, hum4, db, other):	
	conn=sqlite3.connect(dbname)
	curs=conn.cursor()
	curs.execute("INSERT INTO DHT_data values(datetime('now'), (?), (?),  (?), (?),  (?), (?),  (?), (?),  (?), (?))", (temp1, hum1, temp2, hum2,temp3, hum3, temp4, hum4, db, other))
	conn.commit()
	conn.close()

# guardar datos de los sensores en google sheet
def logGData (temp1, hum1, temp2, hum2, temp3, hum3, temp4, hum4, db, other):
	fecha = str(datetime.now())
	from google.oauth2.service_account import Credentials

	scopes = [
		'https://www.googleapis.com/auth/spreadsheets',
		'https://www.googleapis.com/auth/drive'
	]

	credentials = Credentials.from_service_account_file(
		'sensores-123456-xxx123x12x12.json',
		scopes=scopes
	)

	gc = gspread.authorize(credentials)


	sh = gc.open("Sensores")

	worksheet = sh.get_worksheet(0)
	
	worksheet.update([[fecha, temp1, hum1, temp2, hum2, temp3, hum3, temp4, hum4, db, other]],'A2:K2')
	
	#print(sh.sheet1.get('A1'))

	#worksheet = gc.open(sheet).sheet1
	#values = [datetime.datetime.now(), temp1, hum1, temp2, hum2,temp3, hum3, temp4, hum4, db, other]
	#worksheet.append_row(values)
	#time.sleep(5)
	#except:
		#print('Oops! ver Internet o login')
		#sys.exit()


# ajustar los valores erroneos
def adjustValue(valor):
	if ((valor > 20) and (valor < 40)):
		valor = valor
	else:
		valor = 29
	return valor

# ajustar los valores erroneos de humedad
def adjustHum(valor):
	if ((valor > 0) and (valor < 100)):
		valor = valor
	else:
		valor = 50
	return valor		

# ajustar los valores erroneos de Db
def adjustDb(valor):
	if ((valor == "n/a")):
		valor = "0"
	else:
		valor = valor
	return valor	
	
# mostrar los datos de la base de datos
def displayData():
	conn=sqlite3.connect(dbname)
	curs=conn.cursor()
	print ("\nContenido total de la base de datos:\n")
	for row in curs.execute("SELECT * FROM DHT_data"):
		print (row)
	conn.close()
	
	
# funcion principal
def main():
	#for i in range (0,3):
	getDHTdata()
	time.sleep(sampleFreq)
	displayData()
# Ejecutar el programa 
main()

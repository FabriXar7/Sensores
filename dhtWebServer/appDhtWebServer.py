from flask import Flask, render_template, request
app = Flask(__name__)
import sqlite3
# Obtiene los datos de la base de datos
def getData():
	conn=sqlite3.connect('../sensorsData.db')
	curs=conn.cursor()
	for row in curs.execute("SELECT * FROM DHT_data ORDER BY timestamp DESC LIMIT 1"):
		time = str(row[0])
		temp1 = row[1]
		temp2 = row[3]
		temp3 = row[5]
		temp4 = row[7]
		hum1 = row[2]
		hum2 = row[3]
		hum3 = row[6]
		hum4 = row[8]
		db = row[9]
		hum = round((hum1 + hum2 + hum3 + hum4) / 4)
	conn.close()
	return time, temp1, temp2, temp3, temp4, hum, db
# main route 
@app.route("/")
def index():	
	time, temp1, temp2, temp3, temp4, hum, db = getData()
	templateData = {
		'time': time,
		'temp1': temp1,
		'temp2': temp2,
		'temp3': temp3,
		'temp4': temp4,
		'hum': hum,
		'db': db
	}
	return render_template('index.html', **templateData)
if __name__ == "__main__":
   app.run(host='0.0.0.0', port=80, debug=False)

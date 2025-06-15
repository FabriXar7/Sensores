import os
import datetime
from redmail import EmailSender
import numpy as np
import matplotlib
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt2
from datetime import datetime
from datetime import timedelta

fecha = datetime.now()
ayer = fecha - timedelta(days=1)  
ayer = ayer.strftime("%d-%m-%Y")

# Open the database
try:
    conn = sqlite3.connect('sensorsData.db')
    cursor = conn.cursor()
except sqlite3.Error as e:
    # If things go wrong
    print("Error connecting to the database:", e)


# Retrieve data from the table 1 week
cursor.execute('SELECT timestamp, temp1, temp2, temp3, temp4, db FROM DHT_data WHERE date(timestamp) = date("now", "-1 days")') #ORDER BY timestamp DESC LIMIT 1440
results = cursor.fetchall()

# Separate the data into lists:
tiempo = [result[0] for result in results]

temp1 = [abs(result[1]) for result in results]

temp2 = [abs(result[2]) for result in results]

temp3 = [abs(result[3]) for result in results]

temp4 = [abs(result[4]) for result in results]

dbs = [abs(result[5]) for result in results]



# Create a graph of the data1
fig, ax = plt.subplots()
xtick_labels = [23,24,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22]
ytick_labels = [0,10,15,20,25,30,35,40,40]
ax.set(xlabel='Hora', ylabel='Temperatura', title='Temperatura del DataCenter del ' + ayer)
ax.grid(True)
plt.yticks(range(0,40,5))
plt.xticks(range(0,1440,60), xtick_labels)
ax.plot(tiempo,temp1, label="Pasillo 1")
ax.plot(tiempo,temp2, label="Pasillo 2")
ax.plot(tiempo,temp3, label="Pasillo 3")
ax.plot(tiempo,temp4, label="Pasillo 4")
plt.legend(loc="lower left")
plt.savefig('/home/sudo/Sensors-Database/temp.png')

# Create a graph of the data2
fig2, ax2 = plt2.subplots()
ax2.set(xlabel='Hora', ylabel='dB', title='Señal de la portadora ' + ayer)
ax2.grid(True)
plt2.xticks(range(0,1440,60), xtick_labels)
ax2.plot(tiempo,dbs)
plt2.savefig('/home/sudo/Sensors-Database/db.png')

#Send the email

email = EmailSender(
    host='smtp.gmail.com',
    port=587,
    username='nombre@email.com',
    password='##############'
)

email.send(
    subject="Datos de Sensores del DataCenter",
    sender="nombre@email.com",
    receivers=['nombre1@email.com, nombre2@email.com'],    
    text="Valores de los sensores del DataCenter generados",
    html="""
        <h1>Datos de los Sensores del DataCenter generados:</h1>
        {{ my_image1 }}
        {{ my_image2 }}
        <h1>@DataCenter 2025</h1>
    """,
    body_images={
        'my_image1': '/home/sudo/Sensors-Database/temp.png',
        'my_image2': '/home/sudo/Sensors-Database/db.png',
    }
)

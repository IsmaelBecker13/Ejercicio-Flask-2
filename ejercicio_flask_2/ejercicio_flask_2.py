from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
import os
import logging
import asyncio
import ssl
import certifi
import aiomqtt
import traceback
from werkzeug.middleware.proxy_fix import ProxyFix

# Logging
logging.basicConfig(format='%(asctime)s - CRUD - %(levelname)s - %(message)s', level=logging.INFO)

# Flask app
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
app.secret_key = os.environ["FLASK_SECRET_KEY"]

# MySQL config
app.config["MYSQL_USER"] = os.environ["MYSQL_USER"]
app.config["MYSQL_PASSWORD"] = os.environ["MYSQL_PASSWORD"]
app.config["MYSQL_DB"] = os.environ["MYSQL_DB"]
app.config["MYSQL_HOST"] = os.environ["MYSQL_HOST"]

mysql = MySQL(app)

@app.route('/')
def index():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT DISTINCT sensor_id FROM mediciones")
        ids = [row[0] for row in cur.fetchall()]
        cur.close()
        return render_template("index.html", ids_dispositivos=ids)
    except Exception as e:
        logging.error("Error al obtener IDs:\n" + traceback.format_exc())
        flash("Error al cargar los IDs desde la base de datos.")
        return render_template("index.html", ids_dispositivos=[])

@app.route("/controlar_topico", methods=["POST"])
def controlar_topico():
    selected_sensor_id = request.form.get("selected_sensor_id")
    topico = request.form.get("topico")
    valor = request.form.get("valor", "")

    if not selected_sensor_id or not topico:
        flash("Faltan datos para controlar el tópico.")
        return redirect(url_for('index'))

    topico_completo = f"{selected_sensor_id}/{topico}"

    try:
        asyncio.run(publicar_mqtt(topico_completo, valor))
        flash(f"Control enviado a '{topico_completo}' con valor: '{valor}'")
    except Exception as e:
        logging.error("Error al enviar MQTT:\n" + traceback.format_exc())
        flash(f"Error al enviar mensaje MQTT: {e}")

    return redirect(url_for("index"))

async def publicar_mqtt(topico, valor):
    tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    tls_context.verify_mode = ssl.CERT_REQUIRED
    tls_context.check_hostname = True
    tls_context.load_verify_locations(certifi.where())

    async with aiomqtt.Client(
        hostname=os.environ["SERVIDOR"],
        port=int(os.environ["PUERTO_MQTTS"]),
        username=os.environ["MQTT_USR"],
        password=os.environ["MQTT_PASS"],
        tls_context=tls_context,
    ) as client:
        await client.publish(topico, payload=valor.encode('utf-8'), qos=1)

    logging.info(f"Publicado: {topico} = {valor}")

if __name__ == "__main__":
    app.run(debug=True)

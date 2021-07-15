from flask import Flask, render_template, request
from datetime import datetime
from ChartHelper import ChartHelper
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)

#
#app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)

@app.route("/")
def index():
    return render_template('index.html', title="Test GBE_T")

@app.route("/hello")
def hello():
    return render_template('hello.html', title="Temperature Chart")


@app.route("/temp_chart")
def temp_chart():
    ch = ChartHelper("Temperature")
    arr = ch.get_array()
    return render_template('temp_chart.html', title="Temperature Chart", data=arr)

@app.route("/humidity_chart")
def humidity_chart():
    ch = ChartHelper("Humidity")
    arr = ch.get_array()
    return render_template('humidity_chart.html', title="Humidity Chart", data=arr)

@app.route("/pressure_chart")
def pressure_chart():
    ch = ChartHelper("Pressure")
    arr = ch.get_array()
    return render_template('pressure_chart.html', title="Pressure Chart", data=arr)

@app.route("/co2_chart")
def co2_chart():
    ch = ChartHelper("CO2")
    arr = ch.get_array()
    return render_template('co2_chart.html', title="CO2 Chart", data=arr)

@app.route("/dewpoint_chart")
def dewpoint_chart():
    ch = ChartHelper()
    arr = ch.get_dewpoint_array()
    return render_template('dewpoint_chart.html', title="Dewpoint Chart", data=arr)

@app.route("/vpd_chart")
def vpd_chart():
    ch = ChartHelper()
    arr = ch.get_vpd_array()
    return render_template('vpd_chart.html', title="Vapor Pressure Deficite Chart", data=arr)



if __name__ == "__main__":
    app.run(debug=True)
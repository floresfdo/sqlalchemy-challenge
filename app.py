import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime

from flask import Flask, jsonify

engine = create_engine("sqlite:///hawaii.sqlite", echo=False)
Base = automap_base()
Base.prepare(engine, reflect=True)

Station = Base.classes.station
Measurement = Base.classes.measurement

app = Flask(__name__)
@app.route("/")
def home():
    return(
        f"Welcome to the Home Page<br/>"
        f"Available Routes: <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date/2014-04-07<br/>"
        f"/api/v1.0/start_date/end_date/2014-04-07/2015-01-19"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    recent_date = dt.date(2017,8,23)
    prec_results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > (recent_date - dt.timedelta(days=365))).all()
    session.close()

    precipitation = []
    for date, prcp in prec_results:
        prec_dict = {}
        prec_dict["date"] = date
        prec_dict["prcp"] = prcp 
        precipitation.append(prec_dict)
    
    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def station():
    session = Session(engine)
    station_list = session.query(Station.station, Station.name).all()
    session.close()

    stations = []
    for sttn, name in station_list:
        station_dict = {}
        station_dict["station"] = sttn
        station_dict["name"] = name 
        stations.append(station_dict)
    
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    recent_date = dt.date(2017,8,23)
    mostactive_station = session.query(Measurement.station,func.count(Measurement.id)).group_by(Measurement.station).order_by(func.count(Measurement.id).desc()).first()
    query_station = mostactive_station[0]
    results_temp = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == query_station).filter(Measurement.date > (recent_date - dt.timedelta(days=365))).all()
    session.close()

    temps = []
    for fecha, temp in results_temp:
        temp_dict = {}
        temp_dict["date"] = fecha
        temp_dict["temp"] = temp 
        temps.append(temp_dict)
    
    return jsonify(temps)

@app.route("/api/v1.0/start_date/<start_date>")
def start(start_date):
    session = Session(engine)
    temp_stats = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    session.close()

    stats = []
    for mint, maxt, avgt in temp_stats:
        temp_stats = {}
        temp_stats["Min"] = mint
        temp_stats["Max"] = maxt
        temp_stats["Avg"] = avgt 
        stats.append(temp_stats)
    
    return jsonify(stats)

@app.route("/api/v1.0/start_date/end_date/<start_date>/<end_date>")
def start_end(start_date=None,end_date=None):
    session = Session(engine)
    mult_date_stats = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    session.close()

    st_en_stats = []
    for tmin, tmax, tavg in mult_date_stats:
        tobs_stats = {}
        tobs_stats["Min"] = tmin
        tobs_stats["Max"] = tmax
        tobs_stats["Avg"] = tavg 
        st_en_stats.append(tobs_stats)
    
    return jsonify(st_en_stats)

if __name__=='__main__':
    app.run(debug=True)
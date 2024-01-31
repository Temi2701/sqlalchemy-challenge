import numpy as np
import pandas as pd
import datetime as dt


import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.inspection import inspect
from flask import Flask, jsonify



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with = engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################
# Home page for the api with list of routes to navigate 
@app.route("/")
def homePage():
    return(
        f"Hello and Welcome to Hawaii Climate Analysis API<br/><br/>"
        f"Available Routes shown below:<br/><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/><br/>"
        f"*** P.S to run the last two routes *start* and *start/end* use the date format yyyy-mm-dd For example /api/v1.0/2016-09-30 ***"
    )

# Precipitiation route that returns date and precipitation values
@app.route("/api/v1.0/precipitation")

def precipitation():
    session = Session(engine)

    year= dt.date(2017, 8, 23)-dt.timedelta(days=365)
    last_date = dt.date(year.year,year.month,year.day)

    scores= session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_date).order_by(Measurement.date.desc()).all()

    p_info = infotemps_info(scores)
    return jsonify(p_info) 

# stations route that shows the stations and thier information
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    sel = [Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]
    result = session.query(*sel).all()
    session.close()

    stations = []
    for station,name,lat,lon,el in result:
        station_info = {}
        station_info["Station"] = station
        station_info["Name"] = name
        station_info["Latitude"] = lat
        station_info["Longitude"] = lon
        station_info["Elevation"] = el
        stations.append(station_info)

    return jsonify(stations)
# tobs route returning information on the most active station USC00519281
@app.route("/api/v1.0/tobs")
def tobs():
     session = Session(engine)


     results = session.query( Measurement.date, Measurement.tobs).filter(Measurement.station=='USC00519281')\
     .filter(Measurement.date>='2016-08-23').all()


     tob_obs = []
     for date, tobs in results:
         tobs_infotemps_info = {}
         tobs_infotemps_info["Date"] = date
         tobs_infotemps_info["Tobs"] = tobs
         tob_obs.append(tobs_infotemps_info)

     return jsonify(tob_obs)
# start route to find min,max,avg temperature of a given time
@app.route("/api/v1.0/<start>")

def start_temp(start):
    session = Session(engine)
    start_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).all()
    session.close()

    temps = []
    for min_temp, avg_temp, max_temp in start_results:
        temps_info = {}
        temps_info['Min Temp'] = min_temp
        temps_info['Avg Temp'] = avg_temp
        temps_info['Max Temp'] = max_temp
        temps.append(temps_info)

    return jsonify(temps)

#start/end route to find min,max,avg temperature of a given time and end time

@app.route("/api/v1.0/<start>/<end>")
def start_temp_end_temp(start, end):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    temps = []
    for min_temp, avg_temp, max_temp in results:
        temps_info = {}
        temps_info['Min Temp'] = min_temp
        temps_info['Avg Temp'] = avg_temp
        temps_info['Max Temp'] = max_temp
        temps.append(temps_info)

    return jsonify(temps)


if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import datetime as dt
import numpy as np
import pandas as pd
from datetime import timedelta

engine  = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect = True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)
__abstract__ = True


app = Flask(__name__)
@app.route("/")
def Home():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )

@app.route("/api/v1.0/precipitation")
def percipitation():

    session = Session(engine)
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    last_date = dt.datetime.strptime(last_date, "%Y-%m-%d")
    first_date = last_date - timedelta(days = 365)
    prcp_results = (session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= first_date).order_by(Measurement.date).all())
    return jsonify({'prcp_results': [dict(row) for row in prcp_results]})

@app.route("/api/v1.0/stations")
def stations():
  session  = Session(engine)
  stations_results = session.query(Station.station, Station.name).all()
  return jsonify({'stations_results': [dict(row) for row in stations_results]})

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    lateststr = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    latestdate = dt.datetime.strptime(lateststr, '%Y-%m-%d')
    querydate = dt.date(latestdate.year -1, latestdate.month, latestdate.day)
    sel = [Measurement.date,Measurement.tobs]
    queryresult = session.query(*sel).filter(Measurement.date >= querydate).all()
    session.close()

    tobsall = []
    for date, tobs in queryresult:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobsall.append(tobs_dict)

    return jsonify({'tobsall': [dict(row) for row in tobsall]})
    
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    session = Session(engine)

    """Return TMIN, TAVG, TMAX."""

    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        result = session.query(*sel).\
            filter(Measurement.date >= start).all()
        # Unravel result into a 1D array and convert to a list
        temps = list(np.ravel(result))
        return jsonify(temps)

    # calculate TMIN, TAVG, TMAX with start and stop
    result = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
  
    return jsonify({'result': [dict(row) for row in result]})


if __name__ == '__main__':
    app.run(debug=True)


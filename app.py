# Import

import numpy as np
from datetime import datetime as dt
from numpy.core.fromnumeric import ravel
from numpy.testing._private.utils import measure

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, query, session
from sqlalchemy import create_engine, func

from flask import Flask, json, jsonify

# Database Setup

engine = create_engine("sqlite:///resources/hawaii.sqlite")

# reflect existing database into

Base = automap_base()

# reflect the tables

Base.prepare(engine, reflect=True)
print(Base.classes.keys())

# Save reference to the table for measurement and station

measurement = Base.classes.measurement
station = Base.classes.station

# Flask

app = Flask(__name__)

# Create Home and List Available Routes

@app.route("/")
def welcome():
    """List of all available API routes"""
    return (
        f"Welcome to the Hawaii Climate Analysis App! Check out the below information!<br/>"
        f"Here are the Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

# precipitation route

@app.route("/api/v1.0/precipitation")
def precipitation():

    "Return the precipitation data for the last year"

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate the timeline

    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # Query the date and precipitation in timeline

    precipitation = session.query(measurement.date, measurement.prcp).filter(measurement.date >= prev_year).all()

    # Create dictionary with key-value pair of date and prcp

    precip = {date : prcp for date, prcp in precipitation}

    return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():

    "Return list of the stations"

    results = session.query(station.station).all()

    # Unravel and convert to a list

    stations = list(np.ravel(results))
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def temp():

    "Return the temperature observations for the last year"

    # Calculate the timeline

    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the USC00519281 most active station for all tobs from timeline

    results = session.query(measurement.tobs).filter(measurement.station == 'USC00519281').filter(measurement.date >= prev_year).all()

    # Unravel and convert to a list

    temps = list(np.ravel(results))

    return jsonify(temps)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start=None, end=None):

    "Return Minimum, Average, and Maximum Temperature (TMIN,TAVG,TMAX)"

    # select

    sel = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]

    if not end:
        # calculate TMIN, TAVG, TMAX for dates after start

        results = session.query(*sel).filter(measurement.date >= start).all()

        # Unravel and convert to a list

        temps = list(np.ravel(results))

        return jsonify(temps)

    # calculate TMIN, TAVG, TMAX with begin and end

    results = session.query(*sel).filter(measurement.date >= start).filter(measurement.date <= end).all()

    # Unravel and convert to a list

    temps = list(np.ravel(results))

    return jsonify(temps)

if __name__ == '__main__':
    app.run()
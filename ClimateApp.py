# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 14:59:06 2019

@author: Christopher Jung
"""
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt


from flask import Flask, jsonify
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite",connect_args={'check_same_thread': False}, echo=True)
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
Base.classes.keys()
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"<h1>Welcome to the Climate Retrieval API Page (C.R.A.P)!</h1>"
        f"<h2>Climate Data from 01/01/2011 to 08/23/2017</h2>"
        f"<h3>Available Routes:</h3>"
        f"<p><a href=""http://127.0.0.1:5000/api/v1.0/precipitation"">/api/v1.0/precipitation</a> This API endpoint returns precipitaton amounts from the Previous Year.(08/23/2016 to 08/23/2017)</p>"
        f"<p><a href=""http://localhost:5000/api/v1.0/stations"">/api/v1.0/stations</a> This API endpoint returns all stations in the dataset</p>"
        f"<p><a href=""http://localhost:5000/api/v1.0/tobs"">/api/v1.0/tobs</a> This API endpoint returns all temperature observations from the Previous Year.(08/23/2016 to 08/23/2017)</p>"
        f"<p>This API endpoint returns the Minimum, Average, and Maximum Temperature of a given start date range i.e.(2011-01-01). Click link and change default to desired start date. </p>"
        f"<p><a href=""http://localhost:5000/api/v1.0/2011-01-01"">/api/v1.0/2011-01-01</a></p>"
        f"<p>This API endpoint returns the Minimum, Average, and Maximum Temperature of a given start and end date range i.e.(2011-01-01/2017-08-23). Click link and change defaults to desired start/end dates. </p>"
        f"<p><a href=""http://localhost:5000/api/v1.0/2011-01-01/2017-08-23"">/api/v1.0/2011-01-01/2017-08-23</a></p>"
           
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results to a Dictionary using date as the key and prcp as the value."""
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year=dt.datetime.strptime(last_date[0],'%Y-%m-%d')- dt.timedelta(days=366)
    scores=session.query(Measurement.date,Measurement.prcp).filter(Measurement.date>=last_year).all()
    #Add to dictinary and return JSON
    prcp_year=[]

    for date, prcp in scores:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_year.append(prcp_dict)

    return jsonify(prcp_year)


@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    stations=session.query(Station.station).all()

    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():
    """Query for the dates and temperature observations from a year from the last data point."""
    """Return a JSON list of Temperature Observations (tobs) for the previous year"""
    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    #get last date
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()  
    #Calculate the date 1 year ago from the last data point in the database
    last_year=dt.datetime.strptime(last_date[0],'%Y-%m-%d')- dt.timedelta(days=366)    
    # Perform a query to retrieve the DATE and precipitation scores,
    scores=session.query(Measurement.date,Measurement.tobs).filter(Measurement.date>=last_year).all()
    
    return jsonify(scores)


@app.route("/api/v1.0/<start>")
def start_date(start):  
# This function called will accept start date in the format '%Y-%m-%d' 
# and return the minimum, average, and maximum temperatures for that range of dates
    """TMIN, TAVG, and TMAX for a list of datess.
    
    Args:
        start(string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    results= session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    return jsonify(results)
    
    
@app.route("/api/v1.0/<start>/<end>")
def start_end_range(start,end):  
# This function will accept start date and end date in the format '%Y-%m-%d' 
# and return the minimum, average, and maximum temperatures for that range of dates
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start (string): A date string in the format %Y-%m-%d
        end(string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    se_range= session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()


    return jsonify(se_range)
    
    
    
if __name__ == '__main__':
    app.run(debug=True)
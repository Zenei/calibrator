from connection import mydb
import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import numpy as np
from sqlalchemy import create_engine

engine = create_engine('mysql://elvis:kitone@localhost/wdrDb')


def calibrateStation(station_name):

  temperature_query = "select datetime, temp_wimea, temp_unma, station from uploads where station = '%s'" %station_name
  relative_humidity_query = "select datetime, rh_wimea, rh_unma, station from uploads where station = '%s'" %station_name
  
  temp = pd.read_sql(temperature_query,con=engine)
  rel_hum = pd.read_sql(relative_humidity_query,con=engine)
  
  
  ## Temperature
  X   = temp['temp_wimea'].values
  Y   = temp['temp_unma'].values
  D   = temp['datetime'].values
  st  = temp['station'].values
  
  ## Relative Humidity
  X1   = rel_hum['rh_wimea'].values
  Y1   = rel_hum['rh_unma'].values
  D1   = rel_hum['datetime'].values
  st1  = rel_hum['station'].values 
  
  
  ## Temperature
  mean_x = np.mean(X)
  mean_y = np.mean(Y)
  
  ## Relative Humidity
  mean_x1 = np.mean(X1)
  mean_y1 = np.mean(Y1)
  

  # Total number of values
  a  = len(X) ## Temperature
  a1 = len(X1) ## Relative Humidity
  

  # Using formula to calculate m and c coefficients
  ## Temperature
  numer = 0
  denom = 0
  for i in range(a):
      numer += (X[i] - mean_x) * (Y[i] - mean_y)
      denom += (X[i] - mean_x) ** 2
  m = numer / denom
  c = mean_y - (m * mean_x)
  
  ## Relative Humidity
  numer1 = 0
  denom1 = 0
  for p in range(a1):
      numer1 += (X1[p] - mean_x1) * (Y1[p] - mean_y1)
      denom1 += (X1[p] - mean_x1) ** 2
  m1 = numer1 / denom1
  c1 = mean_y1 - (m1 * mean_x1)  

  
  # Appending Calibrated values
  ## Temperature
  dependent = []
  for i in range(a):
      dep = m*(X[i]) + c
      dependent.append(dep)
      
  ## Relative Humidity
  dependent1 = []
  for p in range(a1):
      dep1 = m1*(X1[p]) + c1
      dependent1.append(dep1)


  # Confidence level
  ## Temperature
  ss_t = 0
  ss_r = 0
  for i in range(a):
      y_pred = c + m * X[i]
      ss_t += (Y[i] - mean_y) ** 2
      ss_r += (Y[i] - y_pred) ** 2
  r2 = 1 - (ss_r/ss_t)
  percent_r2 = r2 * 100
  
  
  ## Relative Humidity
  ss_t1 = 0
  ss_r1 = 0
  for p in range(a1):
      y_pred1 = c1 + m1 * X1[p]
      ss_t1 += (Y1[p] - mean_y1) ** 2
      ss_r1 += (Y1[p] - y_pred1) ** 2
  r2a = 1 - (ss_r1/ss_t1)
  percent_r2a = r2a * 100
  
  
  # Combining Series into a Dataframe
  ## Temperature
  datetime   = pd.DataFrame(D)
  wimea_temp = pd.DataFrame(X)
  unma_temp  = pd.DataFrame(Y)
  calibrated = pd.DataFrame(dependent)
  stations   = pd.DataFrame(st)
  merge1  = pd.concat([datetime, wimea_temp], axis = 1)
  merge2  = pd.concat([merge1, calibrated], axis = 1)
  merge3  = pd.concat([merge2, unma_temp], axis = 1)
  newtemp = pd.concat([merge3, stations], axis = 1)
  newtemp.columns = ['datetime','wimea_original_temp','wimea_calibrated_temp','unma_original_temp','station']
  
  
  ## Relative Humidiy
  datetime1   = pd.DataFrame(D1)
  wimea_rh    = pd.DataFrame(X1)
  unma_rh     = pd.DataFrame(Y1)
  calibrated1 = pd.DataFrame(dependent1)
  stations1   = pd.DataFrame(st1)
  merge1  = pd.concat([datetime, wimea_rh], axis = 1)
  merge2  = pd.concat([merge1, calibrated1], axis = 1)
  merge3  = pd.concat([merge2, unma_rh], axis = 1)
  newrh = pd.concat([merge3, stations1], axis = 1)
  newrh.columns = ['datetime','wimea_original_humidity','wimea_calibrated_humidity','unma_original_humidity','station']
  
  s_temp = "{}_temperature".format(station_name)
  s_rh   = "{}_humidity".format(station_name)
  
  
  # Inserting to database (DB)
  ## Temperature
  cursor = mydb.cursor()
  sql = "INSERT INTO calibration_values (confidence_level, coefficient_m, coefficient_c, station_parameter) VALUES (%s, %s, %s, %s)"
  val = (str(percent_r2), str(m), str(c), s_temp)
  cursor.execute(sql,val)
  mydb.commit()
  
  ## Relative Humidity
  cursor = mydb.cursor()
  sql1 = "INSERT INTO calibration_values (confidence_level, coefficient_m, coefficient_c, station_parameter) VALUES (%s, %s, %s, %s)"
  val1 = (str(percent_r2a), str(m1), str(c1), s_rh)
  cursor.execute(sql1,val1)
  mydb.commit()
  
  # DB insertion using to_sql()
  #newtemp.to_sql(name = "temperaturecalibration_wimea_unma", con=engine, if_exists='replace')
  #newrh.to_sql(name = "humiditycalibration_wimea_unma", con=engine, if_exists='replace')
  
  # Plots
  #lines = plt.plot(D, X, D, Y)
  #l1 = plt.plot(D, X)
  #l2 = plt.plot(D, Y) 
  #plt.setp(l1, 'color','r', 'linewidth',1.0)
  #plt.setp(l2, 'color','b', 'linewidth',1.0)

  #plt.setp(lines, 'color', 'r', 'linewidth', 1.0)
  #plt.show()


  #l3 = plt.plot(D, X)
  #l4 = plt.plot(D, dependent)
  #plt.setp(l3, 'color','r', 'linewidth',1.0)
  #plt.setp(l4, 'color','b', 'linewidth',1.0)

  #lines = plt.plot(D, X, D, dependent)
  #plt.setp(lines, 'color', 'r', 'linewidth', 1.0)
  #plt.show()
 
  
# Testing against sample weather stations
calibrateStation(Entebbe)
calibrateStation(Kamuli)
mydb.close()

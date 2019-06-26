# import pymysql.cursors

# connection = pymysql.connect(host='localhost',
#                               user='oboth',
#                               password='oboth',
#                               db='wdrDb',
#                               charset='utf8mb4',
#                               cursorclass=pymysql.cursors.DictCursor)



import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="elvis",
  passwd="kitone",
  database="wdrDb"
)
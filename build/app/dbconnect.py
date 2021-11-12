import mysql.connector
from common import *

def mysql_delete_channel_from_db(channelname):
	mysql_query("DELETE FROM cbb_channels WHERE channelname = '" + channelname + "';")

def mysql_query(statement, values = None):
	try:
		mycursor = mysqlconnection.cursor()

		if values is not None:
			mycursor.execute(statement, values)
		else:
			mycursor.execute(statement)

		mysqlconnection.commit()
	except Exception as e:
		print_mysql_error(statement, e)

def mysql_query_select(statement):
	try:
		mycursor = mysqlconnection.cursor()
		mycursor.execute(statement)
		return mycursor.fetchall()
	except Exception as e:
		print_mysql_error(statement, e)

def mysql_query_select_fetchone(statement):
	try:
		mycursor = mysqlconnection.cursor()
		mycursor.execute(statement)
		return mycursor.fetchone()
	except Exception as e:
		print_mysql_error(statement, e)

def print_mysql_error(statement, e):
	print_msg_time("Error at mysql statement:")
	print_msg_time(statement)
	print_msg_time("Error:")
	print_msg_time(str(e))
	print_msg_time("Exiting...")
	exit(1)

# connect to mysql
try:
	mysqlconnection = mysql.connector.connect(
		host = "db",
		user = os.getenv('MYSQL_USER'),
		password = os.getenv('MYSQL_PW'),
		database = "clickbotbot"
	)
except Exception as e:
	print_msg_time(str(e))
	print_msg_time("Cannot connect to mysql. Exiting...")
	exit(1)
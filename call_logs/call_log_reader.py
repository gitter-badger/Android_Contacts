'''
##########################################
Pseudo code
1) Connect to sqllit3 database.
2) Check if record present in call log info table.
3) If present then get the date of latest call log,
4) Query the Call log.
   if latest date present from step 3 then get all call log whose date greater than latest call log date.
   else get all call logs records.
   Each call_log_info_dict contain following info
   {u'name': u'Gaju', u'numbertype': u'1', u'number': u'+919423231248',
    u'date': u'1388714531568', u'duration': u'64', u'new': u'0', u'_id': u'4551',
    u'type': u'2'}
5) Create empty dict say call_log_per_record_dict = {}.
6) Iterate through each dict and in each iteration perform following steps
   a. Convert date into "YYYY-mm-dd HH:MM" format.
   b. Add record to call_log_per_record_dict where date is key and call_log_info_dict is value.
      Example: {"2014-02-14 02:00", <call_log_info_dict>}
7) Create call_log_key_list of call_log_per_record_dict.
8) If not present go to step 10.
9) If present then get the latest call log date from call_log_info table.
10) Get the list of keys from call_log_key_list where key value is greater than call log date.
11) Iterate through each key from list and add call log to call_log_info table.
##########################################
'''
import sqlite3
import datetime
import re
import android
from db_connection import DB_Connection

def convert_unix_epoch_to_datetime(date_int):
	'''
	1) Convert the date_int which is epoch time in time object in following format.
	'''
	#Since date_int is in millisecond convert it to seconds
	seconds_date_int = date_int/1000
	datetime_obj = datetime.datetime.fromtimestamp(seconds_date_int)
	return datetime_obj

def convert_datetime_to_epoch(datetime_str):
	'''
	@args: datetime string
	@return: epoch timestamp
	1) Convert datetime_str to datetime object.
	2) Convert datetime object to epoch
	'''
	datetime_obj = datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
	epoch_time = int(datetime_obj.strftime("%s"))
	return epoch_time

class Call_Log_Info_Data(object):
	def __init__(self):
		self.name=None
		self.number = None
		self.numbertype = None
		self.duration = None
		self.log_date = None
		self.is_new = None
		self.call_id = None
		self.call_log_type = None
		return

class Call_Log_Reader(object):

	def __init__(self, droid, db_connection):
		self.droid = droid
		self.db_connection = db_connection
		self.connection = self.db_connection.connection
		self.cursor = self.db_connection.cursor

	def query_android_call_log(self, selection, args):
		query = "content://call_log/calls"
		call_log_result_list = self.droid.queryContent(query, None, selection, args).result
		return call_log_result_list

	def get_latest_call_log_date(self):
		#Check if record present in call log info
		latest_call_log_date = None
                query = "select log_date from call_log_info order by log_date desc limit 1"
                self.db_connection.execute_sql(query)
                result = self.cursor.fetchall()
		if result:
			latest_call_log_date = result[0][0]
		return latest_call_log_date

	def start(self):

		selection = None
		args = None
		latest_call_log_date = self.get_latest_call_log_date()
		if latest_call_log_date:
			selection = "date > ?"
			latest_call_log_date = convert_datetime_to_epoch(latest_call_log_date)
			#Convert seconds to milisecond
			args = [latest_call_log_date * 1000]

		android_call_log_dict_list = self.query_android_call_log(selection, args)
		#Iterate through android call log dict and create call_log_per_record_dict

		for call_log_dict in android_call_log_dict_list:
			call_log_info_obj = self.get_call_log_info_obj(call_log_dict)
			self.populate_call_log_info_data(call_log_info_obj)
		return

	def get_call_log_info_obj(self, call_log_dict):
		'''
		1) Read each key value from call log dict and associate it with call_log_info_obj
		'''
		call_log_info_obj = Call_Log_Info_Data()
		call_log_info_obj.call_id = int(call_log_dict["_id"])
		date_int = int(call_log_dict["date"])
		call_log_info_obj.log_date = convert_unix_epoch_to_datetime(date_int)
		call_log_info_obj.duration = int(call_log_dict["duration"])
		try:
			call_log_info_obj.name = call_log_dict["name"]
		except KeyError:
			#If name is not available then ignore it
			pass
		call_log_info_obj.is_new = int(call_log_dict["new"])
		call_log_info_obj.number = call_log_dict["number"]
		try:
			call_log_info_obj.numbertype = int(call_log_dict["numbertype"])
		except KeyError:
			'''
			numbertype keyword present only if number is stored in contacts.
			if it's unknown number then key is not present.
			'''
			pass
		call_log_info_obj.call_log_type = int(call_log_dict["type"])
		return call_log_info_obj

	def populate_call_log_info_data(self, call_log_info_object):
		'''
			Insert data to call_log_info table.
		'''
		query = "insert into call_log_info(name, numbertype, number, log_date, duration, is_new, call_id, type) values \
						  (?, ?, ?, ?, ?, ?, ?, ?)"
		args = (call_log_info_object.name,\
			call_log_info_object.numbertype,\
			call_log_info_object.number, \
			call_log_info_object.log_date, \
			call_log_info_object.duration, \
			call_log_info_object.is_new, \
			call_log_info_object.call_id, \
			call_log_info_object.call_log_type
		       )
		self.db_connection.execute_sql(query, args)
		return


if __name__ == "__main__":
	droid = android.Android()
	db_connection = DB_Connection("call_log_database.db")
	log_reader = Call_Log_Reader(droid, db_connection)
	log_reader.start()



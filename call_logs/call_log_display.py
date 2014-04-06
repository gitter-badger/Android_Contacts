"""
Pseudo code
1) Call call_log_reader which will add call logs to call_log_info table.
2) Read Call logs from call_log_info table and display it on javascript.
"""
import android
import json
from db_connection import DB_Connection
from call_log_reader import Call_Log_Reader

DATABASE_PATH = "/sdcard/sl4a/scripts/call_logs/call_log_database.db"
WEB_VIEW_PATH = "file:///sdcard/sl4a/scripts/call_logs/html/call_log_display.html" 

class Call_Log_Display(object):
	
	def __init__(self):
		self.droid = android.Android()
		self.db_connection = DB_Connection("call_log_database.db")#(DATABASE_PATH)
		self.set_display_property()
	
	def get_call_logs_to_display(self):
		'''
		1) Run query to get call logs by name, number and total calls for each number.
		2) Convert tuple to list and then to json using json.dumps
		3) return json call_log_tuple_list.
		'''
		call_log_dict = {}
		query = "select name, number, count(*) from call_log_info group by name,number;"
		self.db_connection.execute_sql(query)
		result_tuple_tuple = self.db_connection.cursor.fetchall()
		call_log_tuple_list = list(result_tuple_tuple)
		call_log_tuple_list_json = json.dumps(call_log_tuple_list)#.replace("'", r"\'")
		#call_log_tuple_list_json = "'%s'"%call_log_tuple_list_json
		return call_log_tuple_list_json
	
	def set_display_property(self):
		self.droid.addOptionsMenuItem('About','menu-about',None,"ic_menu_info_details")
		self.droid.addOptionsMenuItem('Quit','menu-quit',None,"ic_lock_power_off")
	
	def read_call_logs(self):
		'''
		1) create instance of call_log_reader. and call it's start method
		   which will add call_logs to call_log_info
		'''
		call_log_reader = Call_Log_Reader(self.droid, self.db_connection)
		call_log_reader.start()
		return
	
	def event_loop(self):
		'''
		Yet to decide which event need to send to javascript code.
		'''
		#Wait until python get acknowledgment for receiving call log list from javascript.
             	pass

	def read_call_logs_from_phone(self):
		self.read_call_logs()
		call_log_tuple_list_json = self.get_call_logs_to_display()
		print call_log_tuple_list_json
		self.droid.eventPost("call_logs_read", call_log_tuple_list_json)
		self.droid.makeToast("Event Posted")
            	
	def start(self):
		'''
		1) Call read_call_logs which return call log dict.
		2) Post event as "call_logs" and pass call log dict to it.
		3) That event then read by javascript code.
		4) Call the event loop.
		'''
		self.droid.eventClearBuffer()
		self.droid.webViewShow(WEB_VIEW_PATH)
		self.droid.makeToast("Called html")
		result = self.droid.eventWaitFor("calllog").result#For("calllog")
		self.droid.makeToast("event name %s"%result["name"])
		self.read_call_logs_from_phone()
		while (True):
			event = self.droid.eventWait().result
			if event["name"] == "menu-quit":
				self.droid.eventPost("close", "")
				break

if __name__ == "__main__":
	call_log = Call_Log_Display()
	call_log.start()

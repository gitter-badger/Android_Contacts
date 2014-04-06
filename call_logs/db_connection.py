
'''
Class related to DB connection
'''
import sqlite3
class DB_Connection(object):
	def __init__(self, db_file):
		self.connection = sqlite3.connect(db_file)
		self.cursor = self.connection.cursor()

	def execute_sql(self, query, args=()):
		try:
			self.cursor.execute(query, args)
			self.connection.commit()
		except Exception as e:
			#Roll back
			print e.message
			self.connection.rollback()
		return

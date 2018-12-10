# -*- coding: utf-8 -*-
# 此程序用来抓取 的数据
import pymysql
import sys
reload(sys)
sys.setdefaultencoding('gb18030')

class database(object):
	def __init__(self):
		self.db = pymysql.connect(host='192.168.4.200', user='root', password='wgs123', db='wenchan', charset='utf8')
		self.cursor = self.db.cursor()
	
	def create_db(self):
		db = pymysql.connect(host='192.168.4.200', user='root', password='wgs123', port=3306)
		cursor = db.cursor()
		cursor.execute('SELECT VERSION()')
		data = cursor.fetchone()
		print 'Database version:', data
		cursor.execute("CREATE DATABASE JC DEFAULT CHARACTER SET utf8")
		db.commit()
		db.close()
	
	def add(self, table_name, data):
		keys = ', '.join(data.keys())
		values = ', '.join(['%s'] * len(data))
		sql = 'INSERT INTO {table}({keys}) VALUES ({values})'.format(table=table_name, keys=keys, values=values)
		try:
			self.cursor.execute(sql, tuple(data.values()))
			self.db.commit()
			return True
		except Exception as e:
			print e
			self.db.rollback()
			return False
	
	def delete(self, table_name):
		condition = 'JC_ID >= 1'
		sql = 'DELETE FROM  {table} WHERE {condition}'.format(table=table_name, condition=condition)
		try:
			self.cursor.execute(sql)
			self.db.commit()
		except:
			self.db.rollback()
	
	def up_data(self, table_name, data):
		keys = ', '.join(data.keys())
		values = ', '.join(['%s'] * len(data))
		
		sql = 'INSERT INTO {table}({keys}) VALUES ({values}) ON DUPLICATE KEY UPDATE'.format(table=table_name,
		                                                                                     keys=keys,
		                                                                                     values=values)
		update = ','.join([" {key} = %s".format(key=key) for key in data])
		sql += update
		try:
			if self.cursor.execute(sql, tuple(data.values()) * 2):
				self.db.commit()
				return True
			else:
				return False
		except:
			self.db.rollback()

if __name__ == "__main__":
	DA = database()

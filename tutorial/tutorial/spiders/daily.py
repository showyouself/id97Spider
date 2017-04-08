# encoding: utf-8
import scrapy
import json
import time
import MySQLdb
import re

class Daily(scrapy.Spider):
	name = "daily"
	allowed_domains = ["181bt.com"]
	conn = MySQLdb.connect(host = 'localhost',port = 3306, user = 'root', passwd = 'toot', db = 'deal')
	db = conn.cursor()
	
	
	def start_requests(self):
		result = []
		for val in self.allowed_domains:
			result.append(self.go(val))
		return result	

	def go(self, handler):
		if handler == '181bt.com':
			url = "http://www.181bt.com/" 
			result = scrapy.Request(url,callback=self.parse_id97)
		return result

	def parse_id97(self,response):
		ids = []
		tmp = len(response.css('.carousel-inner a::attr(href)'))
		pat = re.compile('\d+');
		if tmp > 0:
			for val in response.css('.carousel-inner a::attr(href)').extract():
				ids.append(re.findall(pat,val)[1])			
				
		tmp = len(response.css('.movie-item-in a::attr(href)'))
		if tmp > 0:
			for val in response.css('.movie-item-in>a::attr(href)').extract():
				ids.append(re.findall(pat,val)[1])

		tmp = len(ids)
		if tmp > 0:
			l = open('/home/wwwroot/py/tutorial/tutorial/spiders/result/daily/id97daily', 'w')
			line = json.dumps(ids) + "\n"
			l.write(line)	
			l.close()
		
		
	def mysql(self,sql):
		self.db.execute(sql)
		result = self.db.fetchone()		
		self.db.close()
		return result

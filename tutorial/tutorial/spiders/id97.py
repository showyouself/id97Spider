# encoding: utf-8
import scrapy
import json
import time
import datetime
from tutorial.items import DmozItem

class DmozSpider(scrapy.Spider):
	name = "id97"
	allowed_domains = ["181bt.com"]
	sleep_time = 0.5
	handle_httpstatus_list = [403,404,500,503]	
	now = datetime.datetime.now().strftime("%Y-%m-%d")
	l = open('/home/wwwroot/py/tutorial/tutorial/spiders/result/tmp/' + now + 'lost.log', 'w')
	r = open('/home/wwwroot/py/tutorial/tutorial/spiders/result/tmp/' + now + 'result.json','w')
	f = open('/home/wwwroot/py/tutorial/tutorial/spiders/result/daily/id97daily','r')
	source_data = list(set(json.loads(f.readline())))
	max_count = len(source_data) - 1
	count = 0
	data = {}	
	def go(self):
		print "========================"+str(self.max_count)
		url = "http://www.181bt.com/movie/" + self.source_data[self.count] +".html" 
		result = scrapy.Request(url,callback=self.parse)
		return [result]

	def rego(self):
		print ">>>>>>>>>>写出文件"
		line = json.dumps(dict(self.data)) + "\n"
		self.r.write(line)
		self.data = {}

		self.count = self.count + 1
		if self.count >= self.max_count:
			self.l.close()
			self.r.close()
			print "脚本执行结束:",str(self.count)
			return None
		time.sleep(self.sleep_time)
		return self.go()

	def start_requests(self):
		return self.go()	
	
	def parse(self, response):
		print "==执行次数",self.count 
		if response.status in self.handle_httpstatus_list:
			tmp = {'id': str(self.source_data[self.count]),'status': str(response.status)}
			line = json.dumps(dict(tmp)) + "\n"
			self.l.write(line)
			return self.go()
		item = {'id':self.source_data[self.count],'name':'','year':'','logo_url':'','director':'','screenwriter':'','tostar':'','type':'','country':'','language':'','releasetime':'','long':'','altname':'','score':'','tags':[],'introduce':[],'screenshot':[],'download':{}}
		
		print "==== 解析基本信息"	
		tmp = len(response.css('.padding-right-5 h1 ::text'))
		if tmp > 0 :
			item['name'] = response.css('.padding-right-5 h1 ::text')[0].extract()
		if tmp > 1 :
			item['year'] = response.css('.padding-right-5 h1 ::text')[1].extract()
		tmp = len(response.css('.img-thumbnail::attr(src) '))
		if tmp >0:
			item['logo_url'] = response.css('.img-thumbnail::attr(src) ')[0].extract()
		
		print "========== 解析详细信息"
		tr = response.css('.table-striped tr')
		item = self.decode_item(item, tr)

		tmp = len(response.css('.movie-introduce > p'))
		if tmp > 0:
			print "============== 解析电影简介"
			item['introduce'] = self.p(response.css('.movie-introduce > p'))
		tmp = len(response.css('.tags a'))
		if tmp > 0:
			print "===================== 解析tags"
			item['tags'] = self.p(response.css('.tags a::text'))
		
		tmp = len(response.css('.movie-screenshot img::attr(src)'))
		if tmp > 0:
			print "========================== 解析电影截图"
			item['screenshot'] = self.nomarl_p(response.css('.movie-screenshot img::attr(src)'))		

		self.data = item
		
	
		return self.go_ed2k() 
		
	def go_ed2k(self):
		url = "http://www.181bt.com/videos/resList/" + str(self.source_data[self.count])
		print "================================== 资源请求：", url
		result = scrapy.Request(url,callback=self.ed2k_parse)
		return [result]
	
	def ed2k_parse(self, response):
		print "====================================== 解析电影资源"
		ret = {'d_xl':[],'d_gq':[]}
		if response.status in self.handle_httpstatus_list:
			self.data['download'] = ret
			return self.go()
	 	tmp = len(response.css('.tab-pane'))
		ser = '.text-break a[mid="' +str(self.source_data[self.count]) + '"]'
		if tmp > 0:
			for v in response.css('.tab-pane')[0].css(ser):
				tmpl = {}
				tmpl['title'] = v.css('::attr(title)').extract()[0]	
				tmpl['href'] = v.css('::attr(href)').extract()[0] 
				ret['d_xl'].append(tmpl)
		if tmp > 1:
			for v in response.css('.tab-pane')[1].css(ser):
				tmpl = {} 
				tmpl['title'] = v.css('::attr(title)').extract()[0]
				tmpl['href'] = v.css('::attr(href)').extract()[0] 
				ret['d_gq'].append(tmpl)
		print "========================================== 解析电影资源成功"
		self.data['download'] = ret
		return self.rego()

	def decode_item(self, item, tr):
		if isinstance(tr, list) and len(tr) > 0:
			for v in tr:
				lb_info = v.css('.span2 .info-label::text')[0].extract()
				if (lb_info.encode('utf-8') == '导演'):
					item['director'] = self.p(v.css('td + td a').css('::text')) 
				if (lb_info.encode('utf-8') == '编剧'):		
					item['screenwriter'] = self.p(v.css('td + td a').css('::text'))
				if (lb_info.encode('utf-8') == '主演'):
					item['tostar'] = self.p(v.css('td + td a[target=_blank]').css('::text'))
				if (lb_info.encode('utf-8') == '类型'):
					item['type'] = self.p(v.css('td + td a').css('::text'))
				if (lb_info.encode('utf-8') == '制片国家'):
					item['country'] = self.p(v.css('td + td a').css('::text'))
				if (lb_info.encode('utf-8') == '评分'):
					item['score'] = self.p(v.css('td + td a').css('::text'))
				if (lb_info.encode('utf-8') == '语言'):
					item['language'] =  v.css('td + td::text')[0].extract()
				if (lb_info.encode('utf-8') == '上映时间'):
					item['releasetime'] =  v.css('td + td::text')[0].extract()
				if (lb_info.encode('utf-8') == '片长'):
					item['long'] =  v.css('td + td::text')[0].extract()
				if (lb_info.encode('utf-8') == '又名'):
					item['altname'] =  v.css('td + td::text')[0].extract()
		return item
	
	def p(self,s):
		ret = []
		for v in s:
			ret.append(v.extract())
		return ret

	def nomarl_p(self,s):
		ret = []
		s_long = len(s)
		i = 1
		for v in s:
			if i > s_long:
				break
			ret.append(v.extract())
			i = i +1
		return ret	

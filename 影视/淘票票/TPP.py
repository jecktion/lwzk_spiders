# -*- coding: utf-8 -*-
# 此程序用来抓取 的数据
import PyV8
import requests
import time
import random
import re
import csv
import json
from fake_useragent import UserAgent, FakeUserAgentError
from save_data import database


class Spider(object):
	def __init__(self):
		try:
			self.ua = UserAgent(use_cache_server=False).random
		except FakeUserAgentError:
			pass
		with open('b.txt') as f:
			self.sign_js = f.read().strip()
		self.db = database()

	def get_headers(self):
		user_agents = ['Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20130406 Firefox/23.0',
		               'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0',
		               'IBM WebExplorer /v0.94', 'Galaxy/1.0 [en] (Mac OS X 10.5.6; U; en)',
		               'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
		               'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14',
		               'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; TheWorld)',
		               'Opera/9.52 (Windows NT 5.0; U; en)',
		               'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.2pre) Gecko/2008071405 GranParadiso/3.0.2pre',
		               'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.458.0 Safari/534.3',
		               'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/4.0.211.4 Safari/532.0',
		               'Opera/9.80 (Windows NT 5.1; U; ru) Presto/2.7.39 Version/11.00']
		user_agent = random.choice(user_agents)
		headers = {'Host': 'www.shilladfs.com', 'Connection': 'keep-alive',
		           'User-Agent': user_agent,
		           'Referer': 'http://www.shilladfs.com/estore/kr/zh/Skin-Care/Basic-Skin-Care/Pack-Mask-Pack/p/3325351',
		           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		           'Accept-Encoding': 'gzip, deflate, br',
		           'Accept-Language': 'zh-CN,zh;q=0.8'
		           }
		return headers
	
	def p_time(self, stmp):  # 将时间戳转化为时间
		stmp = float(str(stmp)[:10])
		timeArray = time.localtime(stmp)
		otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
		return otherStyleTime
	
	def replace(self, x):
		# 去除img标签,7位长空格
		removeImg = re.compile('<img.*?>| {7}|')
		# 删除超链接标签
		removeAddr = re.compile('<a.*?>|</a>')
		# 把换行的标签换为\n
		replaceLine = re.compile('<tr>|<div>|</div>|</p>')
		# 将表格制表<td>替换为\t
		replaceTD = re.compile('<td>')
		# 把段落开头换为\n加空两格
		replacePara = re.compile('<p.*?>')
		# 将换行符或双换行符替换为\n
		replaceBR = re.compile('<br><br>|<br>')
		# 将其余标签剔除
		removeExtraTag = re.compile('<.*?>', re.S)
		# 将&#x27;替换成'
		replacex27 = re.compile('&#x27;')
		# 将&gt;替换成>
		replacegt = re.compile('&gt;|&gt')
		# 将&lt;替换成<
		replacelt = re.compile('&lt;|&lt')
		# 将&nbsp换成''
		replacenbsp = re.compile('&nbsp;')
		# 将&#177;换成±
		replace177 = re.compile('&#177;')
		replace1 = re.compile(' {2,}')
		x = re.sub(removeImg, "", x)
		x = re.sub(removeAddr, "", x)
		x = re.sub(replaceLine, "\n", x)
		x = re.sub(replaceTD, "\t", x)
		x = re.sub(replacePara, "", x)
		x = re.sub(replaceBR, "\n", x)
		x = re.sub(removeExtraTag, "", x)
		x = re.sub(replacex27, '\'', x)
		x = re.sub(replacegt, '>', x)
		x = re.sub(replacelt, '<', x)
		x = re.sub(replacenbsp, '', x)
		x = re.sub(replace177, u'±', x)
		x = re.sub(replace1, '', x)
		x = re.sub('\n', '', x)
		return x.strip()
	
	def GetProxies(self):
		# 代理服务器
		proxyHost = "http-dyn.abuyun.com"
		proxyPort = "9020"
		# 代理隧道验证信息
		proxyUser = "HI18001I69T86X6D"
		proxyPass = "D74721661025B57D"
		proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
			"host": proxyHost,
			"port": proxyPort,
			"user": proxyUser,
			"pass": proxyPass,
		}
		proxies = {
			"http": proxyMeta,
			"https": proxyMeta,
		}
		return proxies
	
	def get_cookie(self):
		s = requests.Session()
		# print 's.cookies:',s.cookies.get_dict()
		retry = 10
		while 1:
			try:
				user_agents = ['Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20130406 Firefox/23.0',
							   'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0',
							   'IBM WebExplorer /v0.94', 'Galaxy/1.0 [en] (Mac OS X 10.5.6; U; en)',
							   'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
							   'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14',
							   'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; TheWorld)',
							   'Opera/9.52 (Windows NT 5.0; U; en)',
							   'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.2pre) Gecko/2008071405 GranParadiso/3.0.2pre',
							   'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.458.0 Safari/534.3',
							   'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/4.0.211.4 Safari/532.0',
							   'Opera/9.80 (Windows NT 5.1; U; ru) Presto/2.7.39 Version/11.00']
				user_agent = random.choice(user_agents)
				headers = {
					'host': "api.m.taobao.com",
					'connection': "keep-alive",
					'cache-control': "no-cache",
					'upgrade-insecure-requests': "1",
					'user-agent': user_agent,
					'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
					'accept-encoding': "gzip, deflate, br",
					'accept-language': "zh-CN,zh;q=0.9"
				}
				urls = ['https://api.m.taobao.com/h5/mtop.msp.qianggou.queryitembybatchid/3.1/?',
				        'https://api.m.taobao.com/h5/com.taobao.redbull.getpassworddetail/1.0/?']
				url0 = random.choice(urls)
				# cookie = 'cna=M/zAEaDar2kCAXWILYUCOTfq; _m_h5_tk=bd82f50bafe372694b66e9ddc02e2b42_1527576367997; _m_h5_tk_enc=8f8e7858ec8e5c6fc5a14d4ec82fdca5;'
				cookie = 'cna=80NPFMVN720CAW/NuxLikS9t; _m_h5_tk=e0d32e672ec3754c83e7557653435992_1541044778690; _m_h5_tk_enc=44d64929eff47b8d4c2d07be50fdcc41;'
				# headers['cookie'] = cookie
				# req = s.get('https://api.m.taobao.com/h5/mtop.msp.qianggou.queryitembybatchid/3.1/?',headers=headers,proxies=self.GetProxies())
				req = s.get(url0, headers=headers, proxies=self.GetProxies())
				# print s.cookies.get_dict()
				_m_h5_tk, _m_h5_tk_enc = s.cookies.get_dict()['_m_h5_tk'], s.cookies.get_dict()['_m_h5_tk_enc']
				# print '_m_h5_tk:',s.cookies.get_dict()['_m_h5_tk']
				# print '_m_h5_tk_enc:',_m_h5_tk_enc
				cna = str(random.uniform(1, 10))
				cookie = re.sub(re.compile('_m_h5_tk=.*?;'), '_m_h5_tk=%s;' % _m_h5_tk, cookie)
				# print 'cookie_m_h5_tk=',cookie
				cookie = re.sub(re.compile('_m_h5_tk_enc=.*?;'), '_m_h5_tk_enc=%s;' % _m_h5_tk_enc, cookie)
				# print 'cookie_m_h5_tk_enc=', cookie
				cookie = re.sub(re.compile('cna=.*?;'), 'cna=%s;' % cna, cookie)
				t = 't=%s; _tb_token_=%s; cookie2=%s;' % (cna, cna, cna)
				return _m_h5_tk.split('_')[0], cookie + t
			except:
				retry -= 1
				if retry == 0:
					return None
				else:
					continue
	

	def get_comments_num(self, film_id,m_h5_tk, cookie):
		stmp = ''.join(str(time.time()).split('.')) + '0'
		retry = 5
		url = "https://acs.m.taopiaopiao.com/h5/mtop.film.mtopcommentapi.queryindextabshowcomments/7.3/"
		data = '{"type":1,"showId":"%s","cityCode":310100,"platform":"8"}' % film_id
		sign = self.get_sign(m_h5_tk, stmp, '12574478', data)
		while 1:
			try:
				user_agents = ['Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20130406 Firefox/23.0',
							   'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0',
							   'IBM WebExplorer /v0.94', 'Galaxy/1.0 [en] (Mac OS X 10.5.6; U; en)',
							   'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
							   'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14',
							   'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; TheWorld)',
							   'Opera/9.52 (Windows NT 5.0; U; en)',
							   'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.2pre) Gecko/2008071405 GranParadiso/3.0.2pre',
							   'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.458.0 Safari/534.3',
							   'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/4.0.211.4 Safari/532.0',
							   'Opera/9.80 (Windows NT 5.1; U; ru) Presto/2.7.39 Version/11.00']
				user_agent = random.choice(user_agents)
				headers = {
					'host': "acs.m.taopiaopiao.com",
					'connection': "keep-alive",
					'user-agent': user_agent,
					'accept': "*/*",
					'referer': "https://h5.m.taopiaopiao.com/app/moviemain/pages/show-detail/index.html?showid=16743",
					'accept-encoding': "gzip, deflate,br",
					'accept-language': "zh-CN,zh;q=0.9",
					'cookie': cookie
				}
				querystring = {"jsv": "2.4.11",
				               "appKey": "12574478",
				               "t": stmp,
				               "sign": sign,
				               "api": "mtop.film.mtopcommentapi.queryindextabshowcomments", "v": "7.3",
				               "timeout": "10000",
				               "forceAntiCreep": "true",
				               "AntiCreep": "true",
				               "type": "jsonp",
				               "dataType": "jsonp",
				               "callback": "mtopjsonp2",
				               "data": data}
				text = requests.get(url, headers=headers, params=querystring, proxies=self.GetProxies(), timeout=10).text
				p0 = re.compile(u'mtopjsonp2\((.*)\)', re.S)
				t0 = ''.join(re.findall(p0, text))
				t1 = json.loads(t0)
				try:
					comment_num = str(t1['data']['returnValue']['count'])
				except:
					comment_num = '0'
				return comment_num
			except Exception as e:
				retry -= 1
				if retry == 0:
					print e
					return '0'
				else:
					continue

	def executeJS(self, js_func_string, arg):
		'''
		self.ctxt.enter()
		func = self.ctxt.eval("({js})".format(js=js_func_string))
		return func(arg)
		'''
		ctxt = PyV8.JSContext()
		with PyV8.JSLocker():
			ctxt.enter()
			vl5x = ctxt.eval("({js})".format(js=js_func_string))
			sign = vl5x(arg)
			ctxt.leave()
		return sign

	def get_sign(self, m_h5_tk, stmp, appkey, data):
		js_func = self.sign_js
		js_arg = m_h5_tk + '&' + stmp + '&' + appkey + '&' + data
		try:
			sign = self.executeJS(js_func, js_arg)
		except:
			sign = ''
		return sign
	
	def get_t_movie_summary(self, film_id, product_number, plat_number,table_name):
		try:
			m_h5_tk, cookie = self.get_cookie()
		except:
			return None
		stmp = ''.join(str(time.time()).split('.')) + '0'
		retry = 5
		url = "https://acs.m.taopiaopiao.com/h5/mtop.film.mtopshowapi.getextendshowbyid/5.4/"
		data = '{"showid":"%s","cityCode":310100,"platform":"8"}' % film_id
		sign = self.get_sign(m_h5_tk, stmp, '12574478', data)
		while 1:
			try:
				user_agents = ['Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20130406 Firefox/23.0',
							   'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0',
							   'IBM WebExplorer /v0.94', 'Galaxy/1.0 [en] (Mac OS X 10.5.6; U; en)',
							   'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
							   'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14',
							   'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; TheWorld)',
							   'Opera/9.52 (Windows NT 5.0; U; en)',
							   'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.2pre) Gecko/2008071405 GranParadiso/3.0.2pre',
							   'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.458.0 Safari/534.3',
							   'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/4.0.211.4 Safari/532.0',
							   'Opera/9.80 (Windows NT 5.1; U; ru) Presto/2.7.39 Version/11.00']
				user_agent = random.choice(user_agents)
				headers = {
					'host': "acs.m.taopiaopiao.com",
					'connection': "keep-alive",
					'user-agent': user_agent,
					'accept': "*/*",
					'referer': "https://h5.m.taopiaopiao.com/app/moviemain/pages/show-detail/index.html?showid=16743",
					'accept-encoding': "gzip, deflate,br",
					'accept-language': "zh-CN,zh;q=0.9",
					'cookie': cookie
				}
				querystring = {"jsv": "2.4.11",
				               "appKey": "12574478",
				               "t": stmp,
				               "sign": sign,
				               "api": "mtop.film.MtopShowAPI.getExtendShowById",
				               "v": "5.4",
				               "timeout": "10000",
				               "forceAntiCreep": "true",
				               "AntiCreep": "true",
				               "type": "jsonp",
				               "dataType": "jsonp",
				               "callback": "mtopjsonp1",
				               "data": data}
				text = requests.get(url, headers=headers, params=querystring, proxies=self.GetProxies(), timeout=10).text
				p0 = re.compile(u'mtopjsonp1\((.*)\)', re.S)
				t0 = ''.join(re.findall(p0, text))
				t1 = json.loads(t0)
				try:
					score = str(t1['data']['returnValue']['remark'])
				except:
					score = '0'
				comment_num = self.get_comments_num(film_id,m_h5_tk, cookie)
				play_num = '0'
				ticket_num = '0'
				last_modify_date = self.p_time(time.time())
				src_url = film_id
				tmp = [product_number, plat_number, score, play_num, comment_num, ticket_num, last_modify_date, src_url]
				print '|'.join(tmp)
				result_dict = {'product_number': product_number,
				               'plat_number': plat_number,
				               'score': score,
				               'play_num': play_num,
				               'comment_num': comment_num,
				               'ticket_num': ticket_num,
				               'last_modify_date': last_modify_date,
				               'src_url': src_url
				               }
				tmp = self.db.up_data(table_name, result_dict)
				if tmp:
					print u'%s 写入 %s 成功' % (product_number, table_name)
				else:
					print u'%s 写入 %s 失败' % (product_number, table_name)
				return None
			except Exception as e:
				retry -= 1
				print '1',e
				if retry == 0:
					return None
				else:
					continue


if __name__ == "__main__":
	spider = Spider()
	s = []
	with open('new_data.csv') as f:
		tmp = csv.reader(f)
		for i in tmp:
			if 'ID' not in i[2] and len(i[2]) > 0:
				s.append([i[2], i[0], 'P35'])
	for j in s:
		print j[1],j[0]
		spider.get_t_movie_summary(j[0], j[1], j[2], 'T_MOVIE_SUMMARY')
	spider.db.db.close()

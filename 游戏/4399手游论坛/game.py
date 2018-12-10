# -*- coding: utf-8 -*-
# 此程序用来抓取 的数据
import requests
import time
import random
import re
from save_data import database
import csv
from fake_useragent import UserAgent, FakeUserAgentError


class Spider(object):
	def __init__(self):
		self.date = ''
		self.cookie = 'Pnick=deleted; Pauth=2833833529%7Cwgs492741071%7C276d4fbbdbbb93f5aac5824c613c324a%7C1539834082%7C0%7Ce59efee4ee8b0c0f009c1d1cc7f62657%7C; User=%7C2833833529%7Cwgs492741071%7Cf5f46a7016358200173093642c0e243f622cc7fb; smidV2=20181018114125a85d988e6fe42e6d026f36e926a242d300c75d0fb5a62bb80; _4399tongji_vid=153983408547152; _4399tongji_st=1539834085; Hm_lvt_5c9e5e1fa99c3821422bf61e662d4ea5=1539834085; Hm_lvt_da0bce75c9049bf4056836b34215ec4c=1539834085; _ga=GA1.2.1652444340.1539834086; _gid=GA1.2.1380540418.1539834086; ad_forums=1; Hm_lpvt_5c9e5e1fa99c3821422bf61e662d4ea5=1539834419; Hm_lpvt_da0bce75c9049bf4056836b34215ec4c=1539834419'
		self.db = database()
		try:
			self.ua = UserAgent(use_cache_server=False).random
		except FakeUserAgentError:
			pass
	
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
		headers = {'Host': 'bbs.4399.cn',
				   'Connection': 'keep-alive',
		           'User-Agent': user_agent,
		           'Referer': 'http://bbs.4399.cn/forums-mtag-82137-page-2',
		           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		           'Accept-Encoding': 'gzip, deflate, br',
		           'Accept-Language': 'zh-CN,zh;q=0.8',
		           'Cookie': self.cookie
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
		proxyUser = "HK847SP62Z59N54D"
		proxyPass = "C0604DD40C0DD358"
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
	
	def get_total_page(self, game_url):  # 获取网址的总页数
		p0 = re.compile('http[s]?://bbs\.4399\.cn/forums-mtag-(\d+)')
		game_id = re.findall(p0, game_url)[0]
		url = 'http://bbs.4399.cn/forums-mtag-%s-page-1' % game_id
		retry = 5
		while 1:
			try:
				text = requests.get(url, headers=self.get_headers(), proxies=self.GetProxies(), timeout=10).content.decode('utf-8', 'ignore')
				p0 = re.compile(u'共 (.*?) 页')
				total_page = re.findall(p0, text)[1]
				return total_page
			except:
				retry -= 1
				if retry == 0:
					return None
				else:
					continue
	
	def get_t_game_summary(self, game_url, product_number, plat_number, table_name):
		retry = 5
		while 1:
			try:
				text = requests.get(game_url, headers=self.get_headers(), timeout=10).content.decode('utf-8', 'ignore')
				# print text
				try:
					p = re.compile(u'id="mtag_member_num">(\d+?)</span>位成员')
					user_num = re.findall(p, text)[0]
				except:
					user_num = '0'
				title_num = '0'
				score = '0'
				comment_people_num = '0'
				comment_num = '0'
				good_comment_num = '0'
				bad_comment_num = '0'
				played_num = '0'
				want_play_num = '0'
				Install_num = '0'
				last_modify_date = self.p_time(time.time())
				src_url = game_url
				results = [product_number, plat_number, user_num, title_num, score, comment_people_num,
				           comment_num, good_comment_num, bad_comment_num, played_num, want_play_num, Install_num,
				           last_modify_date, src_url]
				print '|'.join(results)
				result_dict = {'product_number': product_number,
				               'plat_number': plat_number,
				               'user_num': user_num,
				               'title_num': title_num,
				               'score': score,
				               'comment_people_num': comment_people_num,
				               'comment_num': comment_num,
				               'good_comment_num': good_comment_num,
				               'bad_comment_num': bad_comment_num,
				               'played_num': played_num,
				               'want_play_num': want_play_num,
				               'install_num': Install_num,
				               'last_modify_date': last_modify_date,
				               'src_url': src_url
				               }
				tmp = self.db.up_data(table_name, result_dict)
				if tmp:
					print u'%s 写入 %s 成功' % (product_number, table_name)
				else:
					print u'%s 写入 %s 失败' % (product_number, table_name)
				return None
			except:
				retry -= 1
				if retry == 0:
					print '请求失败！'
					return None
				else:
					continue


if __name__ == "__main__":
	# 4399需要登陆，你这边注册一个4399的账号，登陆一次，然后获取cookie换掉self.cookie就可以运行程序了
	# 4399需要登陆，你这边注册一个4399的账号，登陆一次，然后获取cookie换掉self.cookie就可以运行程序了
	# 4399需要登陆，你这边注册一个4399的账号，登陆一次，然后获取cookie换掉self.cookie就可以运行程序了
	# 4399需要登陆，你这边注册一个4399的账号，登陆一次，然后获取cookie换掉self.cookie就可以运行程序了
	spider = Spider()
	s1 = []
	with open('data.csv') as f:
		tmp = csv.reader(f)
		for i in tmp:
			if 'http' in i[2]:
				s1.append([i[2], i[0], 'P28'])
	for j in s1:
		print j[1],j[0]
		spider.get_t_game_summary(j[0], j[1], j[2], 'T_GAME_SUMMARY')
	spider.db.db.close()

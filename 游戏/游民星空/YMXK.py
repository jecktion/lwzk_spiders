# -*- coding: utf-8 -*-
# 此程序用来抓取 的数据
import hashlib
import os

import requests
import time
import random
import re
from save_data import database
import csv
import json
from selenium import webdriver


class Spider(object):
	def __init__(self):
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
		headers = {'host': "shouyou.gamersky.com",
		           'connection': "keep-alive",
		           'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
		           'accept': "*/*",
		           'referer': "http://ku.gamersky.com/2015/pal6/",
		           'accept-encoding': "gzip, deflate",
		           'accept-language': "zh-CN,zh;q=0.9"
		           }
		return headers
	
	def p_time(self, stmp):  # 将时间戳转化为时间
		stmp = float(str(stmp)[:10])
		timeArray = time.localtime(stmp)
		otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
		return otherStyleTime
	
	def replace(self, x):
		# 将其余标签剔除
		removeExtraTag = re.compile('<.*?>', re.S)
		x = re.sub(removeExtraTag, "", x)
		x = re.sub('\n', '  ', x)
		x = re.sub(re.compile('\s{2,}'), '  ', x)
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
		# print 'proxies:',proxies
		return proxies
	
	def get_md5(self, s):
		hl = hashlib.md5()
		hl.update(s.encode(encoding='utf-8'))
		return hl.hexdigest()
	
	def save_pic(self, pic_url, pic_name):  # 保存图片
		path = os.path.join(os.getcwd(), 'IMAGE')
		if not os.path.exists(path):
			os.mkdir(path)
		filename1 = pic_name
		filename2 = os.path.join(path, filename1.encode('gbk'))
		retry = 3
		while 1:
			try:
				content = requests.get(pic_url, proxies=self.GetProxies(), timeout=10).content
				break
			except:
				retry -= 1
				if retry == 0:
					return '0'
				else:
					continue
		with open(filename2, 'wb') as f:
			f.write(content)
		return '1'
	
	def get_t_game_1(self, game_url, product_number, plat_number,table_name):
		retry = 5
		while 1:
			try:
				headers = self.get_headers()
				headers['host'] = 'ku.gamersky.com'
				text = requests.get(game_url, headers=headers, proxies=self.GetProxies(), timeout=10).content.decode('utf-8', 'ignore')
				try:
					p = re.compile(u'<div class="tag">.*?target=\'_blank\'>(.*?)</a>', re.S)
					category = ';'.join(re.findall(p, text))
				except:
					category = ''
				try:
					p0 = re.compile(u'<div class="win" tit="游戏平台">(.*?)</div>', re.S)
					t1 = re.findall(p0, text)[0]
					p = re.compile('<a href="javascr.*?>(.*?)</a>', re.S)
					os_game = ';'.join(re.findall(p, t1))
				except:
					os_game = ''
				try:
					p = re.compile(u'制作发行：</div><div class="txt">(.*?)</div></div>')
					t1 = re.findall(p, text)[0].split('/')
					if len(t1) == 2:
						dev_company, publish_company = t1
					else:
						dev_company = t1[0]
						publish_company = ''
				except:
					dev_company, publish_company = '', ''
				try:
					p = re.compile(u'data-time="([\d+]{4})-[\d+]{2}-[\d+]{2}')
					first_show_year_global = re.findall(p, text)[0]
					print 'first_show_year_global 1:',first_show_year_global
				except:
					first_show_year_global = ''
					print 'first_show_year_global 1:', first_show_year_global
				try:
					p = re.compile(u'<div class="con-hide">(.*?)</div>', re.S)
					game_desc = self.replace(re.findall(p, text)[0])
				except:
					game_desc = ''
				try:
					product_image = self.get_md5(product_number + plat_number)
					p = re.compile('<div class="YXXX-L">.*?<img src="(.*?)"', re.S)
					pic_url = re.findall(p, text)[0]
					self.save_pic(pic_url, product_image)
				except:
					product_image = self.get_md5(product_number + plat_number)
				last_modify_date = self.p_time(time.time())
				src_url = game_url
				tmp = [product_number, plat_number, category, os_game, dev_company, publish_company,
				       first_show_year_global, game_desc, product_image, last_modify_date, src_url]
				print '|'.join(tmp)
				result_dict = {'product_number': product_number,
				               'plat_number': plat_number,
				               'category': category,
				               'os': os_game,
				               'dev_company': dev_company,
				               'publish_company': publish_company,
				               'first_show_year_global': first_show_year_global,
				               'game_desc': game_desc,
				               'product_image': product_image,
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
					return None
				else:
					continue
	
	def get_t_game(self, game_url, product_number, plat_number,table_name):  # 获取t_game
		retry = 5
		while 1:
			try:
				text = requests.get(game_url, headers=self.get_headers(), proxies=self.GetProxies(), timeout=10).content.decode('utf-8', 'ignore')
				try:
					p = re.compile(u'\| 类型：(.*?)</div>', re.S)
					category = ';'.join(re.findall(p, text)[0].split())
				except:
					try:
						p = re.compile(u'<span>类型：(.*?)</span>')
						category = re.findall(p, text)[0]
					except:
						category = ''
				os_game = 'iOS;Android'
				try:
					p = re.compile(u'<div class="box_txt">开发：(.*?) \|', re.S)
					dev_company = ';'.join(re.findall(p, text))
				except:
					dev_company = ''
				try:
					publish_company = dev_company
				except:
					publish_company = ''
				try:
					p = re.compile(u'上市：([\d+]{4})-')
					first_show_year_global = re.findall(p, text)[0]
					print 'first_show_year_global: 0',first_show_year_global
				except:
					first_show_year_global = ''
				try:
					p = re.compile(u'<div class="Intro" id="Intro">(.*?)<div class="sort_btn">', re.S)
					game_desc = self.replace(re.findall(p, text)[0])
				except:
					game_desc = ''
				try:
					product_image = self.get_md5(product_number + plat_number)
					p = re.compile('<div class="box_img"><img src="(.*?)"')
					pic_url = re.findall(p, text)[0]
					self.save_pic(pic_url, product_image)
				except:
					try:
						product_image = self.get_md5(product_number + plat_number)
						p = re.compile('target="_blank"><img alt=".*?" src="(.*?)"')
						pic_url = re.findall(p, text)[0]
						self.save_pic(pic_url, product_image)
					except:
						product_image = self.get_md5(product_number + plat_number)
				last_modify_date = self.p_time(time.time())
				src_url = game_url
				tmp = [product_number, plat_number, category, os_game, dev_company, publish_company,
				       first_show_year_global, game_desc, product_image, last_modify_date, src_url]
				print '|'.join(tmp)
				result_dict = {'product_number': product_number,
				               'plat_number': plat_number,
				               'category': category,
				               'os': os_game,
				               'dev_company': dev_company,
				               'publish_company': publish_company,
				               'first_show_year_global': first_show_year_global,
				               'game_desc': game_desc,
				               'product_image': product_image,
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
					return None
				else:
					continue
	
	def get_t_game_summary(self, game_url, product_number, plat_number,table_name):
		retry = 5
		while 1:
			try:
				chromedriver = 'C:\Users\Administrator\AppData\Local\Google\Chrome\Application\chromedriver.exe'
				chrome_options = webdriver.ChromeOptions()
				chrome_options.add_argument('--headless')
				# chrome_options.add_argument(('--proxy-server=http://' + ip:端口))
				# os.environ["webdriver.chrome.driver"] = chromedriver
				driver = webdriver.Chrome(chrome_options=chrome_options,
				                          executable_path=os.path.join(os.getcwd(), chromedriver))
				
				driver.get(game_url)
				time.sleep(2)
				text = driver.page_source
				# print text
				user_num = '0'
				title_num = '0'
				p1 = re.compile(u'id="scoreAvg">(.*?)</div>', re.S)
				try:
					score = re.findall(p1, text)[0]
				except:
					score = '0'
				try:
					p = re.compile(u'<span id="scoreTimes">(\d+?)</span>票')
					comment_people_num = re.findall(p, text)[0]
				except:
					comment_people_num = '0'
				try:
					p = re.compile(u'<span>评论\(<i class="cy_comment" data-sid="\d+?" data-lddt="yes">(\d+?)</i>')
					comment_num = re.findall(p, text)[0]
				except:
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
				driver.quit()
				return None
			except:
				retry -= 1
				if retry == 0:
					driver.quit()
					return None
				else:
					continue
	
	def get_score(self, game_id):  # 获取端游的评分和评分人数
		url = "http://cm1.gamersky.com/apirating/getplayersscore"
		querystring = {"jsondata": "{\"genneralId\":\"%s\",\"num\":\"10\"}" % game_id}
		retry = 5
		while 1:
			try:
				text = requests.get(url, params=querystring, proxies=self.GetProxies(), timeout=10).text
				p1 = re.compile('\((.*)\)')
				text = re.findall(p1, text)[0]
				text = json.loads(text)
				score = str(text['sorce'])
				if '--' in score:
					score = '0'
				totalnumber = str(text['totalnumber'])
				return score, totalnumber
			except Exception as e:
				print e
				retry -= 1
				if retry == 0:
					return '0', '0'
				else:
					continue
	
	def get_comment_want(self, game_id):  # 获取玩过和想玩评论数
		url = "http://cm1.gamersky.com/api/GetComment"
		querystring = {
			"jsondata": "{\"dateType\":\"1\",\"loadType\":\"1\",\"pageIndex\":1,\"pageSize\":2,\"foorPageSize\":5,\"articleId\":\"%s\"}" % game_id}
		retry = 5
		while 1:
			try:
				text = requests.get(url, params=querystring, proxies=self.GetProxies(), timeout=10).text
				p1 = re.compile('\((.*)\)')
				text = re.findall(p1, text)[0]
				text = json.loads(text)['body']
				p1 = re.compile('"PlayedCount\":(\d+?),\"WantPlayCount\":(\d+?),')
				played_num, want_play_num = re.findall(p1, text)[0]
				all_count = int(played_num) + int(want_play_num)
				return str(all_count), played_num, want_play_num
			except:
				retry -= 1
				if retry == 0:
					return '0', '0', '0'
				else:
					continue
	
	def get_t_game_summary_1(self, game_url, product_number, plat_number,table_name):
		retry = 5
		while 1:
			try:
				headers = self.get_headers()
				headers['host'] = 'ku.gamersky.com'
				text = requests.get(game_url, headers=headers, proxies=self.GetProxies(), timeout=10).content.decode('utf-8', 'ignore')
				# print text
				user_num = '0'
				title_num = '0'
				try:
					p = re.compile('data-generalid="(\d+?)"')
					game_id = re.findall(p, text)[0]
					print game_id
					score, comment_people_num = self.get_score(game_id)
				except:
					score, comment_people_num = '0', '0'
				good_comment_num = '0'
				bad_comment_num = '0'
				try:
					p = re.compile('data-generalid="(\d+?)"')
					game_id = re.findall(p, text)[0]
					comment_num, played_num, want_play_num = self.get_comment_want(game_id)
				except:
					comment_num, played_num, want_play_num = '0', '0', '0'
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
					return None
				else:
					continue


if __name__ == "__main__":
	spider = Spider()
	s1 = []
	with open('data.csv') as f:
		tmp = csv.reader(f)
		for i in tmp:
			if 'http' in i[2]:
				s1.append([i[2], i[0], 'P29'])
	for s in s1:
		print s[1],s[0]
		if 'ku.gamersky.com' in s[0]:
			spider.get_t_game_1(s[0], s[1], s[2],'T_GAME')
			spider.get_t_game_summary_1(s[0], s[1], s[2],'T_GAME_SUMMARY')
		else:
			spider.get_t_game(s[0], s[1], s[2], 'T_GAME')
			spider.get_t_game_summary(s[0], s[1], s[2],'T_GAME_SUMMARY')
			

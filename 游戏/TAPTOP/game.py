# -*- coding: utf-8 -*-
# 此程序用来抓取 的数据
import hashlib
import os

import requests
import time
import random
import re
import csv
from fake_useragent import UserAgent, FakeUserAgentError
from save_data import database


class Spider(object):
	def __init__(self):
		self.ct_time = []
		self.date = ''
		self.db = database()
		try:
			self.ua = UserAgent(use_cache_server=False).random
		except FakeUserAgentError as e:
			print u'浏览器错误！',e
	
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
		headers = {'Host': 'www.taptap.com',
				   'Connection': 'keep-alive',
		           'User-Agent': user_agent,
		           'Referer': 'https://www.taptap.com/app/6514/review?order=default&page=2#review-list',
		           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		           'Accept-Encoding': 'gzip, deflate, br',
		           'Accept-Language': 'zh-CN,zh;q=0.8',
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
		x = re.sub(re.compile('\s{2,}'), ' ', x)
		x = re.sub(re.compile('[\n\r]'), ' ', x)
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
	
	def get_md5(self, s):
		hl = hashlib.md5()
		hl.update(s.encode(encoding='utf-8'))
		return hl.hexdigest()
	
	def get_t_game(self, game_url, product_number, plat_number,table_name):  # 获取游戏的基本信息
		game_url = game_url.replace('/review', '')
		retry = 5
		while 1:
			try:
				text = requests.get(game_url, headers=self.get_headers(), proxies=self.GetProxies(), timeout=10).text
				try:
					p = re.compile(
						u'<ul class="list-unstyled list-inline side-body-tag" id="appTag">(.*?)<li class="tag-add"',
						re.S)
					tmp1 = re.findall(p, text)[0]
					p1 = re.compile('<a href="https://www\.taptap\.com/tag/.*?>(.*?)</a>', re.S)
					category = ';'.join([x.strip() for x in re.findall(p1, tmp1)])
				except:
					category = ''
				os_1 = 'IOS;Android'
				try:
					p = re.compile(u'<span>开发商: </span>.*?<span itemprop="name">(.*?)</span>', re.S)
					dev_company = re.findall(p, text)[0]
				except:
					try:
						p = re.compile(u'<span>厂商: </span>.*?<span itemprop="name">(.*?)</span>', re.S)
						dev_company = re.findall(p, text)[0]
					except:
						dev_company = ''
				try:
					p = re.compile(u'<span>发行商: </span>.*?<span itemprop="name">(.*?)</span>', re.S)
					publish_company = re.findall(p, text)[0]
				except:
					publish_company = ''
				first_show_year_global = ''
				p0 = re.compile(
					'<div class="body-description-paragraph" id="description">(.*?)<div class="body-description-more">',
					re.S)
				try:
					game_desc = self.replace(re.findall(p0, text)[0])
				except:
					game_desc = ''
				p1 = re.compile('<img itemprop="image".*?src="(.*?)"', re.S)
				try:
					product_image = self.get_md5(product_number + plat_number)
					pic_url = re.findall(p1, text)[0]
					self.save_pic(pic_url, product_image)
				except:
					product_image = ''
				last_modify_date = self.p_time(time.time())
				src_url = game_url
				results = [product_number, plat_number, category, os_1, dev_company, publish_company,
				           first_show_year_global,
				           game_desc, product_image, last_modify_date, src_url]
				print '|'.join(results)
				result_dict = {'product_number': product_number,
				               'plat_number': plat_number,
				               'category': category,
				               'os': os_1,
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
			except Exception as e:
				retry -= 1
				if retry == 0:
					print e
					return None
				else:
					continue
	
	def get_t_game_summary(self, game_url, product_number, plat_number,table_name):  # 获取 t_game_summary的数据
		retry = 5
		while 1:
			try:
				text = requests.get(game_url, headers=self.get_headers(), proxies=self.GetProxies(), timeout=10).text
				p0 = re.compile(u'<span class="count-stats">(\d+?) 人关注</span>', re.S)
				try:
					user_num = re.findall(p0, text)[0]
				except:
					user_num = '0'
				try:
					p = re.compile(
						u'rel="nofollow">论坛                                             <small>(\d+?)</small></a>',
						re.S)
					title_num = re.findall(p, text)[0]
				except:
					title_num = '0'
				p1 = re.compile(' class="app-rating-score">(.*?)</span>', re.S)
				try:
					score = re.findall(p1, text)[0]
				except:
					score = '0'
				comment_people_num = '0'
				p2 = re.compile(u'评价                                             <small>(\d+?)</small></a>')
				try:
					comment_num = re.findall(p2, text)[0]
				except:
					comment_num = '0'
				good_comment_num = '0'
				bad_comment_num = '0'
				played_num = '0'
				want_play_num = '0'
				p3 = re.compile(u'<span class="count-stats">(\d+?) 人安装</span>')
				try:
					Install_num = re.findall(p3, text)[0]
				except:
					Install_num = '0'
				last_modify_date = self.p_time(time.time())
				src_url = game_url
				results = [product_number, plat_number, user_num, title_num, score, comment_people_num,
				           comment_num, good_comment_num, bad_comment_num, played_num, want_play_num, Install_num,
				           last_modify_date, src_url]
				print '|'.join(results)
				result_dict = {'product_number': product_number,
				               'plat_number': plat_number,
				               'user_num':user_num,
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
			except Exception as e:
				retry -= 1
				if retry == 0:
					print u'请求出错',e
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
				s1.append([i[2], i[0], 'P26'])
	for j in s1:
		print j[1],j[0]
		spider.get_t_game(j[0], j[1], j[2], 'T_GAME')
		spider.get_t_game_summary(j[0], j[1], j[2], 'T_GAME_SUMMARY')
	spider.db.db.close()

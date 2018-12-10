# -*- coding: utf-8 -*-
# 此程序用来抓取 的数据
import hashlib
import os

import requests
import time
import re
import random
from multiprocessing.dummy import Pool
import csv
from fake_useragent import UserAgent, FakeUserAgentError
from save_data import database


class Spider(object):
	def __init__(self):
		self.db = database()
		try:
			self.ua = UserAgent(use_cache_server=False).random
		except FakeUserAgentError:
			pass
	
	def get_headers(self):
		try:
			user_agent = self.ua.chrome
			headers = {'Host': 'apicdn.sc.pptv.com', 'Connection': 'keep-alive',
					   'User-Agent': user_agent,
					   'Referer': 'http://v.pptv.com/show/NnJb2UGnF1W4Np4.html?spm=pc_search_web.search.result.1',
					   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
					   'Accept-Encoding': 'gzip, deflate, br',
					   'Accept-Language': 'zh-CN,zh;q=0.8'
					   }
		except:
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
			headers = {'Host': 'apicdn.sc.pptv.com', 'Connection': 'keep-alive',
					   'User-Agent': user_agent,
					   'Referer': 'http://v.pptv.com/show/NnJb2UGnF1W4Np4.html?spm=pc_search_web.search.result.1',
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
		# 将其余标签剔除
		removeExtraTag = re.compile('<.*?>', re.S)
		x = re.sub(removeExtraTag, "", x)
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
	
	def get_vod(self, film_url):  # 获取电影的VOD
		retry = 5
		while 1:
			try:
				headers = self.get_headers()
				headers['host'] = 'v.pptv.com'
				text = requests.get(film_url, headers=headers, proxies=self.GetProxies(), timeout=10).text
				p0 = re.compile(u'var webcfg = \{"id":(\d+?),')
				vod = re.findall(p0, text)[0]
				return vod
			except:
				retry -= 1
				if retry == 0:
					return None
				else:
					continue
	
	def get_comments_num(self, vod):  # 获取评论数目
		if vod == '0':
			return '0'
		url = "http://apicdn.sc.pptv.com/sc/v4/pplive/ref/vod_%s/feed/list" % vod
		querystring = {"appplt": "web", "action": "1", "pn": '0', "ps": "20"}
		retry = 20
		while 1:
			try:
				text = requests.get(url, proxies=self.GetProxies(), headers=self.get_headers(), timeout=10,
				                    params=querystring).json()
				total = str(text['data']['total'])
				return total
			except Exception as e:
				retry -= 1
				if retry == 0:
					print e
					return '0'
				else:
					continue
	
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
				content = requests.get(pic_url, timeout=10).content
				break
			except:
				retry -= 1
				if retry == 0:
					print '图片保存失败！'
					return '0'
				else:
					continue
		with open(filename2, 'wb') as f:
			f.write(content)
		print '图片保存成功！'
		return '1'
	
	def get_t_movie(self, film_url, product_number, plat_number, table_name):
		retry = 10
		while 1:
			try:
				headers = {
					'host': "v.pptv.com",
					'connection': "keep-alive",
					'cache-control': "no-cache",
					'upgrade-insecure-requests': "1",
					'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
					'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
					'accept-encoding': "gzip, deflate",
					'accept-language': "zh-CN,zh;q=0.9"
				}
				text = requests.get(film_url, proxies=self.GetProxies(), headers=headers, timeout=10).text
				if u'<meta name="title" content=' not in text:
					retry -= 1
					if retry == 0:
						return None
					else:
						continue
				try:
					p0 = re.compile(u'<li>导演：(.*?)</li>', re.S)
					t = re.findall(p0, text)[0].split('</a>')
					t1 = [self.replace(x) for x in t[:-1]]
					directors = ';'.join(t1)
				except:
					directors = ''
				try:
					p1 = re.compile(u'<li>地区：(.*?)</li>', re.S)
					area = self.replace(re.findall(p1, text)[0])
				except:
					area = ''
				try:
					p2 = re.compile(u'class="now">分集\((\d+?)\)</a>', re.S)
					sets_number = re.findall(p2, text)[0]
				except:
					sets_number = '1'
				product_type = ''
				try:
					p = re.compile(u'<li class="actor">主演：(.*?)</li>', re.S)
					t = re.findall(p, text)[0].split('</a>')
					t1 = [self.replace(x) for x in t[:-1]]
					actors = ';'.join(t1)
				except:
					actors = ''
				try:
					p4 = re.compile(u'<div class="intro j_intro">(.*?)</div>', re.S)
					movie_desc = self.replace(re.findall(p4, text)[0])
					movie_desc = re.sub(re.compile('\s{2,}'), ' ', movie_desc)
				except:
					movie_desc = ''
				try:
					p5 = re.compile(u'<li>上映：<a target="_blank" href=".*?" title="">(\d+?)</a></li>', re.S)
					first_show_year_global = re.findall(p5, text)[0]
				except:
					first_show_year_global = ''
				try:
					product_image = self.get_md5(product_number + plat_number)
					p6 = re.compile(u'<img data-src2="(.*?)"')
					pic_url = re.findall(p6, text)[0]
					self.save_pic(pic_url, product_image)
				except:
					product_image = self.get_md5(product_number + plat_number)
				last_modify_date = self.p_time(time.time())
				tmp = [product_number, plat_number, directors, area, sets_number, product_type,
				       actors, movie_desc, first_show_year_global, product_image, last_modify_date, film_url]
				print '|'.join(tmp)
				result_dict = {'product_number': product_number,
				               'plat_number': plat_number,
				               'director': directors,
				               'area': area,
				               'sets_number':sets_number,
				               'product_type':product_type,
				               'actors':actors,
				               'movie_desc':movie_desc,
				               'first_show_year_global':first_show_year_global,
				               'product_image':product_image,
				               'last_modify_date': last_modify_date,
				               'src_url': film_url
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
	
	def get_t_movie_summary(self, film_url, product_number, plat_number, table_name):
		retry = 8
		while 1:
			try:
				headers = {
					'host': "v.pptv.com",
					'connection': "keep-alive",
					'cache-control': "no-cache",
					'upgrade-insecure-requests': "1",
					'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
					'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
					'accept-encoding': "gzip, deflate",
					'accept-language': "zh-CN,zh;q=0.9"
				}
				text = requests.get(film_url, proxies=self.GetProxies(), headers=headers, timeout=10).text
				if u'<meta name="title" content=' not in text:
					retry -= 1
					if retry == 0:
						return None
					else:
						continue
				p0 = re.compile(u'var webcfg = \{"id":(\d+?),')
				try:
					vod = re.findall(p0, text)[0]
				except:
					vod = '0'
				try:
					p1 = re.compile(u'<b class="score">(.*?)</b>')
					score = re.findall(p1, text)[0]
				except:
					score = '0'
				try:
					comment_num = self.get_comments_num(vod)
				except:
					comment_num = '0'
				try:
					p2 = re.compile(u'<li>播放：(.*?)</li>', re.S)
					play_num = re.findall(p2, text)[0].replace(',', '')
					if u'万' in play_num:
						play_num = float(play_num.replace(u'万', '')) * 10000
						play_num = '%.0f' % play_num
					if u'亿' in play_num:
						play_num = float(play_num.replace(u'亿', '')) * 100000000
						play_num = '%.0f' % play_num
				except:
					play_num = '0'
				ticket_num = '0'
				last_modify_date = self.p_time(time.time())
				src_url = film_url
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
				if retry == 0:
					print e
					return None
				else:
					continue


if __name__ == "__main__":
	spider = Spider()
	s = []
	with open('new_data.csv') as f:
		tmp = csv.reader(f)
		for i in tmp:
			if 'http' in i[2]:
				s.append([i[2], i[0], 'P06'])
	for j in s:
		print j[1],j[0]
		spider.get_t_movie(j[0], j[1], j[2], 'T_MOVIE')
		spider.get_t_movie_summary(j[0], j[1], j[2], 'T_MOVIE_SUMMARY')
	spider.db.db.close()

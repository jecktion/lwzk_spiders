# -*- coding: utf-8 -*-
# 此程序用来抓取 的数据
import hashlib
import os

import requests
import time
import random
import re
from multiprocessing.dummy import Pool
import csv
from save_data import database


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
		headers = {'Host': 'v.youku.com', 'Connection': 'keep-alive',
		           'User-Agent': user_agent,
		           'Referer': 'https://v.youku.com/v_show/id_XMzU3MzUyNjYyMA==.html?spm=a2h0k.11417342.soresults.dtitle&s=50efbfbdefbfbd5fefbf',
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
		x = re.sub('/', ';', x)
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
	
	def get_movie_id(self, film_url):  # 获取电影id
		retry = 5
		while 1:
			try:
				text = requests.get(film_url, headers=self.get_headers(), proxies=self.GetProxies(), timeout=10).text
				# print text
				p0 = re.compile(u'videoId: \'(\d+?)\'')
				videoId = re.findall(p0, text)[0]
				return videoId
			except Exception as e:
				retry -= 1
				if retry == 0:
					print e
					return None
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
	
	def normal_url(self, film_url):
		if 'list' in film_url:
			return film_url
		retry = 5
		while 1:
			try:
				text = requests.get(film_url, proxies=self.GetProxies(), timeout=10).text
				p0 = re.compile(u'<a href="(.*?)" target="_blank" class="" title=".*?">')
				url0 = re.findall(p0, text)[0]
				film_url = 'https:' + url0
				return film_url
			except:
				retry -= 1
				if retry == 0:
					return None
				else:
					continue
	
	def get_t_movie(self, film_url, product_number, plat_number, table_name):
		retry = 5
		while 1:
			try:
				text = requests.get(film_url, proxies=self.GetProxies(), timeout=10).text
				try:
					p0 = re.compile(u'><li><b>导演：</b> <span title="(.*?)">', re.S)
					directors = self.replace(re.findall(p0, text)[0])
				except:
					directors = ''
				try:
					p1 = re.compile(u'国家/地区：</b> <span title="(.*?)">', re.S)
					area = self.replace(re.findall(p1, text)[0])
				except:
					area = ''
				try:
					p2 = re.compile(u'<span class="total_num">(.*?)</span>', re.S)
					sets_number = re.findall(p2, text)[0]
				except:
					sets_number = '1'
				try:
					p3 = re.compile(u'<li><b>类型：</b> <span title="(.*?)">')
					product_type = self.replace(re.findall(p3, text)[0])
				except:
					product_type = ''
				try:
					p = re.compile(u'<b>主演：</b> <span title="(.*?)"')
					actors = re.findall(p, text)[0].replace('/', ';')
				except:
					actors = ''
				try:
					p4 = re.compile(u'<b>简介：</b> <span class="des_con">(.*?)</span>', re.S)
					movie_desc = re.findall(p4, text)[0]
				except:
					movie_desc = ''
				try:
					p5 = re.compile(u'><b>年代：</b> <span title="(\d+?)-', re.S)
					first_show_year_global = re.findall(p5, text)[0]
				except:
					try:
						p5 = re.compile(u'><b>上映：</b> <span title="(\d+?)-', re.S)
						first_show_year_global = re.findall(p5, text)[0]
					except:
						first_show_year_global = ''
				try:
					product_image = self.get_md5(product_number + plat_number)
					p6 = re.compile(u'<div class="inner_left"id="play_pic">.*?<img src="(.*?)"')
					pic_url = re.findall(p6, text)[0]
					self.save_pic(pic_url, product_image)
				except:
					product_image = self.get_md5(product_number + plat_number)
				last_modify_date = self.p_time(time.time())
				tmp = [product_number, plat_number, directors, area, sets_number, product_type,
				       actors, movie_desc, first_show_year_global, product_image, last_modify_date, film_url]
				print '|'.join(tmp)
				'''
				with open('data_t_movie.csv', 'a') as f:
					writer = csv.writer(f, lineterminator='\n')
					writer.writerow(tt)
				'''
				result_dict = {'product_number': product_number,
				               'plat_number': plat_number,
				               'director': directors,
				               'area': area,
				               'sets_number': sets_number,
				               'product_type': product_type,
				               'actors': actors,
				               'movie_desc': movie_desc,
				               'first_show_year_global': first_show_year_global,
				               'product_image': product_image,
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
		retry = 5
		while 1:
			try:
				text = requests.get(film_url, proxies=self.GetProxies(), timeout=10).text
				try:
					p1 = re.compile(u'<span class="sorce_num">(.*?)</span>')
					score = re.findall(p1, text)[0]
				except:
					score = '0'
				try:
					p2 = re.compile(u'总评论数：</b> <span>(.*?)</span>', re.S)
					comment_num = re.findall(p2, text)[0].replace(',', '')
					if u'万' in comment_num:
						comment_num = float(comment_num.replace(u'万', '')) * 10000
						comment_num = '%.0f' % comment_num
					if u'亿' in comment_num:
						comment_num = float(comment_num.replace(u'亿', '')) * 100000000
						comment_num = '%.0f' % comment_num
				except:
					comment_num = '0'
				try:
					p2 = re.compile(u'总播放数：</b> <span>(.*?)</span>', re.S)
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
			except:
				retry -= 1
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
			if 'http' in i[2]:
				s.append([i[0], i[2]])
	for j in s:
		try:
			print j[0],j[1]
			spider.get_t_movie(j[1], j[0], 'P04', 'T_MOVIE')
			spider.get_t_movie_summary(j[1], j[0], 'P04', 'T_MOVIE_SUMMARY')
		except:
			continue
	spider.db.db.close()

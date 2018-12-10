# -*- coding: utf-8 -*-
# 此程序用来抓取哔哩哔哩的数据
import hashlib
import os

import requests
import time
import re
from multiprocessing.dummy import Pool
import csv
import random
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
			headers = {'host': "api-t.iqiyi.com",
					   'connection': "keep-alive",
					   'user-agent': user_agent,
					   'accept': "*/*",
					   'referer': "http://www.iqiyi.com/lib/m_216426014.html?src=search",
					   'accept-encoding': "gzip, deflate",
					   'accept-language': "zh-CN,zh;q=0.9"
					   }
		except AttributeError:
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
			headers = {'host': "api-t.iqiyi.com",
					   'connection': "keep-alive",
					   'user-agent': user_agent,
					   'accept': "*/*",
					   'referer': "http://www.iqiyi.com/lib/m_216426014.html?src=search",
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
		x = re.sub('/', ";", x)
		x = re.sub(re.compile('\s{2,}'), ' ', x)
		x = re.sub('\n', ' ', x)
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
	
	def get_film_id(self, text):  # 获取电视剧每一集的id
		p0 = re.compile('"aid":(\d+?),')
		return re.findall(p0,text)
	
	def get_comments_num_video(self, videoid):  # 获取某一个视频的总评论页数
		# print videoid
		url = "https://api.bilibili.com/x/v2/reply"
		querystring = {"pn": "2", "type": "1", "oid": videoid, "sort": "0"}
		headers = {
			'host': "api.bilibili.com",
			'connection': "keep-alive",
			'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
			'accept': "*/*",
			'referer': "https://www.bilibili.com/bangumi/play/ep232978",
			'accept-encoding': "gzip, deflate, br",
			'accept-language': "zh-CN,zh;q=0.9",
			'cookie':'finger=edc6ecda; buvid3=F4AF72ED-200A-4CBF-965D-B7D93F6D7CF86721infoc; LIVE_BUVID=AUTO7015346503106035; fts=1534650364; stardustvideo=1; CURRENT_FNVAL=8; BANGUMI_SS_349_REC=6568; BANGUMI_SS_1733_REC=32374; sid=7ohvnjdu; BANGUMI_SS_5609_REC=100838; BANGUMI_SS_24448_REC=232978'
		}
		retry = 5
		while 1:
			try:
				total = requests.get(url, headers=headers, proxies=self.GetProxies(), params=querystring,timeout=10).json()['data']['page']['acount']
				return total
			except:
				retry -= 1
				if retry == 0:
					return 0
				else:
					continue
	
	def get_commentsnum_total(self, text):  # 获取某个视频的所有评论
		videoids = self.get_film_id(text)
		# print len(videoids)
		pool = Pool(4)
		items = pool.map(self.get_comments_num_video, videoids)
		pool.close()
		pool.join()
		if len(items) > 1 and items[0] == items[-1]:
			total = items[0]
		else:
			total = sum(items)
		return str(total)
	
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
	
	def get_t_movie(self, film_url, product_number, plat_number,table_name):
		if 'bangumi' not in film_url:
			return None
		headers = self.get_headers()
		headers['host'] = 'www.bilibili.com'
		retry = 5
		while 1:
			try:
				text = requests.get(film_url, headers=headers, proxies=self.GetProxies(), timeout=10).text
				directors = ''
				area = ''
				try:
					p2 = re.compile(u'全(\d+?)话', re.S)
					sets_number = re.findall(p2, text)[0]
				except:
					sets_number = '1'
				try:
					p3 = re.compile(u'<span class="media-tag">(.*?)</span>', re.S)
					product_type = ';'.join(re.findall(p3,text))
				except:
					product_type = ''
				actors = ''
				try:
					p4 = re.compile(u'"evaluate":"(.*?)"',re.S)
					movie_desc = self.replace(re.findall(p4, text)[0])
					movie_desc = re.sub(re.compile('\s{2,}'), ' ', movie_desc)
				except:
					movie_desc = ''
				try:
					p5 = re.compile(u'<div class="media-info-time"><span>(\d+?)年', re.S)
					first_show_year_global = re.findall(p5, text)[0]
				except:
					first_show_year_global = ''
				try:
					product_image = self.get_md5(product_number + plat_number)
					p6 = re.compile(u'<meta property="og:image" content="(.*?)">', re.S)
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
	
	def get_t_movie_summary(self, film_url, product_number, plat_number,table_name):  # 获取t_movie_summary
		if 'bangumi' not in film_url:
			return None
		retry = 5
		while 1:
			try:
				text = requests.get(url=film_url, proxies=self.GetProxies(), timeout=10).text
				try:
					p = re.compile(u'<div class="media-info-score-content"><div>(.*?)</div>')
					score = re.findall(p,text)[0]
				except:
					score = '0'
				try:
					p = re.compile(u'总播放</span><em>(.*?)</em>')
					play_num = re.findall(p,text)[0]
					if u'万' in play_num:
						play_num = float(play_num.replace(u'万', '')) * 10000
						play_num = '%.0f' % play_num
					if u'亿' in play_num:
						play_num = float(play_num.replace(u'亿', '')) * 100000000
						play_num = '%.0f' % play_num
				except:
					play_num = '0'
				comment_num = self.get_commentsnum_total(text)
				ticket_num = '0'
				last_modify_date = self.p_time(time.time())
				src_url = film_url
				tmp = [product_number, plat_number, score, play_num, comment_num,ticket_num, last_modify_date, src_url]
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
	with open('data.csv') as f:
		tmp = csv.reader(f)
		for i in tmp:
			if 'http' in i[2]:
				s.append([i[2], i[0], 'P08'])
	for j in s:
		print j[1],j[0]
		spider.get_t_movie(j[0], j[1], j[2], 'T_MOVIE')
		spider.get_t_movie_summary(j[0], j[1], j[2], 'T_MOVIE_SUMMARY')
	spider.db.db.close()

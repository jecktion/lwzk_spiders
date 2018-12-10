# -*- coding: utf-8 -*-
# 此程序用来抓取搜狐视频的数据
import csv
import hashlib
import os

import requests
import random
import time
import re
from fake_useragent import UserAgent, FakeUserAgentError
from  save_data import database
from multiprocessing.dummy import Pool


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
			headers = {'host': "api.my.tv.sohu.com",
					   'connection': "keep-alive",
					   'user-agent': user_agent,
					   'accept': "*/*",
					   'referer': "http://www.iqiyi.com/lib/m_216426014.html?src=search",
					   'accept-encoding': "gzip, deflate",
					   'accept-language': "zh-CN,zh;q=0.9"
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
			headers = {'host': "api.my.tv.sohu.com",
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
	
	def get_pl_id(self, film_url):  # 获取电影id
		retry = 5
		while 1:
			try:
				text = requests.get(url=film_url, proxies=self.GetProxies(), timeout=10).text
				if '/item/' in film_url:
					p = re.compile('var playlistId="(\d+?)";')
				else:
					p = re.compile('var playlistId = "(\d+?)";')
				pl_id = re.findall(p, text)[0]
				return pl_id
			except:
				retry -= 1
				if retry == 0:
					return None
				else:
					continue
	
	def get_film_id(self, plid):  # 获取电视剧每一集的id
		url = "http://pl.hd.sohu.com/videolist"
		
		querystring = {"playlistid": plid, "order": "0", "cnt": "1", "withLookPoint": "1", "preVideoRule": "1",
		               "ssl": "0"}
		retry = 5
		while 1:
			try:
				film_ids = []
				text = requests.get(url, proxies=self.GetProxies(), params=querystring, timeout=10).json()['videos']
				for item in text:
					film_ids.append(item['vid'])
				if len(film_ids) == 0:
					return None
				else:
					return film_ids
			except:
				retry -= 1
				if retry == 0:
					return None
				else:
					continue
	
	def get_comments_num_video(self, videoid):  # 获取某一个视频的总评论页数
		# print 'videoid:',videoid
		url = "https://api.my.tv.sohu.com/comment/api/v1/load"
		querystring = {"topic_id": videoid,
		               "topic_type": "1",
		               "source": "2",
		               "page_size": "10",
		               "sort": "0",
		               "ssl": "0",
		               "page_no": "1",
		               "reply_size": "2"}
		retry = 5
		while 1:
			try:
				total = requests.get(url, params=querystring, proxies=self.GetProxies(), timeout=10).json()['data']['comment_count']
				return total
			except:
				retry -= 1
				if retry == 0:
					return 0
				else:
					continue
	
	def get_commentsnum_total(self, plid):  # 获取某个视频的所有评论
		videoids = self.get_film_id(plid)
		if videoids is None:
			return '0'
		# print 'len(videoids):',len(videoids)
		pool = Pool(2)
		items = pool.map(self.get_comments_num_video, videoids)
		pool.close()
		pool.join()
		total = sum(items)
		return str(total)
	
	def get_md5(self, s):
		hl = hashlib.md5()
		hl.update(s.encode(encoding='utf-8'))
		return hl.hexdigest()
	
	def get_play_count(self, plid):  # 获取视频的播放量
		if plid is None:
			return '0'
		url = "https://count.vrs.sohu.com/count/queryext.action"
		querystring = {"plids": plid}
		retry = 10
		while 1:
			try:
				text = requests.get(url, params=querystring, proxies=self.GetProxies(), timeout=10).text
				p = re.compile('"total":(\d+?),')
				play_count = re.findall(p, text)[0]
				return play_count
			except:
				retry -= 1
				if retry == 0:
					return '0'
				else:
					continue
	
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
					print '图片保存失败！'
					return '0'
				else:
					continue
		with open(filename2, 'wb') as f:
			f.write(content)
		print '图片保存成功！'
		return '1'
	
	def get_score(self, pl_id):  # 获取电影评分
		if pl_id is None:
			return '0'
		url = 'http://vote.biz.itc.cn/query/score.json'
		querystring = {"albumId": pl_id}
		retry = 10
		while 1:
			try:
				text = requests.get(url, params=querystring, proxies=self.GetProxies(), timeout=10).json()
				try:
					score = str(text['score'])
				except:
					score = '0'
				return score
			except:
				retry -= 1
				if retry == 0:
					return '0'
				else:
					continue
	
	def get_t_movie(self, film_url, product_number, plat_number,table_name):  # 获取插入 t_movie 所需要的数据
		plid = self.get_pl_id(film_url)
		url = "http://pl.hd.sohu.com/videolist"
		querystring = {"playlistid": plid}
		retry = 5
		while 1:
			try:
				text = requests.get(url, params=querystring, proxies=self.GetProxies(), timeout=10).json()
				if 'directors' not in text:
					return None
				try:
					directors = ';'.join(text['directors'])
				except:
					directors = ''
				try:
					area = text['area']
				except:
					area = ''
				try:
					sets_number = str(text['size'])
				except:
					sets_number = '1'
				try:
					product_type = ';'.join(text['categories'])
				except:
					product_type = ''
				try:
					actors = ';'.join(text['actors'])
				except:
					actors = ''
				try:
					movie_desc = self.replace(text['albumDesc'])
				except:
					movie_desc = ''
				try:
					first_show_year_global = str(text['publishYear'])
				except:
					first_show_year_global = ''
				try:
					product_image = self.get_md5(product_number + plat_number)
					pic_url = text['largeVerPicUrl']
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
			except Exception as e:
				retry -= 1
				if retry == 0:
					print e
					return None
				else:
					continue
	
	def get_t_movie_summary(self, film_url, product_number, plat_number,table_name):  # 获取插入t_movie_summary 需要的数据
		plid = self.get_pl_id(film_url)
		retry = 5
		while 1:
			try:
				score = self.get_score(plid)
				play_num = self.get_play_count(plid)
				comment_num = self.get_commentsnum_total(plid)
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
				s.append([i[2], i[0], 'P05'])
	for j in s:
		print j[1],j[0]
		spider.get_t_movie(j[0], j[1], j[2], 'T_MOVIE')
		spider.get_t_movie_summary(j[0], j[1], j[2], 'T_MOVIE_SUMMARY')
	spider.db.db.close()

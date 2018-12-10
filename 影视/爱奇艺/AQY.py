# -*- coding: utf-8 -*-
# 此程序用来抓取爱奇艺的数据
import hashlib
import os

import requests
import time
import random
import re
from multiprocessing.dummy import Pool
import csv
import json
import sys
from fake_useragent import UserAgent, FakeUserAgentError
from  save_data import database


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
	
	def get_film_id(self, film_url):  # 获取film_id
		retry = 20
		while 1:
			try:
				headers = {
					'host': "www.iqiyi.com",
					'connection': "keep-alive",
					'cache-control': "no-cache",
					'upgrade-insecure-requests': "1",
					'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
					'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
					'accept-encoding': "gzip, deflate",
					'accept-language': "zh-CN,zh;q=0.9"
				}
				text = requests.get(film_url, headers=headers, proxies=self.GetProxies(), timeout=10).text
				p0 = re.compile('tvId: (\d+?),')
				p1 = re.compile('data-score-tvid="(\d+?)"')
				try:
					film_id = re.findall(p0, text)[0]
					return film_id
				except:
					film_id = re.findall(p1, text)[0]
					return film_id
			except:
				retry -= 1
				if retry == 0:
					return None
				else:
					continue
	
	def get_params(self, film_url):  # 获取请求参数
		retry = 5
		while 1:
			try:
				text = requests.get(film_url, proxies=self.GetProxies(), timeout=10).text
				p0 = re.compile('\[\'wallId\'\] = "(\d+?)"', re.S)
				p1 = re.compile('\[\'snsTime\'\] = (\d+?);', re.S)
				p2 = re.compile('\[\'feedId\'\] = (\d+?);', re.S)
				wallId = re.findall(p0, text)[0]
				snsTime = re.findall(p1, text)[0]
				feedId = re.findall(p2, text)[0]
				return wallId, snsTime, feedId
			except:
				retry -= 1
				if retry == 0:
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
	
	def get_score(self, film_id):  # 获取电影评分
		if film_id is None:
			return '0'
		url = 'http://pcw-api.iqiyi.com/video/score/getsnsscore?qipu_ids=%s' % film_id
		retry = 2
		while 1:
			try:
				text = requests.get(url, proxies=self.GetProxies(), timeout=10).json()
				score = str(text['data'][0]['sns_score'])
				return score
			except:
				retry -= 1
				if retry == 0:
					return '0'
				else:
					continue
	
	def get_play_num(self, film_id):  # 获取视频播放量
		if film_id is None:
			return '0'
		url = "http://iface2.iqiyi.com/views/3.0/player_tabs"
		querystring = {"api_v": "5.2", "app_k": "f0f6c3ee5709615310c0f053dc9c65f2", "app_v": "8.5.5", "app_gv": "",
		               "app_t": "0", "platform_id": "13", "dev_os": "11.2.1", "dev_ua": "iPad6,11",
		               "dev_hw": "{\"cpu\":\"\",\"mem\":\"1759\"}", "net_sts": "1", "scrn_sts": "2",
		               "scrn_res": "2048*1536", "scrn_dpi": "786432", "qyid": "B84C14D6-D286-444B-B938-EE99B4D51095",
		               "cupid_uid": "B84C14D6-D286-444B-B938-EE99B4D51095", "cupid_v": "3.11.004", "secure_p": "iPad",
		               "secure_v": "1", "lang": "zh_CN", "app_lm": "cn", "psp_vip": "0", "core": "1",
		               "req_sn": "1536414089510",
		               "net_ip": "{\"country\":\"中国\",\"province\":\"北京\",\"city\":\"北京\",\"cc\":\"电信\",\"area\":\"华北\",\"timeout\":0,\"respcode\":0}",
		               "service_order": "", "psp_status": "1",
		               "profile": "%7B%22group%22%3A%222%22%2C%22counter%22%3A2%7D", "gps": "39.66764,116.31381",
		               "album_id": film_id, "page_part": "2", "video_tab": "0", "pps": "0", "req_times": "1"}
		
		headers = {
			't': "847201068",
			'user-agent': "QIYIVideo/8.5.5 (iOS;com.qiyi.hd;iOS11.2.1;iPad6,11) Corejar",
			'sign': "69e1a73f703f16037652ed93278e413b",
			'accept-encoding': "gzip",
			'connection': "keep-alive",
			'cache-control': "no-cache",
			'postman-token': "726de67d-b7bb-25da-0e85-4fb2f6361f87"
		}
		retry = 2
		while 1:
			try:
				comment_num = '0'
				text = requests.get(url, headers=headers, params=querystring, proxies=self.GetProxies(), timeout=10).json()
				items = text['cards'][0]['items'][0]['meta']
				for item in items:
					content = item['text']
					if u'播放次数' in content:
						comment_num = content.replace(u'播放次数:', '').split()[0].replace(',', '')
						if u'万' in comment_num:
							comment_num = float(comment_num.replace(u'万', '')) * 10000
							comment_num = '%.0f' % comment_num
						if u'亿' in comment_num:
							comment_num = float(comment_num.replace(u'亿', '')) * 100000000
							comment_num = '%.0f' % comment_num
				return comment_num
			except:
				retry -= 1
				if retry == 0:
					return '0'
				else:
					continue
	
	def get_comments_num(self, videoid):  # 获取评论量
		if videoid is None:
			return '0'
		url = "https://api-t.iqiyi.com/qx_api/comment/get_video_comments"
		querystring = {"categoryid": "2", "need_subject": "true", "need_total": "1", "page": "1", "page_size": "20",
		               "sort": "hot", "tvid": videoid}
		retry = 5
		while 1:
			try:
				total = requests.get(url, params=querystring, proxies=self.GetProxies(), timeout=10).json()['data']['count']
				return str(total)
			except:
				retry -= 1
				if retry == 0:
					return '0'
				else:
					continue
	
	def get_t_movie(self, film_url, product_number, plat_number,table_name):
		headers = self.get_headers()
		headers['host'] = 'www.iqiyi.com'
		retry = 10
		while 1:
			try:
				text = requests.get(film_url, headers=headers,  proxies=self.GetProxies(), timeout=10).text
				if '<meta itemprop="name" content=' not in text:
					retry -= 1
					if retry == 0:
						return None
					else:
						continue
				try:
					p0 = re.compile(u'<em>导演：</em>(.*?)</p>', re.S)
					directors = self.replace(re.findall(p0, text)[0])
				except:
					directors = ''
				try:
					p1 = re.compile(u'<em>地区：</em>(.*?)</p>', re.S)
					area = self.replace(re.findall(p1, text)[0])
				except:
					area = ''
				try:
					p2 = re.compile(u'<i class="title-update-num">(\d+?)</i>集', re.S)
					sets_number = re.findall(p2, text)[0]
				except:
					sets_number = '1'
				try:
					p3 = re.compile(u'<em>类型：</em>(.*?)</p>', re.S)
					product_type = self.replace(re.findall(p3, text)[0]).replace(' ;', ';')
				except:
					product_type = ''
				try:
					p = re.compile(u'<\!-- 展开后 -->(.*?)data-moreorless="lessbtn">收起<span', re.S)
					t = re.findall(p, text)[0]
					p = re.compile(u'<p class="headImg-name"><a title="(.*?)"')
					t1 = re.findall(p, t)
					actors = ';'.join(t1)
				except:
					actors = ''
				try:
					p4 = re.compile(
						u'<div class="episodeIntro-brief" data-moreorless="moreinfo".*?<span class="briefIntroTxt">(.*?)</span>',
						re.S)
					movie_desc = self.replace(re.findall(p4, text)[0])
					movie_desc = re.sub(re.compile('\s{2,}'), ' ', movie_desc)
				except:
					try:
						p4 = re.compile(
							u'<div class="episodeIntro-brief" data-moreorless="lessinfo" itemprop="description">.*?<span class="briefIntroTxt">(.*?)</span>',
							re.S)
						movie_desc = self.replace(re.findall(p4, text)[0])
						movie_desc = re.sub(re.compile('\s{2,}'), ' ', movie_desc)
					except:
						try:
							p = re.compile(u'<span class="briefIntroTxt">(.*?)</span>', re.S)
							movie_desc = self.replace(re.findall(p, text)[0])
							movie_desc = re.sub(re.compile('\s{2,}'), ' ', movie_desc)
						except:
							movie_desc = ''
				try:
					p5 = re.compile(u'<em>全球首映：</em><span>            (\d{4})-', re.S)
					first_show_year_global = re.findall(p5, text)[0]
				except:
					first_show_year_global = ''
				try:
					product_image = self.get_md5(product_number + plat_number)
					p6 = re.compile(u'<div class="info-img">.*?<img.*?src="(.*?)"', re.S)
					pic_url = re.findall(p6, text)[0]
					if 'http' not in pic_url:
						pic_url = 'http:' + pic_url
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
		retry = 5
		while 1:
			try:
				headers = {
					'host': "www.iqiyi.com",
					'connection': "keep-alive",
					'cache-control': "no-cache",
					'upgrade-insecure-requests': "1",
					'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
					'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
					'accept-encoding': "gzip, deflate",
					'accept-language': "zh-CN,zh;q=0.9"
				}
				text = requests.get(film_url, headers=headers, proxies=self.GetProxies(), timeout=10).text
				p0 = re.compile('tvId: (\d+?),')
				p1 = re.compile('data-score-tvid="(\d+?)"')
				try:
					film_id = re.findall(p0, text)[0]
					print 'film_id:', film_id
				except:
					film_id = re.findall(p1, text)[0]
					print 'film_id:', film_id
				score = self.get_score(film_id)
				# play_num = self.get_play_num(film_id)
				play_num = '0'
				try:
					p0 = re.compile(u'<span class="feedLength">（(.*?)条）')
					comment_num = re.findall(p0, text)[0]
					if u'万' in comment_num:
						comment_num = float(comment_num.replace(u'万', '')) * 10000
						comment_num = '%.0f' % comment_num
					if u'亿' in comment_num:
						comment_num = float(comment_num.replace(u'亿', '')) * 100000000
						comment_num = '%.0f' % comment_num
				except:
					comment_num = self.get_comments_num(film_id)
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
					print '1',e
					return None
				else:
					continue


if __name__ == "__main__":
	spider = Spider()
	# spider.get_t_movie_summary('http://www.iqiyi.com/a_19rrgj9kvh.html', 'A0000002', 'P01', 'T_MOVIE_SUMMARY')
	s = []
	with open('new_data.csv') as f:
		tmp = csv.reader(f)
		for i in tmp:
			if 'http' in i[2]:
				s.append([i[2], i[0], 'P01'])
	for j in s:
		print j[1],j[0]
		spider.get_t_movie(j[0], j[1], j[2], 'T_MOVIE')
		spider.get_t_movie_summary(j[0], j[1], j[2], 'T_MOVIE_SUMMARY')
	spider.db.db.close()
	

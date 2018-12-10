# -*- coding: utf-8 -*-
# 此程序用来抓取腾讯视频的数据
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
		try:
			self.ua = UserAgent(use_cache_server=False).random
		except FakeUserAgentError:
			pass
		self.db = database()
	
	def get_headers(self):
		try:
			user_agent = self.ua.chrome
			headers = {'host': "video.coral.qq.com",
					   'connection': "keep-alive",
					   'user-agent': user_agent,
					   'accept': "*/*",
					   'referer': "http://v.qq.com/txyp/coralComment_yp_1.0.htm",
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
			headers = {'host': "video.coral.qq.com",
					   'connection': "keep-alive",
					   'user-agent': user_agent,
					   'accept': "*/*",
					   'referer': "http://v.qq.com/txyp/coralComment_yp_1.0.htm",
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
		replace1 = re.compile('\s{2,}')
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
		x = re.sub(replace1, ' ', x)
		x = re.sub('\n', ' ', x)
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
	
	def get_film_id(self, film_url):  # 获取电视剧每一集的id
		retry = 10
		while 1:
			try:
				text = requests.get(film_url, proxies=self.GetProxies(), timeout=10).text
				p0 = re.compile('itemprop="episode".*?<a href="http://v\.qq\.com/x/cover/.*?vid=(.*?)"', re.S)
				vids = []
				items = re.findall(p0, text)
				# print 'items:',items
				if len(items) == 0:
					p1 = re.compile('https://v\.qq\.com/detail/.*?/(.*?)\.')
					vid = re.findall(p1, film_url)[0]
					vids.append(vid)
					break
				else:
					vids.extend(items)
					break
			except:
				retry -= 1
				if retry == 0:
					return None
				else:
					continue
		pool = Pool(10)
		ss = pool.map(self.get_article_id, vids)
		pool.close()
		pool.join()
		videoids = filter(lambda x: x is not None, ss)
		return videoids
	
	def get_comments_num_video(self, comment_id):  # 获取某一个视频的总评论页数
		# print 'comment_id:',comment_id
		if comment_id is None:
			return 0
		else:
			headers = {
				'host': "coral.qq.com",
				'connection': "keep-alive",
				'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
				'accept': "*/*",
				'referer': "https://v.qq.com/txyp/coralComment_yp_1.0.htm",
				'accept-encoding': "gzip, deflate, br",
				'accept-language': "zh-CN,zh;q=0.9"
			}
			url = 'https://coral.qq.com/article/%s/commentnum' % comment_id
			retry = 5
			while 1:
				try:
					text = requests.get(url, headers=headers, proxies=self.GetProxies(), timeout=10).json()['data'][
						'commentnum']
					return int(text)
				except:
					retry -= 1
					if retry == 0:
						return 0
					else:
						continue
	
	def get_commentsnum_total(self, film_url):  # 获取某个视频的所有评论
		videoids = self.get_film_id(film_url)
		if videoids is None:
			return '0'
		print len(videoids)
		pool = Pool(10)
		items = pool.map(self.get_comments_num_video, videoids)
		pool.close()
		pool.join()
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
	
	def get_t_movie(self, film_url, product_number, plat_number, table_name):
		if 'cover' in film_url:
			pp = re.compile('cover/(.*?)\.html')
			film_id = re.findall(pp, film_url)[0]
			film_url = 'https://v.qq.com/detail/%s/%s.html' % (film_id[0], film_id)
		retry = 5
		while 1:
			try:
				text = requests.get(film_url, proxies=self.GetProxies(), timeout=10).text
				try:
					p0 = re.compile(u'<span class="director">导演</span>.*?_stat="info:actor_name">(.*?)</span>', re.S)
					directors = ';'.join(re.findall(p0, text))
				except:
					directors = ''
				try:
					p1 = re.compile(u'<span class="type_tit">地.*?<span class="type_txt">(.*?)</span>', re.S)
					area = re.findall(p1, text)[0]
				except:
					area = ''
				try:
					p2 = re.compile(u'总集数:</span>.*?<span class="type_txt">(.*?)</span>', re.S)
					sets_number = re.findall(p2, text)[0]
				except:
					sets_number = '1'
				try:
					p3 = re.compile(u'_stat="info\:tag">(.*?)</a>')
					product_type = ';'.join(re.findall(p3, text))
				except:
					product_type = ''
				try:
					if u'<span class="director">导演</span>' in text:
						p = re.compile(u'_stat="info:actor_name">(.*?)</span>')
						actors = ';'.join(re.findall(p, text)[1:])
					else:
						p = re.compile(u'_stat="info:actor_name">(.*?)</span>')
						actors = ';'.join(re.findall(p, text))
				except:
					actors = ''
				try:
					p4 = re.compile(u'<span class="txt _desc_txt_lineHight" itemprop="description">(.*?)</span>', re.S)
					movie_desc = re.findall(p4, text)[0]
				except:
					movie_desc = ''
				try:
					p5 = re.compile(u'出品时间:</span>.*?<span class="type_txt">(.*?)</span>', re.S)
					first_show_year_global = re.findall(p5, text)[0]
				except:
					try:
						p5 = re.compile(u'上映时间:</span>.*?type_txt">(.*?)-.*?</span>', re.S)
						first_show_year_global = re.findall(p5, text)[0]
					except:
						first_show_year_global = ''
				try:
					product_image = self.get_md5(product_number + plat_number)
					p6 = re.compile(u'vpic:  \'(.*?)\'')
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
			except Exception as e:
				retry -= 1
				if retry == 0:
					print e
					return None
				else:
					continue
	
	def get_t_movie_summary(self, film_url, product_number, plat_number, table_name):
		if 'cover' in film_url:
			pp = re.compile('cover/(.*?)\.html')
			film_id = re.findall(pp, film_url)[0]
			film_url = 'https://v.qq.com/detail/%s/%s.html' % (film_id[0], film_id)
		else:
			pp = re.compile('detail/.*?/(.*?)\.html')
			film_id = re.findall(pp, film_url)[0]
		retry = 5
		while 1:
			try:
				text = requests.get(film_url, proxies=self.GetProxies(), timeout=10).text
				try:
					p1 = re.compile(u'<div class="score_v"><span class="score">(.*?)</span>')
					score = re.findall(p1, text)[0]
				except:
					score = '0'
				comment_num = self.get_commentsnum_total(film_url)
				try:
					p2 = re.compile('_stat="series:numbtn".*?<a href="(.*?)"')
					play_num_url = re.findall(p2, text)[0]
				except:
					play_num_url = 'https://v.qq.com/x/cover/%s.html' % film_id
				play_num = str(self.get_playnum(play_num_url))
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
	
	def get_playnum(self, url):
		headers = {
			'host': "v.qq.com",
			'connection': "keep-alive",
			'cache-control': "no-cache",
			'upgrade-insecure-requests': "1",
			'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
			'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
			'accept-encoding': "gzip, deflate, br",
			'accept-language': "zh-CN,zh;q=0.9"
		}
		retry = 5
		while 1:
			try:
				text = requests.get(url, headers=headers, proxies=self.GetProxies(), timeout=10).content.decode('utf-8',
				                                                                                                'ignore')
				p0 = re.compile(u'"><em id="mod_cover_playnum" class="num">(.*?)</em>次专辑播放</span>')
				play_num = re.findall(p0, text)[0]
				if u'万' in play_num:
					play_num = float(play_num.replace(u'万', '')) * 10000
					play_num = '%.0f' % play_num
				if u'亿' in play_num:
					play_num = float(play_num.replace(u'亿', '')) * 100000000
					play_num = '%.0f' % play_num
				return play_num
			except:
				retry -= 1
				if retry == 0:
					return '0'
				else:
					continue
	
	def get_article_id(self, vid):
		url = "https://ncgi.video.qq.com/fcgi-bin/video_comment_id"
		querystring = {"otype": "json", "op": "3", "vid": vid, "cid": vid}
		retry = 5
		while 1:
			try:
				headers = self.get_headers()
				headers['host'] = 'ncgi.video.qq.com'
				text = requests.get(url, headers=headers, proxies=self.GetProxies(), params=querystring,
				                    timeout=10).text
				p0 = re.compile('"comment_id":"(\d+?)",')
				comment_id = re.findall(p0, text)[0]
				return comment_id
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
				s.append([i[2], i[0], 'P02'])
	for j in s:
		print j[1],j[0]
		spider.get_t_movie(j[0], j[1], j[2], 'T_MOVIE')
		spider.get_t_movie_summary(j[0], j[1], j[2], 'T_MOVIE_SUMMARY')
	spider.db.db.close()

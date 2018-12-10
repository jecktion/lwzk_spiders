# -*- coding: utf-8 -*-
# 此程序用来抓取 的数据
import hashlib
import os

import requests
import time
import random
import re
import csv
from PIL import Image
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
		# 将其余标签剔除
		removeExtraTag = re.compile('<.*?>', re.S)
		x = re.sub(removeExtraTag, "", x)
		x = re.sub(' / ', ';', x)
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
	
	def get_md5(self, s):
		hl = hashlib.md5()
		hl.update(s.encode(encoding='utf-8'))
		return hl.hexdigest()
	
	def webp2jpg(self, file_path):
		im = Image.open(file_path)
		if im.mode == "RGBA":
			im.load()  # required for png.split()
			background = Image.new("RGB", im.size, (255, 255, 255))
			background.paste(im, mask=im.split()[3])  # 3 is the alpha channel
			im = background
		im.save(file_path.replace('webp', 'jpg'), 'JPEG')
	
	def save_pic(self, pic_url, pic_name):  # 保存图片
		path = os.path.join(os.getcwd(), 'IMAGE')
		if not os.path.exists(path):
			os.mkdir(path)
		filename1 = '%s.webp' % pic_name
		filename2 = os.path.join(path, filename1.encode('gbk'))
		retry = 3
		while 1:
			try:
				s = requests.Session()
				content = s.get(pic_url, timeout=10).content
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
		self.webp2jpg(filename2)
		os.remove(filename2)
		print '图片保存成功！'
		return '1'
	
	def get_t_movie(self, film_url, product_number, plat_number, table_name):
		retry = 5
		while 1:
			try:
				headers = {
					'host': "movie.douban.com",
					'connection': "keep-alive",
					'cache-control': "no-cache",
					'upgrade-insecure-requests': "1",
					'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
					'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
					'accept-encoding': "gzip, deflate",
					'accept-language': "zh-CN,zh;q=0.9"
				}
				text = requests.get(film_url, headers=headers, proxies=self.GetProxies(), timeout=10).text
				try:
					p0 = re.compile(u'<span class=\'pl\'>导演</span>: (.*?)<br/>', re.S)
					directors = self.replace(re.findall(p0, text)[0])
				except:
					directors = ''
				try:
					p1 = re.compile(u'制片国家/地区:</span> (.*?)<br/>', re.S)
					area = self.replace(re.findall(p1, text)[0])
				except:
					area = ''
				try:
					p2 = re.compile(u'集数:</span> (\d+?)<br/>', re.S)
					sets_number = re.findall(p2, text)[0]
				except:
					sets_number = '1'
				try:
					p0 = re.compile(u'<span class="pl">类型:</span>(.*?)<br/>', re.S)
					product_type = self.replace(re.findall(p0, text)[0])
				except:
					product_type = ''
				try:
					p0 = re.compile(u'<span class=\'pl\'>主演</span>: (.*?)<br/>', re.S)
					actors = self.replace(re.findall(p0, text)[0])
				except:
					actors = ''
				try:
					p4 = re.compile(u'<span property="v:summary" class="">(.*?)</span', re.S)
					movie_desc = self.replace(re.findall(p4, text)[0])
					movie_desc = re.sub(re.compile('\s{2,}'), ' ', movie_desc)
				except:
					movie_desc = ''
				try:
					p = re.compile('<span class="year">\((\d+?)\)</span>')
					first_show_year_global = re.findall(p, text)[0]
				except:
					first_show_year_global = ''
				try:
					product_image = self.get_md5(product_number + plat_number)
					p6 = re.compile(u'<img class="media" src="(.*?)"')
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
	
	def get_xiangkan_num(self, film_url):  # 获取
		p = re.compile('subject/(\d+)')
		subject_id = re.findall(p, film_url)[0]
		url = 'https://movie.douban.com/subject/%s/comments?status=P' % subject_id
		retry = 5
		while 1:
			try:
				headers = self.get_headers()
				headers['host'] = 'movie.douban.com'
				text = requests.get(url, headers=headers, proxies=self.GetProxies(), timeout=10).text
				p0 = re.compile(u'<span>看过\((\d+?)\)</span>')
				kanguo_num = re.findall(p0, text)[0]
				p1 = re.compile(u'<a href="\?status=F">想看\((\d+?)\)</a>')
				xiangkan_num = re.findall(p1, text)[0]
				return kanguo_num, xiangkan_num
			except:
				retry -= 1
				if retry == 0:
					return '0', '0'
				else:
					continue
	
	def get_t_product_summary_douban(self, film_url, product_number, plat_number, table_name):
		retry = 5
		while 1:
			try:
				headers = {
					'host': "movie.douban.com",
					'connection': "keep-alive",
					'cache-control': "no-cache",
					'upgrade-insecure-requests': "1",
					'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
					'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
					'accept-encoding': "gzip, deflate",
					'accept-language': "zh-CN,zh;q=0.9"
				}
				text = requests.get(film_url, headers=headers, proxies=self.GetProxies(), timeout=10).text
				try:
					p0 = re.compile(u'property="v:average">([0-9\.]+?)</strong>', re.S)
					score = re.findall(p0, text)[0]
				except:
					score = '0'
				try:
					p1 = re.compile(u'<span property="v:votes">(\d+?)</span>人评价</a>', re.S)
					cmt_user_number = re.findall(p1, text)[0]
				except:
					cmt_user_number = '0'
				try:
					p = re.compile(u'<span class="rating_per">(.*?)\%</span>')
					star_5, star_4, star_3, star_2, star_1 = [str(float(x) / 100 * int(cmt_user_number)) for x in
					                                          re.findall(p, text)]
				except:
					star_5, star_4, star_3, star_2, star_1 = ['0', '0', '0', '0', '0']
				See_num = '0'
				Saw_num, Want_see_num = self.get_xiangkan_num(film_url)
				try:
					p2 = re.compile(u'去这部影片的讨论区（全部(\d+?)条）', re.S)
					discuss_number = re.findall(p2, text)[0]
				except:
					discuss_number = '0'
				try:
					p0 = re.compile(u'的短评</i>.*?全部 (\d+?) 条</a>', re.S)
					Short_cmt_num = re.findall(p0, text)[0]
				except:
					Short_cmt_num = '0'
				try:
					p0 = re.compile(u'<a href="reviews">全部 (\d+?) 条</a>', re.S)
					long_cmt_num = re.findall(p0, text)[0]
				except:
					long_cmt_num = '0'
				last_modify_date = self.p_time(time.time())
				tmp = [product_number, plat_number, score, cmt_user_number, star_1, star_2, star_3, star_4, star_5,
				       See_num, Saw_num, Want_see_num, discuss_number, Short_cmt_num, long_cmt_num, last_modify_date,
				       film_url]
				print '|'.join(tmp)
				result_dict = {'product_number': product_number,
				               'plat_number': plat_number,
				               'score': score,
				               'cmt_user_num': cmt_user_number,
				               'start_1_num': star_1,
				               'start_2_num': star_2,
				               'start_3_num': star_3,
				               'start_4_num': star_4,
				               'start_5_num': star_5,
				               'see_num': See_num,
				               'saw_num': Saw_num,
				               'want_see_num': Want_see_num,
				               'discuss_num': discuss_number,
				               'short_cmt_num': Short_cmt_num,
				               'long_cmt_num': long_cmt_num,
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
					print '请求出错！',e
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
				s.append([i[2], i[0], 'P09'])
	for j in s:
		print j[1],j[0]
		spider.get_t_movie(j[0], j[1], j[2], 'T_MOVIE')
		spider.get_t_product_summary_douban(j[0], j[1], j[2], 'T_PRODUCT_SUMMARY_DOUBAN')
	spider.db.db.close()

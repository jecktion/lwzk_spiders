# -*- coding: utf-8 -*-
# 此程序用来抓取 的数据
import hashlib
import os

import requests
import time
import random
import re
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
		x = re.sub(re.compile('[\n\r]'), '  ', x)
		x = re.sub(re.compile('\s{2,}'), '  ', x)
		x = re.sub('-', ';', x)
		x = re.sub('&nbsp;', '', x)
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
					print '图片保存失败！'
					return '0'
				else:
					continue
		with open(filename2, 'wb') as f:
			f.write(content)
		print '图片保存成功！'
		return '1'
	
	def get_comments_num(self, product_url):
		p = re.compile('(\d{5,})')
		ids = re.findall(p, product_url)[0]
		url = 'http://chuangshi.qq.com/novelcomment/index.html?bid=%s' % ids
		headers = self.get_headers()
		headers['host'] = 'chuangshi.qq.com'
		text = requests.get(url, headers=headers, proxies=self.GetProxies(), timeout=10).json()['data']['commentNum']
		return str(text)
	
	def get_md5(self, s):
		hl = hashlib.md5()
		hl.update(s.encode(encoding='utf-8'))
		return hl.hexdigest()
	
	def get_t_cartoon(self, product_url, product_number, plat_number, table_name):  # 获取T_CARTON
		p = re.compile('topic/(\d+)')
		film_id = re.findall(p, product_url)[0]
		url = "https://api.kkmh.com/v1/topics/%s" % film_id
		querystring = {"is_homepage": "0", "is_new_device": "false", "page_source": "9", "sort": "1", "sortAction": "1"}
		retry = 10
		headers = {
			'host': "api.kkmh.com",
			'package-id': "com.kuaikan.comic",
			'hw-model': "iPhone10,1",
			'accept-language': "zh-Hans-CN;q=1",
			'accept-encoding': "br, gzip, deflate",
			'accept': "*/*",
			'user-agent': "Kuaikan/5.12.0/512000(iPhone;iOS 11.4;Scale/2.00;WiFi;1334*750)",
			'connection': "keep-alive",
			'lower-flow': "No"
		}
		while 1:
			try:
				text = requests.get(url, headers=headers, params=querystring, proxies=self.GetProxies(), timeout=10).json()['data']
				# print text
				break
			except:
				retry -= 1
				if retry == 0:
					return None
				else:
					continue
		try:
			authors = []
			t = text['related_authors']
			for item in t:
				authors.append(item['nickname'])
			author = ';'.join(authors)
		except:
			author = ''
		try:
			tags = ';'.join(text['category'])
		except:
			tags = ''
		try:
			cartoon_desc = self.replace(text['description'])
		except:
			cartoon_desc = ''
		if u'独家' in cartoon_desc:
			Signed = u'独家'
		else:
			Signed = ''
		try:
			product_image = self.get_md5(product_number + plat_number)
			pic_url = text['cover_image_url'].replace('http://f2.kkmh.com', 'https://i1s.kkmh.com') + '.jpg'
			self.save_pic(pic_url, product_image)
		except:
			product_image = self.get_md5(product_number + plat_number)
		last_modify_date = self.p_time(time.time())
		src_url = product_url
		results = [product_number, plat_number, author, tags, Signed, cartoon_desc, product_image,
		           last_modify_date, src_url]
		print '|'.join(results)
		'''
		with open('data_t_cartoon.csv', 'a') as f:
			writer = csv.writer(f, lineterminator='\n')
			writer.writerow([x.encode('gbk', 'ignore') for x in results])
		'''
		result_dict = {'product_number': product_number,
		               'plat_number': plat_number,
		               'author': author,
		               'tags': tags,
		               'sign_type': Signed,
		               'cartoon_desc': cartoon_desc,
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
	
	def huajian(self, play_num):
		if u'万' in play_num:
			play_num = float(play_num.replace(u'万', '')) * 10000
			play_num = '%.0f' % play_num
		if u'亿' in play_num:
			play_num = float(play_num.replace(u'亿', '')) * 100000000
			play_num = '%.0f' % play_num
		return play_num
	
	def get_t_cartoon_summary(self, product_url, product_number, plat_number, table_name):  # 获取t_carton_summary
		p = re.compile('topic/(\d+)')
		film_id = re.findall(p, product_url)[0]
		url = "https://api.kkmh.com/v1/topics/%s" % film_id
		querystring = {"is_homepage": "0", "is_new_device": "false", "page_source": "9", "sort": "1", "sortAction": "1"}
		retry = 10
		headers = {
			'host': "api.kkmh.com",
			'package-id': "com.kuaikan.comic",
			'hw-model': "iPhone10,1",
			'accept-language': "zh-Hans-CN;q=1",
			'accept-encoding': "br, gzip, deflate",
			'accept': "*/*",
			'user-agent': "Kuaikan/5.12.0/512000(iPhone;iOS 11.4;Scale/2.00;WiFi;1334*750)",
			'connection': "keep-alive",
			'lower-flow': "No"
		}
		while 1:
			try:
				text = requests.get(url, headers=headers, params=querystring, proxies=self.GetProxies(), timeout=10).json()['data']
				break
			except:
				retry -= 1
				if retry == 0:
					return None
				else:
					continue
		t = text['comics']
		Chapter_num_update = '0'
		update_date = ''
		for i in t[::-1]:
			last_title = i['title']
			p_title = re.compile(u'第(\d+?)话')
			try:
				Chapter_num_update = re.findall(p_title, last_title)[0]
				update_date = self.p_time(t[-1]['created_at'])
				break
			except:
				continue
		try:
			click_num = str(text['view_count'])
		except:
			click_num = '0'
		try:
			comment_num = str(text['comments_count'])
		except:
			comment_num = '0'
		score = '0'
		collect_num = '0'
		ticket_this_week = '0'
		ticket_total = '0'
		reward_num = '0'
		last_modify_date = self.p_time(time.time())
		src_url = product_url
		results = [product_number, plat_number, Chapter_num_update, update_date, click_num, comment_num,
		           collect_num, score, ticket_this_week, ticket_total, reward_num, last_modify_date, src_url]
		print '|'.join(results)
		'''
		with open('data_t_cartoon_summary.csv', 'a') as f:
			writer = csv.writer(f, lineterminator='\n')
			writer.writerow([x.encode('gbk', 'ignore') for x in results])
		'''
		result_dict = {'product_number': product_number,
		               'plat_number': plat_number,
		               'chapter_num_update': Chapter_num_update,
		               'update_date': update_date.split()[0],
		               'click_num': click_num,
		               'comment_num': comment_num,
		               'collect_num': collect_num,
		               'score': score,
		               'ticked_this_week': ticket_this_week,
		               'ticket_total': ticket_total,
		               'reward_num': reward_num,
		               'last_modify_date': last_modify_date,
		               'src_url': src_url
		               }
		tmp = self.db.up_data(table_name, result_dict)
		if tmp:
			print u'%s 写入 %s 成功' % (product_number, table_name)
		else:
			print u'%s 写入 %s 失败' % (product_number, table_name)
		return None


if __name__ == "__main__":
	spider = Spider()
	s = []
	with open('data.csv') as f:
		tmp = csv.reader(f)
		for i in tmp:
			if 'http' in i[2]:
				s.append([i[0], i[2]])
	sss = []
	for j in s:
		print j[0],j[1]
		try:
			spider.get_t_cartoon(j[1], j[0], 'P11', 'T_CARTOON')  # 基本信息表
			spider.get_t_cartoon_summary(j[1], j[0], 'P11', 'T_CARTOON_SUMMARY')  # 周期表
		except:
			continue
	spider.db.db.close()

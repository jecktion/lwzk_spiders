# -*- coding: utf-8 -*-
# 此程序用来抓取 的数据
import hashlib
import os

import requests
import time
import random
import re
import csv
import json
from  save_data import database


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
		return proxies
	
	def get_qq_page_1(self, product_number, plat_number, game_id):  # 获取新版的数据
		print product_number
		page = 0
		while True:
			print page
			url = 'https://itunes.apple.com/WebObjects/MZStore.woa/wa/userReviewsRow?cc=cn&id=' + game_id + '&displayable-kind=11&startIndex=' + str(
				10000 * page) + '&endIndex=' + str(10000 * (page + 1)) + '&sort=0&appVersion=all'
			headers = {
				'User-Agent': 'iTunes/11.0 (Windows; Microsoft Windows 7 Business Edition Service Pack 1 (Build 7601)) AppleWebKit/536.27.1',
			}
			results = []
			retry = 3
			while 1:
				try:
					text = requests.get(url, headers=headers, proxies=self.GetProxies(), timeout=100).text
					# print text
					items = json.loads(text, strict=False)['userReviewList']
					print len(items)
					break
				except:
					retry -= 1
					if retry == 0:
						with open('error.txt', 'a') as f:
							f.write('|'.join([x.encode('gbk') for x in [product_number, plat_number, game_id]]))
						return None
					else:
						continue
			end = False
			s1 = 0
			last_modify_date = self.p_time(time.time())
			for item in items:
				try:
					rate = str(item['rating'])
				except:
					rate = ''
				comments = item['body'].replace('=', '')
				nick_name = item['name'].replace('=', '')
				cmt_time = item['date'].replace('T', ' ').replace('Z', '')
				cmt_date = cmt_time.split()[0]
				date = cmt_date
				like_cnt = '0'
				cmt_reply_cnt = '0'
				long_comment = '0'
				src_url = 'https://itunes.apple.com/WebObjects/MZStore.woa/wa/userReviewsRow'
				# print date
				if date[:4] in ['2018', '2017', '2016', '2015', '2014', '2013', '2012', '2011', '2010']:
					s1 = date
				tmp = [product_number, plat_number, nick_name, cmt_date, cmt_time, comments, like_cnt,
				       cmt_reply_cnt, long_comment, last_modify_date, src_url, rate]
				# if date[:4] in ['2018', '2017', '2016', '2015', '2014', '2013', '2012', '2011', '2010']:
				# 	results.append([x.encode('gbk', 'ignore') for x in tmp])
				# if date[:4] == '2009':
				# 	end = True
				# 	break
			print s1
			if s1 == 0:
				return None
			with open('data_app_store.csv', 'a') as f:
				writer = csv.writer(f, lineterminator='\n')
				writer.writerows(results)
			if end:
				return None
			else:
				page += 1
	
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
	
	def get_t_game(self, game_id, product_number, plat_number, table_name):  # 获取t_game
		retry = 5
		while 1:
			try:
				url = "http://itunes.apple.com/lookup"
				querystring = {"id": game_id, "cc": "cn"}
				headers = {
					'User-Agent': 'iTunes/11.0 (Windows; Microsoft Windows 7 Business Edition Service Pack 1 (Build 7601)) AppleWebKit/536.27.1',
				}
				text = requests.get(url, headers=headers, params=querystring, proxies=self.GetProxies(), timeout=10).json()['results'][0]
				try:
					category = text['genres']
					category = ';'.join(category)
				except:
					category = ''
				os_game = 'iOS'
				try:
					dev_company = text['sellerName']
				except:
					dev_company = ''
				try:
					publish_company = dev_company
				except:
					publish_company = ''
				try:
					first_show_year_global = text['releaseDate'].split('-')[0]
				except:
					first_show_year_global = ''
				try:
					game_desc = self.replace(text['description'])
				except:
					game_desc = ''
				try:
					product_image = self.get_md5(product_number + plat_number)
					pic_url = text['artworkUrl512']
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
				src_url = url
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
	
	def get_t_game_summary(self, game_id, product_number, plat_number, table_name):
		retry = 5
		while 1:
			try:
				url = "http://itunes.apple.com/lookup"
				querystring = {"id": game_id, "cc": "cn"}
				headers = {
					'User-Agent': 'iTunes/11.0 (Windows; Microsoft Windows 7 Business Edition Service Pack 1 (Build 7601)) AppleWebKit/536.27.1',
				}
				text = requests.get(url, headers=headers, params=querystring, proxies=self.GetProxies(), timeout=10).json()['results'][0]
				# print text
				user_num = '0'
				title_num = '0'
				try:
					score = str(text['averageUserRating'])
				except:
					score = '0'
				comment_people_num = '0'
				try:
					comment_num = str(text['userRatingCount'])
				except:
					comment_num = '0'
				good_comment_num = '0'
				bad_comment_num = '0'
				played_num = '0'
				want_play_num = '0'
				Install_num = '0'
				last_modify_date = self.p_time(time.time())
				src_url = url
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
	with open('new_data.csv') as f:
		tmp = csv.reader(f)
		for i in tmp:
			if 'ID' not in i[2] and len(i[2]) > 0:
				s1.append([i[2], i[0], 'P25'])
	for j in s1:
		print j[1],j[0]
		spider.get_t_game(j[0], j[1], j[2], 'T_GAME')
		spider.get_t_game_summary(j[0], j[1], j[2], 'T_GAME_SUMMARY')
	spider.db.db.close()

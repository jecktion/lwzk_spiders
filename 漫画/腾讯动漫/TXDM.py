# -*- coding: utf-8 -*-
# 此程序用来抓取 的数据
import hashlib
import os

import requests
import time
import datetime
import re
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
		headers = {'accept': "*/*",
		           'accept-encoding': "gzip, deflate",
		           'accept-language': "zh-CN,zh;q=0.9",
		           'cache-control': "no-cache",
		           'connection': "keep-alive",
		           'host': "ac.qq.com",
		           'pragma': "no-cache",
		           'referer': "http://ac.qq.com/Comic/comicInfo/id/536658",
		           'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
		           'x-requested-with': "XMLHttpRequest"}
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
		x = re.sub(re.compile('\s{3,}'), " ", x)
		x = re.sub(re.compile('[\n\r]'), " ", x)
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
	
	def get_md5(self, s):
		hl = hashlib.md5()
		hl.update(s.encode(encoding='utf-8'))
		return hl.hexdigest()
	
	def get_t_cartoon(self, product_url, product_number, plat_number, table_name):  # 获取T_CARTON
		retry = 10
		while 1:
			try:
				t = requests.get(product_url, proxies=self.GetProxies(), timeout=10).content.decode('utf-8', 'ignore')
				break
			except:
				retry -= 1
				if retry == 0:
					return None
		p0 = re.compile(u'作者：<em style="max-width: 168px;">(.*?)&nbsp;')
		try:
			author = re.findall(p0, t)[0].strip()
		except:
			author = ''
		try:
			p1 = re.compile(u'的标签：(.*?)" />')
			tags = re.findall(p1, t)[0].replace(',', ';')
		except:
			tags = ''
		Signeds = []
		if u'sign">签约</i>' in t:
			Signeds.append(u'签约')
		if u'>独家</i>' in t:
			Signeds.append(u'独家')
		Signed = ';'.join(Signeds)
		try:
			p = re.compile(u'<p class="works-intro-short ui-text-gray9">(.*?)</p>', re.S)
			cartoon_desc = self.replace(''.join(re.findall(p, t)))
		except:
			cartoon_desc = ''
		try:
			p3 = re.compile('<div class="works-cover ui-left">.*?<img src="(.*?)"', re.S)
			product_image = self.get_md5(product_number + plat_number)
			pic_url = ''.join(re.findall(p3, t))
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
	
	def get_comments_nums(self, product_url):  # 获取评论数
		p = re.compile('/id/(\d+)')
		book_id = ''.join(re.findall(p, product_url))
		url = 'http://ac.qq.com/Community/topicList?targetId=%s&page=2&_=1535292008985' % book_id
		headers = {
			'host': "ac.qq.com",
			'connection': "keep-alive",
			'accept': "*/*",
			'x-requested-with': "XMLHttpRequest",
			'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
			'referer': "http://ac.qq.com/Comic/ComicInfo/id/621912",
			'accept-encoding': "gzip, deflate",
			'accept-language': "zh-CN,zh;q=0.9"
		}
		retry = 5
		while 1:
			try:
				text = requests.get(url, proxies=self.GetProxies(), timeout=10, headers=headers).text
				try:
					p = re.compile(u'<em class="commen-ft-ts">(\d+?)</em> 条话题</span>')
					comments_num = re.findall(p, text)[0]
				except:
					p = re.compile(u'<em class="commen-ft-ts">(\d+?)</em> 条话题</span>')
					comments_num = ''.join(re.findall(p, text))
				return comments_num
			except Exception as e:
				retry -= 1
				if retry == 0:
					print '1',e
					return '0'
				else:
					continue
	
	def huajian(self, play_num):
		if u'万' in play_num:
			play_num = float(play_num.replace(u'万', '')) * 10000
			play_num = '%.0f' % play_num
		if u'亿' in play_num:
			play_num = float(play_num.replace(u'亿', '')) * 100000000
			play_num = '%.0f' % play_num
		return play_num
	
	def get_week_ticket(self, product_url):  # 获取周月票
		p = re.compile('id/(\d+)')
		item_id = ''.join(re.findall(p, product_url))
		url = 'http://ac.qq.com/Comic/getMonthTicketInfo/id/%s?_=1536807722093' % item_id
		retry = 5
		while 1:
			try:
				headers = {'host': "ac.qq.com",
				           'connection': "keep-alive",
				           'accept': "application/json, text/javascript, */*; q=0.01",
				           'x-requested-with': "XMLHttpRequest",
				           'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
				           'referer': "http://ac.qq.com/Comic/comicInfo/id/531490",
				           'accept-encoding': "gzip, deflate",
				           'accept-language': "zh-CN,zh;q=0.9"}
				text = requests.get(url, proxies=self.GetProxies(), headers=headers, timeout=10).json()
				# print 'text:',text
				if text:
					week_ticket = str(text['monthTicket']['mtNum']).replace(',', '')
				else:
					week_ticket = '0'
				print 'week_ticket:', week_ticket
				return week_ticket
			except Exception as e:
				retry -= 1
				if retry == 0:
					print '2',e
					return '0'
				else:
					continue
	
	def get_reward(self, product_url):  # 获取打赏数
		p = re.compile('id/(\d+)')
		item_id = ''.join(re.findall(p, product_url))
		url = 'http://ac.qq.com/Comic/getAwardInfo/id/%s?_=1536807722106' % item_id
		print url
		retry = 5
		while 1:
			try:
				headers = {'host': "ac.qq.com",
						   'connection': "keep-alive",
						   'accept': "application/json, text/javascript, */*; q=0.01",
						   'x-requested-with': "XMLHttpRequest",
						   'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
						   'referer': "http://ac.qq.com/Comic/comicInfo/id/531490",
						   'accept-encoding': "gzip, deflate",
						   'accept-language': "zh-CN,zh;q=0.9"}
				text = requests.get(url,  headers=headers, proxies=self.GetProxies(), timeout=10).json()
				# print 'text:',text
				if 'count' in text:
					reward_num = str(text['count']).replace(',', '')
				else:
					reward_num = '0'
				return reward_num
			except Exception as e:
				retry -= 1
				if retry == 0:
					print '3',e
					return '0'
				else:
					continue
	
	def get_update(self, product_url):  # 获取更新章节，以及更新时间
		p = re.compile('id/(\d+)')
		item_id = ''.join(re.findall(p, product_url))
		url = 'http://m.ac.qq.com/comic/index/id/%s?trace_id=910_111.15.86.255_1536808772' % item_id
		# print 'url:',url
		retry = 5
		while 1:
			try:
				text = requests.get(url, proxies=self.GetProxies(), timeout=10).text
				
				results = []
				p1 = re.compile(u'更新到(.*?)话')
				p2 = re.compile('class="comicList-info-time">(.*?)</span>')
				for p in [p1, p2]:
					try:
						results.append(''.join(re.findall(p, text)))
					except:
						results.append('')
				# print '|'.join(results)
				return results
			except Exception as e:
				retry -= 1
				if retry == 0:
					print '4',e
					return '0', ''
				else:
					continue
	
	def get_t_cartoon_summary(self, product_url, product_number, plat_number, table_name):  # 获取t_carton_summary
		retry = 10
		while 1:
			try:
				t = requests.get(product_url, proxies=self.GetProxies(), timeout=10).content.decode('utf-8', 'ignore')
				break
			except:
				retry -= 1
				if retry == 0:
					return None
		Chapter_num_update, update_date = self.get_update(product_url)
		update_date = ''.join(re.findall(r'[\d+]{4}-[\d+]{2}-[\d+]{2}', update_date))
		if not Chapter_num_update:
			Chapter_num_update = '0'
		if not update_date:
			update_date = datetime.datetime.now().strftime('%Y-%m-%d')
		# print 'Chapter_num_update:', Chapter_num_update
		# print 'update_date:', update_date
		try:
			p = re.compile(u'<span>人气：<em>(.*?)</em></span>', re.S)
			click_num = ''.join(re.findall(p, t))
			if click_num:
				click_num = self.huajian(click_num)
			else:
				click_num = '0'
		except:
			click_num = '0'
		try:
			comment_num = self.get_comments_nums(product_url)
			if not comment_num:
				comment_num = '0'
		except:
			comment_num = '0'
		# print 'comment_num:', comment_num
		try:
			p = re.compile(u'评分：<strong class="ui-text-orange">(.*?)</strong>')
			score = ''.join(re.findall(p, t))
			if not score:
				score = '0'
		except:
			score = '0'
		try:
			p = re.compile(u'<span>收藏数：<em id="coll_count">(\d+?)</em></span>')
			collect_num = ''.join(re.findall(p, t))
			if not collect_num:
				collect_num = '0'

		except:
			collect_num = '0'
		try:
			ticket_this_week = self.get_week_ticket(product_url)
		except:
			ticket_this_week = '0'
		ticket_total = '0'
		try:
			reward_num = self.get_reward(product_url)
		except:
			reward_num = '0'
		last_modify_date = self.p_time(time.time())
		src_url = product_url
		results = [product_number, plat_number, Chapter_num_update, update_date, click_num, comment_num,
		           collect_num, score, ticket_this_week, ticket_total, reward_num, last_modify_date, src_url]
		print '|'.join(results)
		# '''
		# with open('data_t_cartoon_summary.csv', 'a') as f:
		# 	writer = csv.writer(f, lineterminator='\n')
		# 	writer.writerow([x.encode('gbk', 'ignore') for x in results])
		# '''
		result_dict = {'product_number': product_number,
		               'plat_number': plat_number,
		               'chapter_num_update': Chapter_num_update,
		               'update_date': update_date,
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
		print 'tmp:',tmp
		if tmp:
			print u'%s 写入 %s 成功' % (product_number, table_name)
		else:
			print u'%s 写入 %s 失败' % (product_number, table_name)
		return None


if __name__ == "__main__":
	spider = Spider()
	# spider.get_t_cartoon_summary('https://manhua.163.com/source/5232441787740344351', 'D0000299', 'P12', 'T_CARTOON_SUMMARY')
	ss = []
	with open('data.csv') as f:
		tmp = csv.reader(f)
		for i in tmp:
			if 'http' in i[2]:
				ss.append([i[2], i[0], 'P12'])
	for s in ss:
		print s[1],s[0]
		spider.get_t_cartoon(s[0], s[1], s[2], 'T_CARTOON')
		spider.get_t_cartoon_summary(s[0], s[1], s[2], 'T_CARTOON_SUMMARY')
	spider.db.db.close()

# -*- coding: utf-8 -*-
# 此程序用来抓取 的数据
import hashlib
import os

import requests
import time
import re
import csv
from fake_useragent import UserAgent,FakeUserAgentError
from save_data import database


class Spider(object):
	def __init__(self):
		self.db = database()
		try:
			self.ua = UserAgent(use_cache_server=False).random
		except FakeUserAgentError:
			pass
	
	def get_headers(self):
		headers = {'Host': 'www.u17.com',
				   'Connection': 'keep-alive',
		           'User-Agent': self.ua.chrome,
		           'Referer': 'http://www.u17.com/comic/16179.html',
		           'Accept': '*/*',
		           'Accept-Encoding': 'gzip, deflate',
		           'Accept-Language': 'zh-CN,zh;q=0.9'
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
	
	def get_comments_num(self, product_url):  # 获取评论数目
		p = re.compile('(\d{5,})')
		ids = re.findall(p, product_url)[0]
		url = 'http://chuangshi.qq.com/novelcomment/index.html?bid=%s' % ids
		headers = self.get_headers()
		headers['host'] = 'chuangshi.qq.com'
		text = requests.get(url, proxies=self.GetProxies(), headers=headers, timeout=10).json()['data']['commentNum']
		return str(text)
	
	def get_md5(self, s):
		hl = hashlib.md5()
		hl.update(s.encode(encoding='utf-8'))
		return hl.hexdigest()
	
	def get_t_cartoon(self, product_url, product_number, plat_number, table_name):  # 获取T_CARTON
		retry = 10
		while 1:
			try:
				t = requests.get(product_url,proxies=self.GetProxies(), timeout=10).content.decode('utf-8', 'ignore')
				break
			except:
				retry -= 1
				if retry == 0:
					return None
		p0 = re.compile(u'target="_blank" class="name">(.*?)</a>')
		try:
			author = re.findall(p0, t)[0].strip()
		except:
			author = ''
		p1 = re.compile(u'class="class_tag">(.*?)</a>')
		tmp1 = re.findall(p1, t)
		if len(tmp1) == 0:
			p1 = re.compile('<a href="javascript:;"  class="zhenhunjie_tag.*?>(.*?)</a>', re.S)
			tags = ';'.join([self.replace(x) for x in re.findall(p1, t)])
		else:
			tags = ';'.join(tmp1)
		Signeds = []
		if u'title="签约作者"' in t:
			Signeds.append(u'签约')
		if u'title="有妖气独家' in t:
			Signeds.append(u'独家')
		Signed = ';'.join(Signeds)
		try:
			p = re.compile(u'<p class="words" id="words">(.*?)<a', re.S)
			cartoon_desc = self.replace(re.findall(p, t)[0])
		except:
			cartoon_desc = ''
		try:
			p3 = re.compile('id="cover">.*?<img src="(.*?)"', re.S)
			product_image = self.get_md5(product_number + plat_number)
			pic_url = re.findall(p3, t)[0]
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
		retry = 10
		while 1:
			try:
				t = requests.get(product_url, proxies=self.GetProxies(), timeout=10).content.decode('utf-8', 'ignore')
				break
			except:
				retry -= 1
				if retry == 0:
					return None
		try:
			p = re.compile(u'总章节：<em>(\d+?)</em>')
			Chapter_num_update = re.findall(p, t)[0]
		except:
			Chapter_num_update = '0'
		try:
			p = re.compile(u'<span>最后更新时间：(.*?)</span>')
			update_date = re.findall(p, t)[0]
		except:
			update_date = ''
		try:
			p = re.compile(u'总点击：<span class="color_red">(.*?)</span>', re.S)
			click_num = re.findall(p, t)[0]
			click_num = self.huajian(click_num)
		except:
			click_num = '0'
		try:
			p = re.compile(u'总评论：<em>(\d+?)</em>')
			comment_num = re.findall(p, t)[0]
		except:
			comment_num = '0'
		score = '0'
		try:
			p = re.compile(u'总收藏：<em>(\d+?)</em>')
			collect_num = re.findall(p, t)[0]
		except:
			collect_num = '0'
		ticket_this_week = '0'
		try:
			p = re.compile(u'<span>总月票：<em>(\d+?)</em>')
			ticket_total = re.findall(p, t)[0]
		except:
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
	ss = []
	with open('data.csv') as f:
		tmp = csv.reader(f)
		for i in tmp:
			if 'http' in i[2]:
				ss.append([i[2], i[0], 'P13'])
	for s in ss:
		print s[1],s[0]
		spider.get_t_cartoon(s[0], s[1], s[2], 'T_CARTOON')  # 基本信息表
		spider.get_t_cartoon_summary(s[0], s[1], s[2], 'T_CARTOON_SUMMARY')  # 周期表
	spider.db.db.close()

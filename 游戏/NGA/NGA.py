# -*- coding: utf-8 -*-
# 此程序用来抓取 的数据
import hashlib
import os

import requests
import time
import random
import re
from save_data import database
import csv
from selenium import webdriver


class Spider(object):
	def __init__(self):
		self.ss = []
		self.db = database()
		self.cookie = 'UM_distinctid=166861498561c3-07ac53b19e1937-7513384e-1fa400-1668614985783f; taihe=b52daf4edbfb158c70724137010c93e0; guestJs=1540973330; CNZZDATA30043604=cnzz_eid%3D1583360308-1539842675-%26ntime%3D1540969179; CNZZDATA30039253=cnzz_eid%3D361766501-1539846334-%26ntime%3D1540969773; Hm_lvt_5adc78329e14807f050ce131992ae69b=1539847791,1540973332; PHPSESSID=13tnq3uvgm1at00tfpu4figdi3; ngacn0comUserInfo=jockcharles%09jockcharles%0939%0939%09%0910%092889%094%090%090%0939_60; ngacn0comUserInfoCheck=31d147f250ef9f1b6dd70a86e7cea444; ngacn0comInfoCheckTime=1540974093; ngaPassportUid=1448405; ngaPassportUrlencodedUname=jockcharles; ngaPassportCid=be6bb78e2011b74e1560bd07d322abfd08143423; lastpath=/read.php?tid=12063608&rand=769; taihe_session=82b05adfa170b9a18ebceb2fa43aba60; lastvisit=1540974109; bbsmisccookies=%7B%22insad_refreshid%22%3A%7B0%3A%22/154043559919813%22%2C1%3A1541578131%7D%2C%22pv_count_for_insad%22%3A%7B0%3A-45%2C1%3A1541005302%7D%2C%22insad_views%22%3A%7B0%3A1%2C1%3A1541005302%7D%7D; Hm_lpvt_5adc78329e14807f050ce131992ae69b=1540974111'
	
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
		headers = {'host': "bbs.nga.cn",
		           'connection': "keep-alive",
		           'cache-control': "no-cache",
		           'upgrade-insecure-requests': "1",
		           'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
		           'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
		           'referer': "http://bbs.ngacn.cc/misc/adpage_insert_2.html?http://bbs.ngacn.cc/read.php?tid=13427591&page=2",
		           'accept-encoding': "gzip, deflate",
		           'accept-language': "zh-CN,zh;q=0.9",
		          'cookie': self.cookie
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
		replace1 = re.compile(' {2,}')
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
		x = re.sub(replace1, '', x)
		x = re.sub('\n', '', x)
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
	
	def get_detail_page(self, game_id, game_url, product_number, plat_number, page):  # 获取游戏某一页的所有评论
		url = 'http://bbs.ngacn.cc/read.php?tid=%s&page=%d' % (game_id, page)
		retry = 5
		while 1:
			try:
				results = []
				text = requests.get(url, headers=self.get_headers(), proxies=self.GetProxies(), timeout=10).content.decode('gbk', 'ignore')
				p0 = re.compile(
					"<a href='nuke\.php\?func=ucp&uid=(\d+?)'.*?title='reply time'>(.*?)</span>.*?<span id='postcontent\d+?' class='postcontent ubbcode'>(.*?)</span>",
					re.S)
				items = re.findall(p0, text)
				last_modify_date = self.p_time(time.time())
				for item in items:
					nick_name = item[0]
					cmt_date = item[1].split()[0]
					cmt_time = item[1] + ':00'
					comments = item[2]
					like_cnt = '0'
					cmt_reply_cnt = '0'
					long_comment = '0'
					src_url = game_url
					tmp = [product_number, plat_number, nick_name, cmt_date, cmt_time, comments, like_cnt,
					       cmt_reply_cnt, long_comment, last_modify_date, src_url]
					print '|'.join(tmp)
					ee = [nick_name, cmt_date, cmt_time, comments]
					if '|'.join(ee) in self.ss:
						return None
					else:
						self.ss.append('|'.join(ee))
						results.append([x.encode('gbk', 'ignore') for x in tmp])
				return results
			except:
				retry -= 1
				if retry == 0:
					return None
				else:
					continue
	
	def get_all(self, game_url, product_number, plat_number):  # 获取所有评论
		p0 = re.compile('tid=(\d+)')
		game_id = re.findall(p0, game_url)[0]
		page = 1
		while 1:
			print page
			t = self.get_detail_page(game_id, game_url, product_number, plat_number, page)
			if t is None:
				return None
			else:
				with open('data_nga.csv', 'a') as f:
					writer = csv.writer(f, lineterminator='\n')
					writer.writerows(t)
				page += 1
	
	def get_pagenums(self, game_id):  # 获取总页数
		url = 'http://bbs.nga.cn/read.php?tid=%s&page=1' % game_id
		retry = 2
		while 1:
			try:
				text = requests.get(url,headers=self.get_headers(),proxies=self.GetProxies(), timeout=10).content.decode('gbk', 'ignore')
				p = re.compile('var __PAGE = \{0:\'/read\.php\?tid=\d+?\',\d+?:(\d+?),')
				pagenums = re.findall(p, text)[0]
				return pagenums
			except:
				retry -= 1
				if retry == 0:
					return 1
				else:
					continue
	
	def get_id(self, game_id, page):  # 获取某一页的最后一个楼层数
		url = 'http://bbs.nga.cn/read.php?tid=%s&page=%s' % (game_id, page)
		retry = 5
		while 1:
			try:
				text = requests.get(url,headers=self.get_headers(), proxies=self.GetProxies(), timeout=10).content.decode('gbk', 'ignore')
				# print text
				p = re.compile('<tr id=\'post1strow(\d+?)\'')
				last_id = re.findall(p, text)[-1]
				return last_id
			except Exception as e:
				retry -= 1
				if retry == 0:
					print '获取某一页的最后一个楼层数失败！',e
					return '0'
				else:
					continue
	
	def get_title_num(self, product_url):  # 获取title_num
		p0 = re.compile('tid=(\d+)')
		game_id = re.findall(p0, product_url)[0]
		pagenums = self.get_pagenums(game_id)
		return self.get_id(game_id,pagenums)
		
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
	
	def get_t_game(self, game_url, product_number, plat_number,table_name):  # 获取t_game
		p0 = re.compile('tid=(\d+)')
		game_id = re.findall(p0, game_url)[0]
		url = 'http://bbs.nga.cn/read.php?tid=%s&page=1' % game_id
		# print 'url:',url
		retry = 5
		while 1:
			try:
				text = requests.get(url, headers=self.get_headers(), proxies=self.GetProxies(), timeout=10).content.decode('gbk', 'ignore')
				# print text
				try:
					p = re.compile(u'\[comment game_type\](.*?)\[/comment game_type\]', re.S)
					category = ';'.join(re.findall(p, text)[0].split())
					print 'category:', category
				except:
					category = ''
				os_game = 'iOS;Android'
				try:
					p = re.compile(u'\[comment game_devloper\](.*?)\[/comment game_devloper\]', re.S)
					dev_company = ';'.join(re.findall(p, text))
				except:
					dev_company = ''
				try:
					p = re.compile(u'\[comment game_publisher\](.*?)\[/comment game_publisher\]', re.S)
					publish_company = ';'.join(re.findall(p, text))
				except:
					publish_company = ''
				try:
					p = re.compile('iOS \[symbol link\]\[/style\]\[/url\] (\d{4}-\d{2}-\d{2}) \[stripbr\]')
					first_show_year_global = re.findall(p, text)[0]
				except:
					try:
						p = re.compile('Android \[symbol link\]\[/style\]\[/url\] (\d{4}-\d{2}-\d{2}) \[stripbr\]')
						first_show_year_global = re.findall(p, text)[0]
					except:
						first_show_year_global = ''
				game_desc = ''
				try:
					product_image = self.get_md5(product_number + plat_number)
					p = re.compile(r'\[comment game_title_image\]\[.*? src \.(.*?)\]\[\/style\]', re.I|re.S)
					# p = re.compile(r'\[comment game_title_image\]\[style border-radius 0\.3 width 50  src \.(.*)\]\[/style\]', re.S)
					pic_url = re.findall(p, text)[0]
					print 'pic_url 1:',pic_url
					pic_url = 'http://img.nga.178.com/attachments' + pic_url
					self.save_pic(pic_url, product_image)
				except:
					print '重新保存图片！'
					product_image = self.get_md5(product_number + plat_number)
					p = re.compile(r'\[td rowspan=2\]\[align=center\]\[img\]\.(.*?)\[\/img\]\[\/align\]\[\/td\]', re.I | re.S)
					pic_url = re.findall(p, text)[0]
					print 'pic_url 2:', pic_url
					pic_url = 'http://img.nga.178.com/attachments' + pic_url
					self.save_pic(pic_url, product_image)

				last_modify_date = self.p_time(time.time())
				src_url = game_url
				tmp = [product_number, plat_number, category, os_game, dev_company, publish_company,
				       first_show_year_global, game_desc, product_image, last_modify_date, src_url]
				print '|'.join(tmp)
				result_dict = {'product_number': product_number,
				               'plat_number': plat_number,
				               'category': category,
				               'os': os_game,
				               'dev_company': dev_company,
				               'publish_company': publish_company,
				               'first_show_year_global': first_show_year_global.split('-')[0],
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
	
	def get_t_game_summary(self, game_url, product_number, plat_number,table_name):
		retry = 5
		while 1:
			try:
				chrome_options = webdriver.ChromeOptions()
				chrome_options.add_argument('--headless')
				# chrome_options.add_argument('--no-sandbox')
				# chrome_options.add_argument('--disable-dev-shm-usage')
				driver = webdriver.Chrome(chrome_options=chrome_options,
				                          executable_path=os.path.join(os.getcwd(), 'C:\Users\Administrator\AppData\Local\Google\Chrome\Application\chromedriver.exe'))
				driver.get(game_url)
				time.sleep(random.randint(5,10))
				text = driver.page_source
				user_num = '0'
				title_num = self.get_title_num(game_url)
				p1 = re.compile(u'评分</td><td><b>(.*?)分', re.S)
				try:
					score = re.findall(p1, text)[0]
				except:
					score = '0'
				try:
					p = re.compile(u'共计(\d+?)人评分')
					comment_people_num = re.findall(p, text)[0]
				except:
					comment_people_num = '0'
				comment_num = '0'
				good_comment_num = '0'
				bad_comment_num = '0'
				played_num = '0'
				want_play_num = '0'
				Install_num = '0'
				last_modify_date = self.p_time(time.time())
				src_url = game_url
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
			except Exception as e:
				retry -= 1
				if retry == 0:
					print u'请求周期表数据出错', e
					driver.quit()
					return None
				else:
					continue


if __name__ == "__main__":
	spider = Spider()
	s1 = []
	with open('data.csv') as f:
		tmp = csv.reader(f)
		for i in tmp:
			if 'http' in i[2]:
				s1.append([i[2], i[0], 'P23'])
	for j in s1:
		print j[1],j[0]
		spider.get_t_game(j[0], j[1], j[2], 'T_GAME')
		spider.get_t_game_summary(j[0], j[1], j[2], 'T_GAME_SUMMARY')
	spider.db.db.close()

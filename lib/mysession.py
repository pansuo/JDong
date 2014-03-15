# coding:utf-8

import requests
import random


class MySession(requests.Session):
	"""A Requests session. @lite"""

	useragents = [
		'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1b2pre) Gecko/20081015 Fennec/1.0a1',
		'Mozilla/5.0 (X11; U; Linux armv7l; en-US; rv:1.9.2a1pre) Gecko/20090322 Fennec/1.0b2pre',
		'Mozilla/5.0 (Android; Linux armv7l; rv:9.0) Gecko/20111216 Firefox/9.0 Fennec/9.0',
		'Mozilla/5.0 (Android; Mobile; rv:12.0) Gecko/12.0 Firefox/12.0',
		'Mozilla/5.0 (Android; Mobile; rv:14.0) Gecko/14.0 Firefox/14.0',
		'Mozilla/5.0 (Mobile; rv:14.0) Gecko/14.0 Firefox/14.0',
		'Mozilla/5.0 (Mobile; rv:17.0) Gecko/17.0 Firefox/17.0',
		'Mozilla/5.0 (Tablet; rv:18.1) Gecko/18.1 Firefox/18.1',
		'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Mobile/10A5376e',
		'UCWEB7.0.0.33/27/999',
		'UCWEB7.0.1.33/27/999'
	]

	def __init__(self):
		requests.Session.__init__(self)
		self.encoding = 'utf-8'
		self.verify = False
		self.timeout = 5

		randIP = str(random.randint(58, 61)) + '.' + str(random.randint(10, 200)) + '.' + str(random.randint(10, 200)) + '.' + str(random.randint(10, 200))
		self.headers = {
			'User-Agent': random.choice(self.useragents),
			'X-Forwarded-For': randIP
		}

# coding:utf-8
import sys
import os
import time
import string
import random
import pickle
import Queue
import json
import requests
import threading
import logging
from pyquery import PyQuery
from lib.dama import Dama
from lib.mysession import MySession
from config import config


class JDongW():
	FLAG_DAMA = False
	event_start_code = threading.Event()
	event_start_buy = threading.Event()

	"""京东www站"""
	def __init__(self, username=None, password=None):
		self.s = MySession()
		self.dm = Dama()
		self.username = username
		self.password = password
		self.uuid = ''
		self.msg = ''		# res

	def __setSession(self):
		"""保存会话"""
		with file('session/www/' + self.username + '.session', 'w') as f:
			pickle.dump(self.s, f)
		return True

	def __getSession(self):
		"""恢复会话"""
		if not os.path.exists('session/www/' + self.username):
			return False

		with file('session/www/' + self.username + '.session') as f:
			self.s = pickle.load(f)

		try:
			r = self.s.get('http://order.jd.com/center/list.action')
		except:
			logging.debug('%s' % r)
			return False
		if r.url.find('list.action') < 0:
			return False
		else:
			return True

	def reg(self):
		"""自动注册"""
		self.username = config['reg']['name_prx'] + ''.join(random.sample(string.digits, config['reg']['name_len']))
		self.password = ''.join(random.sample(string.letters + string.digits, int(config['reg']['password']))) if config['reg']['password'].isdigit() else config['reg']['password']
		self.s = MySession()

		try:
			r = self.s.get('https://reg.jd.com/reg/person')
			d = PyQuery(r.text)
			r = self.s.get('https://reg.jd.com/validate/isPinEngaged?pin=' + self.username + '&r=' + str(time.time()))
		except:
			print "[error][reg]" + self.username
			return False
		code_url = d('.item-ifo img').attr('onclick')
		code_url = 'http:' + code_url[code_url.find("+") + 2:code_url.find("'+")] + str(int(time.time()))
		try:
			vcode = self.dm.recv_byte(self.s.get(code_url).content)
			if not vcode:
				raise
		except:
			print "[info][reg]get vcode failed " + self.username
			return False

		last_input = d('input[type=hidden]')[-1]
		data = {
			'regType': 'person',
			'schoolid': '',
			'mobileCode': '',
			'uuid': d('input#uuid').val(),
			'regName': self.username,
			'pwd': self.password,
			'pwdRepeat': self.password,
			'authcode': vcode,
			last_input.name: last_input.value
		}
		r = self.s.post('https://reg.jd.com/reg/regService?r=' + str(time.time()), data=data)
		if r.content.find('info') > -1:
			return False
		else:
			confirm_url = r.content[r.content.find('http'):r.content.find('"}')]
			r = self.s.get(confirm_url)
			with file('res/users.txt', 'a') as f:
				f.write(self.username + "---" + self.password + '\r\n')

			self.__setSession()
			return True

	def login(self, retries=2):
		if not retries:
			return False
		if self.__getSession():
			print "[info][login] use session file"
			return True

		# 登录
		r = ''
		d = ''
		while True:
			try:
				r = self.s.get('http://passport.jd.com/uc/login?ltype=logout')
				d = PyQuery(r.text)
				if not d('#uuid').val():
					logging.debug(r.text)
					print '[error][login]loadpage'
					raise
				else:
					break
			except:
				time.sleep(2)
				continue

		inputs = d('input[type="hidden"]')
		self.uuid = d('#uuid').val()

		# 构建参数
		data = {
			'uuid': self.uuid,
			'loginname': self.username,
			'nloginpwd': self.password,
			'loginpwd': self.password,
			'authcode': '',
			'chkRememberMe': 'on',
			inputs[-1].name: inputs[-1].value,
		}
		vcode = ''
		if d('#o-authcode').attr('class').find('hide') < 0:
			code_url = d('#JD_Verification1').attr('src')
			if code_url.find('authcode.jd.com') < 0:
				print "[info][login] vcode url error"
				return False
			# 识别验证码
			while True:
				try:
					vcode = self.dm.recv_byte(self.s.get(code_url).content)
					if not vcode or len(vcode) != 4:
						raise
					else:
						break
				except:
					print "[info][login]vcode error " + self.username
					pass

			data['authcode'] = vcode

		time.sleep(2)
		r = self.s.post('http://passport.jd.com/uc/loginService?uuid=' + self.uuid + '&r=' + str(time.time()), data)
		if r.content.find('success') > 0:
			self.__setSession()
			return True
		else:
			print "[info][login] login failed " + self.username
			return False

	""" # @todo: 失效
	def yushou(self, url, item, retries=2):
		if not retries:
			return False

		# 生成随机key
		vkey = ''.join(random.sample(string.ascii_letters + string.digits, 20))
		r = self.s.get(url)
		d = PyQuery(r.text)
		code_url_index = r.text.find('http://captcha.jd.com/verify/image?srcid=yushou&is=')
		code_url = r.text[code_url_index:code_url_index + 89] + vkey

		# 识别验证码
		vcode = ''
		while True:
			try:
				vcode = self.dm.recv_byte(self.s.get(code_url).content)
				if not vcode or len(vcode) != 4:
					print "[info][yushou] vcode error"
					raise
				else:
					break
			except:
				pass

		# 提交请求
		r = self.s.post('http://yushou.jd.com/insideInvite/verifyCodeValidate.action?vkey=' + vkey + "&vvalue=" + vcode)
		if r.json()[u'pass_mark']:
			data = {
				'vvalue': vcode,
				'vkey': vkey,
				'sku': url[url.find('sku=') + 4:url.find('&key')],
				'key': url[url.find('key=') + 4:],
			}
			r = self.s.post('http://yushou.jd.com/yuyue.action', data=data)
			with file("res/yuyue/" + item + '.txt', 'a') as f:
				f.write(self.username + "---" + self.password + '\n')
			return True
		else:
			return self.yushou(url, item, retries - 1)
	"""


# test
if __name__ == "__main__":
	logging.basicConfig(filename='info.log', format=u'[%(asctime)s][%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)', level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')
	""" # to rm
	print sys.argv
	users = []
	for line in file('config/now.user.txt'):
		if line.find('---') > 0:
			user = line.strip().split('---')
			users.append(user)
	users = users[int(sys.argv[2]):int(sys.argv[3])]

	# users = [['tiancheng02', 'tian1991']]
	queue = Queue.Queue()
	for i in users:
		queue.put(i)

	# 设置worker
	JDongW.FLAG_DAMA = True
	Worker.queue = queue

	for i in range(int(sys.argv[1])):
		time.sleep(5)
		Worker('Thread ' + str(i))

	time.sleep(my_sleep(18))
	JDongW.event_start_code.set()
	time.sleep(my_sleep(3))
	JDongW.event_start_buy.set()

	# 等待任务结束
	Worker.queue.join()
	print "\n#all task end#"
	"""

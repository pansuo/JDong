# coding:utf-8
from ctypes import *
import requests
import json
import random
import binascii
from config import config

class Dama2():
	"""打码兔打码."""
	_username = ''
	_password = ''
	__attrs__ = ['DM', 'username', 'password', 'softuuid', 'timeout']

	def __init__(self):
		self.DM = WinDLL('lib/CrackCaptchaAPI.dll')
		if not self._username:
			Dama2._username = config['dama']['dama2']['username']
			Dama2._password = config['dama']['dama2']['password']
		self.username = c_char_p(self._username)
		self.password = c_char_p(self._password)
		self.softuuid = c_char_p('6fbc06efdc777eee854842572102daec')
		self.timeout = c_ushort(30)

	def recv_byte(self, imgdata, imgtype=42):
		# imgdata = c_void_p(imgdata)
		imgleng = c_uint(len(imgdata))
		imgtype = c_ulong(imgtype)
		res = c_char_p('')

		code = self.DM.D2Buf(self.softuuid, self.username, self.password, imgdata, imgleng, self.timeout, imgtype, res)
		if code > 0:
			return res.value
		return False

	def report_err(self, imgid):
		return False


class Chaoren():
	_username = ''
	_password = ''
	__attrs__ = ['DM', 'username', 'password', 'softuuid', 'timeout']

	def __init__(self):
		if not self._username:
			Chaoren._username = config['dama']['chaoren']['username']
			Chaoren._password = config['dama']['chaoren']['password']

		self.s = requests.Session()
		self.s.encoding = 'utf-8'
		self.s.timeout = 16
		self.data = {
			'username': self.username,
			'password': self.password,
			'softid': '4140',
			'imgid': '',
			'imgdata': ''
		}

	def get_left_point(self):
		try:
			r = self.s.post('http://apib.sz789.net:88/GetUserInfo.ashx', self.data)
			return r.json()
		except requests.ConnectionError:
			return self.get_left_point()
		except:
			return False

	def recv_byte(self, imgdata):
		self.data['imgdata'] = binascii.b2a_hex(imgdata).upper()
		try:
			r = self.s.post('http://apib.sz789.net:88/RecvByte.ashx', self.data)
			res = r.json()
			if res[u'info'] == -1:
				self.report_err(res[u'imgid'])		# 识别错误
				return False

			return r.json()[u'result']
		except requests.ConnectionError:
			return self.recv_byte(imgdata)
		except:
			return False

	def report_err(self, imgid):
		self.data['imgid'] = imgid
		if self.data['imgdata']:
			del self.data['imgdata']
		try:
			r = self.s.post('http://apib.sz789.net:88/ReportError.ashx', self.data)
			return r.json()
		except requests.ConnectionError:
			return self.report_err(imgid)
		except:
			return False


class Dama():
	flag = 'dama2'

	def __init__(self):
		if self.flag == 'dama2':
			self.w = Dama2()
		elif self.flag == 'chaoren':
			self.w = Chaoren()
		else:
			self.w = Dama2()		# 默认

	def recv_byte(self, imgdata):
		return self.w.recv_byte(imgdata)

	def report_err(self, imgid):
		return self.w.report_err(imgid)


# test
if __name__ == '__main__':
	pass

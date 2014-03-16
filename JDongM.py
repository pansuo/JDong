# coding:utf-8
import os
import time
import json
import random
import requests
import threading
import Queue
import pickle
import logging
from pyquery import PyQuery
from lib.mysession import MySession
from lib.dama import Dama


class JDongM():
	"""jdong触屏版"""
	item = '1056969'

	def __init__(self, username, password, address=None):
		self.s = ''
		self.sid_val = ''			# 会话ID
		self.sid_all = ''			# 会话ID GET参数
		self.username = username
		self.password = password
		self.address = address
		self.address_id = ''		# 地址uuid
		self.date = time.strftime('%Y-%m-%d', time.localtime(time.time()))

	def __setSession(self):
		"""保存会话"""
		with file('session/wap/' + self.username + '.session', 'w') as f:
			pickle.dump(self.s, f)
		return True

	def __getSession(self):
		"""恢复会话"""
		if not os.path.exists('session/wap/' + self.username):
			return False

		with file('session/wap/' + self.username + '.session') as f:
			self.s = pickle.load(f)

		# 校验会话是否过期,若有效,设置sid
		r = self.s.get('https://passport.m.jd.com/user/home.action')
		if r.url.find('home.action') < 0:
			return False
		else:
			d = PyQuery(r.text)
			url = d('.new-a-message').attr('href')
			self.sid_all = url[url.find('sid='):]
			self.sid_val = self.sid_all[4:]
			return True

	def login(self, retries=3):
		logging.info('login start')
		if not retries:
			return False

		# 尝试恢复会话
		if self.__getSession():
			logging.info(self.username + u' restore success')
			return True

		# 重新登录
		logging.info(self.username + u' try login')
		self.s = MySession()
		try:
			r = self.s.get('https://passport.m.jd.com/user/doLogin.action?v=t')
		except:
			return self.login(retries - 1)

		# 配置查询参数
		d = PyQuery(r.text)
		sid_all = d('form').attr('action')
		self.sid_all = sid_all[sid_all.find('sid'):]
		self.sid_val = self.sid_all[4:]
		data = {
			'returnurl': 'http://m.jd.com/user/home.action?' + self.sid_all,
			'username': self.username,
			'password': self.password,
			'remember': True
		}

		# 登录需要验证码
		vcode_flag = d('input#codeLevel').val()
		if vcode_flag:
			self.dm = Dama()
			vcode_url = d('.new-abtn-code #code').attr('src')
			vcode_val = ''
			while True:
				try:
					vcode_val = self.dm.recv_byte(self.s.get('https://passport.m.jd.com' + imgurl).content())
					if not vcode_val or len(vcode_val) != 4:
						raise
					else:
						break
				except:
					logging.debug('error vcode' + vcode_val)
					continue
			data['validateCode'] = vcode_val
			data['codeKey'] = self.sid_val,
			data['codeLevel'] = d('input#codeLevel').val()

		# 登录
		try:
			r = self.s.post('https://passport.m.jd.com/user/doLogin.action?' + self.sid_all, data)
			if r.url.find('home.action') < 0:
				if self.debug:
					print "[JDongM][login][9]login failed"
				raise
		except:
			logging.debug(r'login error, returned \n %s' % r.text)
			return self.login(retries - 1)

		self.__setSession()
		logging.info(self.username + ' login success')
		return True

	def setAddress(self, retries=3):
		if not retries:
			return False

		# 删除已存在地址
		try:
			r = self.s.get('http://m.jd.com/address/addressList.action?' + self.sid_all)
			d = PyQuery(r.text)
			addressid = d('.new-addr-btn a:eq(1)').attr('addressid')
			if addressid:
				r = self.s.get('http://m.jd.com/address/doDelete.json?addressId=' + addressid)
				return self.setAddress(retries)
		except:
			logging.debug('del address error : %s' % (r.text))
			return self.setAddress(retries - 1)

		# 添加地址
		try:
			r = self.s.post('http://m.jd.com/address/doAdd.action', data=self.address)
			d = PyQuery(r.text)
			self.addressid = d('.new-addr-btn a:eq(1)').attr('addressid')
			if not self.addressid:
				raise
		except:
			logging.debug('not find addressid %s' % (r.text))
			return self.setAddress(retries - 1)

		return True

	def checkOrder(self, retries=3):
		if not retries:
			return False

		try:
			r = self.s.get('http://m.jd.com/user/unfinishedOrder.action?' + self.sid_all)
		except:
			return self.checkOrder(retries - 1)
		d = PyQuery(r.text)
		order_url = d('#div_orders a')
		if not order_url.size():
			return False
		# 有订单
		try:
			r = self.s.get('http://m.jd.com/' + order_url[0].attrib['href'])
		except:
			return self.checkOrder(retries - 1)

		try:
			d = PyQuery(r.text)
			order_id = d('input[type=hidden]')[0].value
			order_status = d('.new-txt-rd2:eq(0)').html().encode('utf-8')
			order_price = d('.new-mu_l2cw span:eq(1)').html().encode('utf-8')
			order_user = d('.new-order-details li:eq(2)').find('.new-txt').html().encode('utf-8')
			with file('res/' + str(self.date) + '.txt', 'a') as f:
				f.write(self.username + ' - ' + order_id + ' - ' + order_status + ' - ' + order_user + '\n')
		except:
			logging.debug('check_order error %s' % (r.text))
			pass

		return True

	def clearCart(self):
		"""清空购物车"""
		r = self.s.get('http://m.jd.com/cart/cart.action')
		d = PyQuery(r.text)
		items = d('.cart-list .common-input')
		if not items.size():
			return True
		for dom in items:
			item_id = d(dom).attr('id').replace('num', '')
			item_num = d(dom).attr('value')
			if not item_id or not item_num:
				return False
			self.s.get('http://m.jd.com/cart/remove.action?wareId=' + item_id + '&num=' + item_num + '&ran=' + str(time.time()))

		return True

	def checkCart(self):
		"""检查购物车是否有商品, 购买前检测"""
		try:
			r = self.s.get('http://m.jd.com/cart/cart.action')
		except:
			return self.checkCart()
		d = PyQuery(r.text)
		items = d('.cart-list .common-input')
		if not items.size():
			return False
		else:
			return True

	def add2cart(self):
		"""添加到购物车"""
		try:
			url = 'http://m.jd.com/cart/add.json?wareId=' + self.item + '&' + self.sid_all
			r = self.s.get(url)
			return True
		except:
			return False

	def setOrder(self):
		"""设置订单信息"""
		try:
			r = self.s.get('http://m.jd.com/order/order.action?enterOrder=true')
			r = self.s.get('http://m.jd.com/order/address.action?' + self.sid_all)
			r = self.s.post('http://m.jd.com/order/updateOrderAddressTouch.action?' + self.sid_all, data={'vtuanOrder': 'false', 'addressId': self.addressid})
			r = self.s.get('http://m.jd.com/order/paytype.action?' + self.sid_all)
			r = self.s.post('http://m.jd.com/order/updatePaytype.action?' + self.sid_all, data={'idPaymentType': '1'})
			r = self.s.get('http://m.jd.com/order/shipment.action?' + self.sid_all)
			data = {
				'order.idShipmentType': '65',
				'order.codTime': '3',
				'order.isCodInform': 'false',
				'order.paymentWay': '1'
			}
			r = self.s.post('http://m.jd.com/order/updateShipment.action?' + self.sid_all, data=data)
			if r.text.find('images/html5/t_confirm.png') > 0:
				raise
		except:
			return False

		return True

	""" 旧,待更新
	def buy(self):
		data = {
			'order.idShipmentType': '65',
			'order.idInvoiceHeaderType': '4',
			'order.idInvoiceContentsType': '1',
			'order.remark': '',
			'order.idInvoiceType': '1'
		}
		try:
			print "-",
			r = self.s.post('http://m.jd.com/order/submit.action?' + self.sid_all, data=data)
			if r.text.find('pay-tip') > 0:
				print "+",
				return True
			else:
				return False
		except:
			return False
	"""


if __name__ == '__main__':
	logging.basicConfig(filename='info.log', format=u'[%(asctime)s][%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)', level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')
	w = JDongM('tiancheng02', 'tian1991')
	if not w.login():
		print "login error"
	elif not w.clearCart():
		print "clearCart error"
	elif not w.add2cart():
		print 'add2cart error'

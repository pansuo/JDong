# coding:utf-8
import sys
import os
import time
import json
import random
import Queue
import logging
import threading
from JDongM import JDongM
from JDongW import JDongW


class Worker(threading.Thread):
	action = 'set'
	lock = threading.Lock()			# with lock
	event = threading.Event()		# self.event.wait()
	queue = None					# task

	def __init__(self, threadName):
		threading.Thread.__init__(self)
		self.daemon = True
		self.workername = threadName
		self.start()

	def run(self):
		while True:
			if not self.queue or self.queue.empty():
				print "[thread][end]" + self.workername
				break
			user = self.queue.get()
			self.username = user[0]
			self.password = user[1]
			self.jd = JDongM(self.username, self.password)

			if self.action == 'set':
				self.orderSet()
			elif self.action == 'buy':
				self.orderBuy()
			elif self.action == 'check':
				self.orderCheck()
			else:
				print "[thread][end]error action"
			self.queue.task_done()

		pass

	def orderSet(self):
		"""设置订单地址并添加商品到购物车"""
		name1 = [u'罗', u'梁', u'宋', u'唐', u'许', u'韩', u'冯', u'邓', u'曹', u'彭', u'曾', u'肖', u'田', u'董', u'袁', u'潘', u'于', u'蒋', u'蔡', u'余', u'杜', u'叶', u'姚', u'卢', u'姜', u'崔', u'钟', u'谭', u'陆', u'汪', u'范', u'金', u'石', u'廖', u'贾']
		name2 = [u'秀', u'娟', u'英', u'华', u'慧', u'巧', u'美', u'娜', u'静', u'淑', u'惠', u'珠', u'翠', u'芝', u'玉', u'萍', u'红', u'娥', u'玲', u'芬', u'芳', u'燕', u'彩', u'春', u'菊', u'兰', u'洁', u'梅', u'琳', u'素', u'云', u'莲', u'真', u'环', u'雪', u'荣', u'爱', u'妹', u'霞', u'月', u'莺', u'媛', u'艳', u'瑞', u'凡', u'佳', u'嘉', u'琼', u'勤', u'珍', u'贞', u'莉', u'娣', u'叶', u'璧', u'璐', u'娅', u'琦', u'晶', u'妍', u'茜', u'秋', u'珊', u'莎', u'锦', u'青', u'倩', u'婷', u'姣', u'婉', u'娴', u'瑾', u'颖', u'露', u'瑶', u'怡', u'婵', u'雁', u'纨', u'仪', u'荷', u'丹', u'蓉', u'眉', u'君', u'琴', u'蕊', u'薇', u'菁', u'梦', u'岚', u'筠', u'柔', u'竹', u'霭', u'凝', u'晓', u'欢', u'霄', u'枫', u'芸', u'菲', u'寒', u'欣', u'滢', u'伊', u'亚', u'宜', u'可', u'姬', u'舒', u'影', u'荔', u'枝', u'思', u'丽', u'秀', u'飘', u'育', u'馥', u'琦', u'晶', u'妍', u'茜', u'秋', u'珊', u'莎', u'锦', u'黛', u'青', u'倩', u'婷', u'宁', u'蓓', u'纨', u'苑', u'婕', u'馨', u'瑗', u'琰', u'韵', u'融', u'园', u'艺', u'咏', u'卿', u'聪', u'澜', u'纯', u'毓', u'悦', u'昭', u'冰', u'爽', u'琬', u'茗', u'羽']
		name = random.choice(name1) + random.choice(name2)

		# 地址, id值在京东上能找到
		# @todo, 把字典抓一份到本地
		address = [
			{
				'address.id': 0,
				'address.name': u'王' + name,
				'address.mobile': '1526223' + str(random.randint(1000, 9999)),
				'address.idProvince': '1',
				'address.idCity': '2805',
				'address.idArea': '2854',
				'address.where': u'这什么地方的地址',
			},
			{
				'address.id': 0,
				'address.name': u'林' + name,
				'address.mobile': '1526223' + str(random.randint(1000, 9999)),
				'address.idProvince': '19',
				'address.idCity': '1607',
				'address.idArea': '3639',
				'address.idTown': '47389',
				'address.where': u'另一个地址',
			},
		]
		self.jd.address = address[random.randint(0, len(address) - 1)]		# 随机选个地址
		if self.__orderSet():
			print "[succ]" + self.username
		else:
			print "[erro]" + self.username

	def orderCheck(self):
		"""检查是否存在未完成订单"""
		if not self.jd.login():
			return self.__taskFailed()
		if self.jd.checkOrder():
			print "[success]" + self.username
			self.queue.task_done()
			return True

	def __orderSet(self):
		"""更新订单信息"""
		if not self.jd.login():
			print 'logined'
			return self.__taskFailed()

		if not self.jd.setAddress():
			print 'setaddress succ'
			return self.__taskFailed()

		if not self.jd.clearCart():
			print 'clearcart'
			return self.__taskFailed()
		if not self.jd.add2cart():
			print 'add cart'
			return self.__taskFailed()

		if not self.jd.setOrder():
			print 'set order'
			return self.__taskFailed()

		return True

	def __taskFailed(self):
		"""任务失败,标记任务结束"""
		return False

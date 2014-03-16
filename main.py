# coding:utf-8
import sys
import os
import time
import json
import random
import Queue
import logging
from JDongW import JDongW
from worker import Worker


def reg():
	"""京东注册"""
	w = JDongW()
	while True:
		w.reg()
	pass


def set_address(thread_num, queue):
	"""添加购物车 & 改收货地址"""
	Worker.action = 'set'
	Worker.queue = queue

	for i in range(int(thread_num)):
		time.sleep(3)
		Worker('Thread ' + str(i))

	Worker.queue.join()
	print "\n#all task end#"


if __name__ == '__main__':
	logging.basicConfig(filename='info.log', format=u'[%(asctime)s][%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)', level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')
	print sys.argv
	# init
	if len(sys.argv) <= 1:
		# action : ['reg', 'set', 'buy']
		print u'使用方法\n console下 python main.py action thread_num, task_from, task_to' \
			+ u'\naction 		: 可选值为 reg, set, buy;' \
			+ u'\nthread_num 	: 为线程数,加购物车改地址一般3-5个就够了' \
			+ u'\ntask_from, task_to: res/users.txt 列表里从第几个开始,到第几个'
	elif sys.argv[1] == 'reg':
		reg()		# 注册
	else:
		# 取任务
		users = [line.strip().split('---') for line in file('res/users.txt') if line.find('---') > 0]
		sys.argv[3] = (len(users) - 1) if int(sys.argv[3]) > len(users) else int(sys.argv[3])
		sys.argv[4] = len(users) if int(sys.argv[4]) > len(users) else int(sys.argv[4])
		users = users[int(sys.argv[3]):int(sys.argv[4])]
		# users = [['tiancheng02', 'tian1991']]
		queue = Queue.Queue()
		for i in users:
			queue.put(i)

		if sys.argv[1] == 'set':
			set_address(sys.argv[2], queue)
		elif sys.argv[1] == 'buy':
			pass

# coding:utf-8
import sys
import os
import time
import json
import random
import Queue
from JDongW import JDongW


def reg():
	"""京东注册"""
	w = JDongW()
	while True:
		w.reg():


if __name__ == '__main__':
	print sys.argv
	# init
	if len(sys.argv) <= 1:
		print 'use : python main.php reg'
	# reg
	elif sys.argv[1] == 'reg':
		reg()
	# others
	else:
		print 'no action find'

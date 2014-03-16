# coding:utf-8

config = {
	'reg': {				# 注册用户名设置, 生成 前缀+随机数  如 tc_325153
		'name_prx': 'jd_',		# 前缀
		'name_len': 6,			# 数字部分长度
		'password': 'tian1991'	# 固定密码,忽纯数字,并确保长度>=8
		# 'password': '8' 		# 随机8位
	},
	'dama': {
		'flag': 'dama2',	# 打码服务商选择
		'dama2': {			# 打码兔 dama2.com
			'username': '',
			'password': ''
		},
		'chaoren': {		# QQ超人 sz789.net
			'username': '',
			'password': ''
		}
	},
	'yushou': [				# 预约地址, 每行一个
		'',
	],
	'item': '1056969'		# 京东的商品ID
}
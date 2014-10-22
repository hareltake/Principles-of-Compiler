#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import LexicalAnals
from assist import Production, Nonterminal, Terminal 


PRODUCTION = []

TERMINAL = ['INT', 'HEX', 'OCTAL', 'FLOAT', 'STRING', 'VARIABLE',
			'{', '}', '[', ']', '(', ')', '~', ',', ';', '.', '#', '?', ':',
			'if', 'else', 'while', 'break', 'continue', 'for', 'double', 'int', 'float', 'long', 'char', 'short', 'switch', 'case', 'return', 'include',
			'+', '++', '-', '--', '+=', '-=', '*', '*=', '/', '/=', '>', '<', '>=', '<=', '=', '==', '!=', '!', '$']

SPE_TERMINAL = ['INT', 'HEX', 'OCTAL', 'FLOAT', 'STRING', 'VARIABLE']

NONTERMINAL = set()

V_SYMBOL = {}
N_T_PRO = {}
stack = []

#从文件读取产生式
def read_production():
	f = open('production.txt', 'r')
	lines = f.readlines()
	for l in lines:
		left = l.split('->')[0].strip()
		NONTERMINAL.update([left])
		right = l.split('->')[1].strip()
		if right == '':
			p = Production(left, ['NULL'], False)
		else:
			p = Production(left, right.split(), False)
		PRODUCTION.append(p)


#生成字符值到对象的字典
def pro_v_symbol():
	for v in NONTERMINAL:
		non_ter = Nonterminal(v, False)
		V_SYMBOL[v] = non_ter

#寻找所有可推导为空的非终结符
def find_null():
	for pro in PRODUCTION:
		if pro.right == ['NULL']:
			non_ter = V_SYMBOL.get(pro.left)
			non_ter.is_null = True
			pro.is_null = True
			#可空则在first集里加'NULL'
			non_ter.first.add('NULL')
			pro.first.add('NULL')

	while True:
		#平衡判断标志
		is_balance = True
		for pro in PRODUCTION:
			non_ter = V_SYMBOL.get(pro.left)
			if non_ter.is_null is False:
				non_ter.is_null = deduct_null(pro)
				if non_ter.is_null:
					is_balance = False
		if is_balance:
			break
#判断非终结符可不可以推导为空
def deduct_null(pro):
	for symbol in pro.right:
		if symbol in TERMINAL:
			return False
		else:
			non_ter = V_SYMBOL.get(symbol)
			if non_ter.is_null:
				continue
			else:
				return False
	return True

#生成每个非终结符和产生式的first集
def pro_first():
	while True:
		#平衡判断标志
		is_balance = True
		for pro in PRODUCTION:
			if pro.is_null:
				continue
			#将该产生式的first置为空
			pro.first.clear()
			non_ter = V_SYMBOL.get(pro.left)
			#初始fisrt集长度
			s = len(non_ter.first)
			#first可空标志
			has_null = True
			for symbol in pro.right:
				if symbol in TERMINAL:
					non_ter.first.add(symbol)
					pro.first.add(symbol)
					has_null = False
					break
				else:
					r_non_ter = V_SYMBOL.get(symbol)
					if r_non_ter.is_null:
						non_ter.first.update(r_non_ter.first - set(['NULL']))
						pro.first.update(r_non_ter.first - set(['NULL']))
						continue
					else:
						non_ter.first.update(r_non_ter.first)
						pro.first.update(r_non_ter.first)
						has_null = False
						break
			#如果first可空，则加入'NULL'
			if has_null:
				non_ter.first.add('NULL')
				pro.first.add('NULL')
				pro.is_null = True
			#结束first集长度
			e = len(non_ter.first)
			if e > s:
				is_balance = False
		if is_balance:
			break

#生成非终结符的follow集
def pro_follow():
	while True:
		is_balance = True
		for pro in PRODUCTION:
			if pro.is_null:
				continue
			#右部长度
			l = len(pro.right)
			#左部非终结符
			l_non_ter = V_SYMBOL.get(pro.left)
			for i in range(0, l):
				if pro.right[i] in TERMINAL:
					continue
				non_ter = V_SYMBOL.get(pro.right[i])
				#初始follow集长度
				s = len(non_ter.follow)
				#是否包含左部的follow集
				has_left = True
				for j in range(i+1, l):
					if pro.right[j] in TERMINAL:
						non_ter.follow.add(pro.right[j])
						has_left = False
						break
					else:
						r_non_ter = V_SYMBOL.get(pro.right[j])
						if r_non_ter.is_null:
							non_ter.follow.update(r_non_ter.first - set(['NULL']))
							continue
						else:
							non_ter.follow.update(r_non_ter.first)
							has_left = False
							break
				if has_left:
					non_ter.follow.update(l_non_ter.follow)
				#结束follow集长度
				e = len(non_ter.follow)
				if e > s:
					is_balance = False
		if is_balance:
			break

#生成每个产生式的select集
def pro_select():
	for pro in PRODUCTION:
		if pro.is_null:
			non_ter = V_SYMBOL.get(pro.left)
			#在这里必须使用union操作
			pro.select = non_ter.follow.union(pro.first - set(['NULL']))
		else:
			pro.select = pro.first

#生成解析表
def pro_parsing_table():
	for non_ter in NONTERMINAL:
		N_T_PRO[non_ter] = {}
	#错误恢复处理，将follow集作为SYNCH
	for pro in PRODUCTION:
		non_ter = V_SYMBOL.get(pro.left)
		for ter in non_ter.follow:
			N_T_PRO[pro.left][ter] = 'SYNCH'
	for pro in PRODUCTION:
		for ter in pro.select:
			N_T_PRO[pro.left][ter] = pro
#读入一个token，并进行栈操作
def parser(t):
	while stack[-1] not in TERMINAL:
		pro = N_T_PRO.get(stack[-1]).get(t)
		#错误恢复处理
		if pro is None:
			#产生式为空，跳过token
			print 'Wrong 1' + '\n'
			return 
		if pro == 'SYNCH':
			#遇到\'SYNCH\',弹栈
			print 'Wrong 2' + '\n'
			stack.pop()
			continue
		print '当前token:  ' + t
		print '栈:  ' + str(stack) + '\n' + '产生式:  ' + str(pro) + '\n'
		stack.pop()
		if pro.right != ['NULL']:
			for sym in pro.right[::-1]:
				stack.append(sym)
		#若栈里只剩'$',则结束
		if len(stack) == 1 and stack[-1] == '$':
			print '栈:  ' + str(stack)
			return
	#错误恢复处理
	if stack[-1] != t:
		#栈顶非终结符与token不相等，弹栈
		print 'Wrong 3' + '\n'
		stack.pop()
		parser(t)
	print '当前token:  ' + t
	print '栈:  ' + str(stack) + '\n'
	stack.pop()

def main():
	read_production()
	pro_v_symbol()
	find_null()
	pro_first()
	pro_follow()
	pro_select()
	pro_parsing_table()
	# for n in NONTERMINAL:
	# 	print n + ':  '
	# 	for t in TERMINAL:
	# 		pro = N_T_PRO.get(n).get(t)
	# 		if pro is not None:
	# 			print t + ':  ' + str(pro)
	# 	print 
	stack.append('$')
	stack.append('<functions>')
	file_name = sys.argv[1]
	LexicalAnals.read_file(file_name)
	while True:
		t = LexicalAnals.scanner()
		if t == 'EOF':
			parser('$')
			break
		if t == None:
			continue
		if t[0] == 'CNOTE' or t[0] == 'C++NOTE':
			print t
			continue
		if t[0] in SPE_TERMINAL:
			parser(t[0])
		else:
			parser(t[1])

if __name__ == '__main__':
	main()
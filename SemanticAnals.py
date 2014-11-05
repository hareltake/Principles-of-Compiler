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

ci = -1
ch = -1
co = -1
cf = -1
cs = -1
cv = -1
S_C = {}
S_C['INT'] = ci
S_C['HEX'] = ch
S_C['OCTAl'] = co
S_C['FLOAT'] = cf
S_C['STRING'] = cs
S_C['VARIABLE'] = cv

label = -1
prev_f = -1
prev_n = -1
offset = 0

NONTERMINAL = set()
#非终结符值到对象的字典
V_SYMBOL = {}
#解析表嵌套字典
N_T_PRO = {}
#非终结符属性值的嵌套字典
SYMBOL_A = {}
#语义动作临时变量到值的字典
TEMP_V = {}
#特殊终结符到值的字典
TER_V = {}
#变量表嵌套字典
VARIABLE_V = {}
#栈
stack = []
#三地址码产生式栈
three_stack = []

#从文件读取产生式
def read_production():
	f = open('action.txt', 'r')
	lines = f.readlines()
	for l in lines:
		left = l.split('->')[0].strip()
		NONTERMINAL.update([left])
		right = l.split('->')[1].strip()
		if left == 'C' and right[0] == '#':
			p = Production(left, ['NULL'], False)
		elif left == 'E\'' and right[0] == '#':
			p = Production(left, ['NULL'], False)
		elif left == 'B\'' and right[0] == '#':
			p = Production(left, ['NULL'], False)
		elif right == '':
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
		if '#' in symbol:
			continue
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
				elif symbol in NONTERMINAL:
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
			#右部长度
			l = len(pro.right)
			#左部非终结符
			l_non_ter = V_SYMBOL.get(pro.left)
			for i in range(0, l):
				if pro.right[i] in TERMINAL:
					continue
				elif pro.right[i] in NONTERMINAL:
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
						elif pro.right[j] in NONTERMINAL:
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

#生成符号表
def pro_symbol_table():
	for non_ter in NONTERMINAL:
		SYMBOL_A[non_ter] = {}

#读入一个token，并进行栈操作，语义动作
def parser(t):
	while stack[-1] not in TERMINAL:
		#如果栈顶是语义动作
		if '#' in stack[-1]:
			sem_act = stack[-1].strip('##')
			sem_att = sem_act.split(',')
			#最简单的语义动作
			if len(sem_att) == 1:
				l = sem_att[0].split('.')
				SYMBOL_A[l[0]][l[1]] = -1
				stack.pop()
				continue
			if len(sem_att) == 2:
				if sem_att[0] == 'offset':
					global offset
					l = sem_att[1].split('.')
					print 'SYMBOL_TABLE:   ' + TER_V['VARIABLE' + str(S_C['VARIABLE'])] + '  ' + SYMBOL_A[l[0]]['type'] + '  ' + str(offset)
					offset += SYMBOL_A[l[0]][l[1]]
					#将变量写入变量符号表
					VARIABLE_V[TER_V['VARIABLE' + str(S_C['VARIABLE'])]] = {}
					#变量初始值为-1
					VARIABLE_V[TER_V['VARIABLE' + str(S_C['VARIABLE'])]]['addr'] = -1
					S_C['VARIABLE'] -= 1

				if '.' in sem_att[0]:
					l = sem_att[0].split('.')
					#T.type = C.type
					if '.' in sem_att[1]:
						r = sem_att[1].split('.')
						SYMBOL_A[l[0]][l[1]] = SYMBOL_A[r[0]][r[1]]
						# print 'T.type = C.type'
					#T.type = INT/VARIABLE
					elif sem_att[1] in SPE_TERMINAL:
						nv = TER_V[sem_att[1] + str(S_C[sem_att[1]])]
						S_C[sem_att[1]] -= 1
						if sem_att[1] == 'VARIABLE':
							if VARIABLE_V.get(nv) == None:
								print nv + ' is not defined'
								SYMBOL_A[l[0]][l[1]] = -1
							else:
								SYMBOL_A[l[0]][l[1]] = VARIABLE_V[nv]['addr']
						else:
							SYMBOL_A[l[0]][l[1]] = nv
					#T.type = int
					elif sem_att[1] in TERMINAL or sem_att[1] == 'null':
						SYMBOL_A[l[0]][l[1]] = sem_att[1]
						# print 'T.type = int'
					#T.type = 4
					elif sem_att[1].isdigit():
						SYMBOL_A[l[0]][l[1]] = int(sem_att[1])
						# print 'T.type = 4'
					#S.next = newlabel()
					elif sem_att[1] == 'label':
						global prev_f
						global prev_n
						SYMBOL_A[l[0]][l[1]] = label + 1
						if l[1] == 'false':
							three_stack[prev_f] = str(prev_f) + ':   goto  ' + str(label + 1)
						elif l[1] == 'next':
							three_stack[prev_n] = str(prev_n) + ':   goto  ' + str(label + 1)
					#T.type = t
					else:
						SYMBOL_A[l[0]][l[1]] = TEMP_V[sem_att[1]]
						# print 'T.type = t'


				else:
					#t = T.type
					if '.' in sem_att[1]:
						r = sem_att[1].split('.')
						TEMP_V[sem_att[0]] = SYMBOL_A[r[0]][r[1]]
						# print 't = T.type'
					elif sem_att[0] == 'begin':
						TEMP_V['begin'] = label + 1
					#t = t
					else:
						TEMP_V[sem_att[0]] = TEMP_V[sem_att[1]]
						# print 't = t'
				stack.pop()
				continue
			#其他语义动作 TODO
			if len(sem_att) == 3:
				if sem_att[0] == 'gen':
					global label
					if sem_att[2] == 'E.addr':
						variable = TER_V['VARIABLE' + str(S_C['VARIABLE'])]
						S_C['VARIABLE'] -= 1
						if VARIABLE_V.get(variable) == None:
							print variable + ' is not defined'
						else:
							VARIABLE_V[variable]['addr'] = SYMBOL_A['E']['addr'] 
							label += 1
							three_stack.append(str(label) + ':   ' + variable + ' = ' + str(SYMBOL_A['E']['addr']))
					elif sem_att[1] == 'VARIABLE':
						variable = TER_V['VARIABLE' + str(S_C['VARIABLE'])]
						S_C['VARIABLE'] -= 1
						if VARIABLE_V.get(variable) == None:
							print variable + 'is not defined'
							SYMBOL_A['E']['addr'] = -1
						else:
							if SYMBOL_A['E\'']['r'] == '+':
								SYMBOL_A['E']['addr'] = VARIABLE_V[variable]['addr'] + SYMBOL_A['E\'']['addr']
								label += 1
								three_stack.append(str(label) + ':   ' + 'E.addr = ' + str(VARIABLE_V[variable]['addr']) + ' + ' + str(SYMBOL_A['E\'']['addr']))
							elif SYMBOL_A['E\'']['r'] == '*':
								SYMBOL_A['E']['addr'] = VARIABLE_V[variable]['addr'] * SYMBOL_A['E\'']['addr']
								label += 1
								three_stack.append(str(label) + ':   ' + 'E.addr = ' + str(VARIABLE_V[variable]['addr']) + ' * ' + str(SYMBOL_A['E\'']['addr']))
							elif SYMBOL_A['E\'']['r'] == 'null':
								SYMBOL_A['E']['addr'] = VARIABLE_V[variable]['addr']
								label += 1
								three_stack.append(str(label) + ':   ' + 'E.addr = ' + str(VARIABLE_V[variable]['addr']))

					elif sem_att[1] == 'INT':
						value = TER_V['INT' + str(S_C['INT'])]
						S_C['INT'] -= 1
						if SYMBOL_A['E\'']['r'] == '+':
							SYMBOL_A['E']['addr'] = value + SYMBOL_A['E\'']['addr']
							label += 1
							three_stack.append(str(label) + ':   ' + 'E.addr = ' + str(value) + ' + ' + str(SYMBOL_A['E\'']['addr']))
						elif SYMBOL_A['E\'']['r'] == '*':
							SYMBOL_A['E']['addr'] = value * SYMBOL_A['E\'']['addr']
							label += 1
							three_stack.append(str(label) + ':   ' + 'E.addr = ' + str(value) + ' * ' + str(SYMBOL_A['E\'']['addr']))
						elif SYMBOL_A['E\'']['r'] == 'null':
							SYMBOL_A['E']['addr'] = value
							label += 1
							three_stack.append(str(label) + ':   ' + 'E.addr = ' + str(value))
					elif sem_att[1] == 'goto':
						label += 1
						if sem_att[2] == 'E.false':
							prev_f = label
							three_stack.append('')
						elif sem_att[2] == 'S.next' or sem_att[2] == 'L.next':
							prev_n = label
							three_stack.append('')
						elif sem_att[2] == 'begin':
							three_stack.append(str(label) + ':   ' + 'goto  ' + str(TEMP_V['begin']))


				else:
					SYMBOL_A['E\'']['r'] = sem_att[0]
					SYMBOL_A['E\'']['addr'] = SYMBOL_A['E']['addr']
				stack.pop()
				continue

			if len(sem_att) == 4:
				if sem_att[1] == 'array':
					l = sem_att[0].split('.')
					SYMBOL_A[l[0]][l[1]] = 'array(' + str(TER_V[sem_att[2] + str(S_C['INT'])]) + ', ' + SYMBOL_A[l[0]][l[1]] + ')'
					stack.pop()
					sem_act = stack[-1].strip('##')
					sem_att = sem_act.split(',')
					r = sem_att[0].split('.')
					SYMBOL_A[r[0]][r[1]] = TER_V[sem_att[1] + str(S_C['INT'])] * SYMBOL_A[r[0]][r[1]]
					S_C['INT'] -= 1
				elif sem_att[1] == 'E.addr':
					label += 1
					three_stack.append(str(label) + ':   if  ' + str(SYMBOL_A['E']['addr']) + '  goto  ' + str(label + 2))
				stack.pop()
				continue

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
		stack.pop()
		if pro.right != ['NULL']:
			for sym in pro.right[::-1]:
				stack.append(sym)
		elif pro.left == 'C':
			stack.append('#C.width,w#')
			stack.append('#C.type,t#')
		elif pro.left == 'E\'':
			stack.append('#E\'.r,null')
		elif pro.left == 'B\'':
			stack.append('#E.false,label#')

		#若栈里只剩'$',则结束
		if len(stack) == 1 and stack[-1] == '$':
			return
	#错误恢复处理
	if stack[-1] != t:
		#栈顶非终结符与token不相等，弹栈
		print 'Wrong 3' + '\n'
		stack.pop()
		parser(t)
	stack.pop()

def main():
	read_production()
	pro_v_symbol()
	find_null()
	pro_first()
	pro_follow()
	pro_select()
	pro_parsing_table()
	pro_symbol_table()
	#初始化值
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
			S_C[t[0]] += 1
			TER_V[t[0] + str(S_C[t[0]])] = t[1]
		else:
			parser(t[1])
	for three in three_stack:
		print three

if __name__ == '__main__':
	main()
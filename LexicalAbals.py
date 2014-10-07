#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys

#关键字列表
KEYWORD = ['if', 'else', 'while', 'break', 'continue', 'for', 'double', 'int', 'float', 'long', 'char', 'short', 'switch', 'case', 'return']
#分隔符列表
SEPARATOR = ['{', '}', '[', ']', '(', ')', '~', ',', ';', '.', '#', '?', ':']
#操作符列表
OPERATOR = ['+', '++', '-', '--', '+=', '-=', '*', '*=', '/', '/=', '>', '<', '>=', '<=', '=', '==', '!=', '!']
#16进制列表
HEX = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'A', 'B', 'C', 'D', 'E', 'F']
#8进制列表
OCTAL = ['0', '1', '2', '3', '4', '5', '6', '7']
#当前行和当前列
current_row = -1
current_line = 0
#存储文件
input_str = []

def is_keyword(s):
	return s in KEYWORD

def is_separator(s):
	return s in SEPARATOR

def is_operator(s):
	return s in OPERATOR

def is_hex(s):
	return s in HEX

def is_octal(s):
	return s in OCTAL
#读取一个字符
def getchar():
	global current_row
	global current_line
	current_row += 1
	if current_row == len(input_str[current_line]):
		current_line += 1
		current_row = 0

	if current_line == len(input_str):
		return "EOF"
	return input_str[current_line][current_row]
#回退一个字符
def ungetc():
	global current_row
	global current_line
	current_row -= 1
	if current_row < 0:
		current_line -= 1
		current_row = len(input_str[current_line]) - 1

	return input_str[current_line][current_row]

def read_file(file):
	global input_str
	f = open(file, 'r')
	input_str = f.readlines()
	f.close()

def lexical_error(info, line=None, row=None):
	if line is None:
		line = current_line + 1
	if row is None:
		row = current_row + 1
	print(str(line) + ':' + str(row) + ' Lexical error: ' + info)
#自动机
def scanner():
	global current_line
	global current_row
	current_char = getchar()
	if current_char == 'EOF':
		return 'EOF'

	if current_char.strip() == '':
		return
#检测浮点数，十进制、八进制、十六进制整数
	if current_char.isdigit():
		if(current_char == '0'):
			next_char = getchar()
			if(next_char == 'x'):
				hex = '0x'
				next_char = getchar()
				if not is_hex(next_char):
					ungetc()
					lexical_error('illegal hex number')
					return None
				else:
					while is_hex(next_char):
						hex += next_char
						next_char = getchar()
					ungetc()
					return ('HEX', hex)
			elif is_octal(next_char):
				octal = '0'
				while is_octal(next_char):
					octal += next_char
					next_char = getchar()
				ungetc()
				return ('OCTAL', octal)
			elif next_char.isdigit():
				ungetc()
				lexical_error('illegal octal number')
				return None
			ungetc()
			return ('INT', 0)
		value = 0			
		while current_char.isdigit():
			value = value * 10 + int(current_char)
			current_char = getchar()

		if current_char != '.':
			ungetc()
			return ('INT', value)

		float_str = str(value) + '.'
		current_char = getchar()
		while current_char.isdigit():
			float_str += current_char
			current_char = getchar()

		ungetc()
		return ('FLOAT', float_str)
#检测关键字、变量
	if current_char.isalpha() or current_char == '_':
		variable = ''
		while (current_char != 'EOF' and current_char.isalpha()) or current_char.isdigit() or current_char == '_':
			variable += current_char
			current_char = getchar()
		ungetc()
		if is_keyword(variable):
			return ('KEYWORD', variable)
		else:
			return ('VARIABLE', variable)
#检测单个字符
	if current_char == '\'':
		current_char = getchar()
		if current_char == 'EOF':
			ungetc()
			lexical_error('illegal char')
			return None
		next_char = getchar()
		if next_char == '\'':
			return ('CHAR', current_char)
		ungetc()
		ungetc()
		lexical_error('illegal char')
		return None
#检测字符串
	if current_char == '\"':
		string = ''
		line = current_line
		row = current_row

		current_char = getchar()
		while current_char != '\"':
			string += current_char
			current_char = getchar()
			if current_char == 'EOF':
				lexical_error('missing termination \"', line + 1 ,row + 1)
				current_line = line
				current_row = row 
				return None
		return ('STRING', string)
#检测注释（同时支持C和C++风格），/打头的操作符
	if current_char == '/':
		next_char = getchar()
		line = current_line
		row = current_row
		if next_char == '*':
			c_note = ''
			next_char = getchar()
			while True:
				if next_char == 'EOF':
					lexical_error('missing termination */', line ,row)
					return 'EOF'
				if next_char == '*':
					end_char = getchar()
					if end_char == '/':
						return ('CNOTE', c_note)
					if end_char == 'EOF':
						lexical_error('missing termination /', line + 1, row + 1)
						return 'EOF'
				c_note += next_char
				next_char = getchar()
		elif next_char == '/':
			cc_note = ''
			next_char = getchar()
			#读到末尾
			while current_line == line:
				cc_note += next_char
				next_char = getchar()
			ungetc()
			return ('C++NOTE', cc_note)


		else:
			ungetc()
			op = current_char
			next_char = getchar()
			if is_operator(next_char):
				op += next_char
				if is_operator(op):
					return ('OPERATOR', op)
			ungetc()
			return ('OPERATOR', current_char)
#检测分隔符
	if is_separator(current_char):
		return ('SEPARATOR', current_char)
#检测操作符（双界符优先）
	if is_operator(current_char):
		op = current_char
		next_char = getchar()
		if is_operator(next_char):
			op += next_char
			if is_operator(op):
				return ('OPERATOR', op)
		ungetc()
		return ('OPERATOR', current_char)
	else:
		print(current_char)
		lexical_error('unknown character')

def main():
	file_name = sys.argv[1]
	read_file(file_name)
	while True:
		r = scanner()
		if r == 'EOF':
			break;
		if r is not None:
			print(r)

if __name__ == '__main__':
	main()





Principles-of-Compiler
======================
##Lexical Analysis
LexicalAnals.py                 
在亮叔的基础上添加了八进制、十六进制、字符、C++风格注释的检测和纠错，并且修复了一些关键bug
##Syntax Analysis
production.txt:产生式             
SyntaxAnals.py                                              
LL(1)文法的句法分析器，可以识别函数，声明，赋值，循环，分支等基本语句，并有简单的错误恢复处理
##Semantic Analysis
action.txt：语义动作                                                           
SemanticAnals.py                                   
L属性的SDT，可以对声明，赋值，循环，分支等结构就行语义分析。

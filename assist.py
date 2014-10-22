

class Production(object):
	def __init__(self, left, right, is_null):
		self.left = left
		self.right = right
		self.is_null = False
		self.first = set()
		self.select = set()

	def __str__(self):
		return str(self.left) + '-->' + str(self.right)



class Nonterminal(object):
	def __init__(self, value, is_null):
		self.value = value
		self.is_null = is_null
		self.first = set()
		self.follow = set('$')


class Terminal(object):
	def __init__(self, value, is_null):
		self.value = value
		self.is_null = is_null
		self.first = set()
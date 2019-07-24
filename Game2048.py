#导入要用的模块
from random import randint,choice
import curses
from collections import defaultdict
letter_codes = [ord(ch) for ch in 'WASDREwasdre']
actions = ['Up', 'Left', 'Down', 'Right', 'Reset', 'Exit']
actions_dict = dict(zip(letter_codes,actions*2))
#矩阵类
class Matrix(object):
	
	def __init__(self):
	#画
		self.width = 4
		self.height =4
		self.Zeros()
		
	def Zeros(self):
		self.field = [[0 for i in range(self.width)] for j in range(self.height)]
	def transpose(self):
		#矩阵转置
		#zip可以用来将可迭代对象的对应元素打包成元组，以列表的形式返回
		return [list(row) for row in zip(*self.field)]
		
	def invert(self):
		#矩阵逆转
		return [row[::-1] for row in self.field]
		
	def invert_transpose(self):
		#同时进行转置和逆转的矩阵
		return [row[::-1] for row in [list(row) for row in zip(*self.field)]]
	
	#生成随机数
	def spwan(self):
		new_element = 2 if randint(0,10) > 1 else 4
		(i,j) = choice([(i,j) for i in range(self.width) for j in range(self.height) if self.field[i][j] == 0])
		self.field[i][j] = new_element
		
class Game(object):

	def __init__(self,Win_score):
		self.score = 0 
		self.matrix = Matrix()
		self.Win_score = Win_score
		for i in range(2):
			self.matrix.spwan()
		self.Exit = False
		self.state = "Gaming"
		
	def get_user_action(self,keyabord):
		char = 'N'
		while char not in actions_dict:
			char = keyabord.getch()
		#直到获得有效输入才返回响应
		return actions_dict[char]
			
	def Play(self,stdscr):
	
		curses.use_default_colors()
		while not self.Exit:
			self.draw(stdscr)
			if self.game_state() == 'Win':
				stdscr.addstr(f"You Win!And your score is {self.score}"+'\n')
				stdscr.addstr("Reset(R) or Exit(E)"+'\n')
				#改变状态
				comm = self.get_user_action(stdscr)
				if comm == "Reset": 
					self.Reset()
				elif comm == "Exit":
				#退出游戏
					self.exit()
				else :
					pass
			elif self.game_state() == 'Fail':
				stdscr.addstr(f"I'm sorry you're faild with score {self.score}")
				#改变状态
				stdscr.addstr("Reset(R) or Exit(E)"+'\n')
				comm = self.get_user_action(stdscr)
				if actions_dict[comm] == "Reset": 
					self.Reset()
				#退出游戏
				elif actions_dict[comm] == "Exit":
					self.Exit()
				else :
					pass
			else:
				#接受信息
				comm = self.get_user_action(stdscr)
				self.Move(comm,stdscr)
				
			
		
	#生成随机数
	def Reset(self):
		self.score = 0
		self.matrix.Zeros()
		for i in range(2):
			self.matrix.spwan()
			
		self.state = 'Gaming'
		
	def exit(self):
		self.Exit = True
		
	#移动函数
	def Move(self,direction,screen):
	
		def Movable_left(row):
		#以向左为例，当所有行满足以下条件就不能移动
		#1.该方向上无法合并 2.没有0在任意非0数前方
			for i in range(len(row)-1):
				if (row[i] == row[i+1] and row[i]+row[i+1]>0) or (row[i]+row[i+1]>0 and row[i]==0):
					return True
						
			return False
		
		Movable={}
		Movable['Left'] = lambda matrix:any([Movable_left(row) for row in matrix.field])
		Movable['Right']= lambda matrix:any([Movable_left(row) for row in matrix.invert()])
		Movable['Up'] = lambda matrix:any([Movable_left(row) for row in matrix.transpose()])
		Movable['Down'] = lambda matrix:any([Movable_left(row) for row in matrix.invert_transpose()])
		def move_to_left(row):
			new_list = []
			Merged = False
			for i in row:
				if i!=0:
					if len(new_list) == 0 or (new_list[-1]!=i) or Merged == True:
						new_list.append(i)
						Merged = False
					else:
						new_list[-1]*=2
						#加分
						self.score += new_list[-1]
						Merged = True
			while len(new_list)<len(row):
				#补0
				new_list.append(0)
			return new_list
		
		moves = {}
	
		moves['Left'] = lambda matrix:[move_to_left(row) for row in matrix.field]
		
		moves['Right'] = lambda matrix:[move_to_left(row)[::-1] for row in matrix.invert()]
		
		moves['Up'] = lambda matrix:[list(row) for row in zip(*[move_to_left(row) for row in matrix.transpose()])]
		
		moves['Down'] = lambda matrix:[list(row) for row in zip(*[move_to_left(row) for row in matrix.invert_transpose()])][::-1]
			
		if direction in moves:
			if Movable[direction](self.matrix):
				self.matrix.field = moves[direction](self.matrix)	
				#随机生成操作
				self.matrix.spwan()
				
			else:
				#该方向上不做处理
				pass
			
		else:
		#不做处理
			pass
			
	
	#判断胜利
	def is_win(self):
		return any(any(i >= self.Win_score for i in row) for row in self.matrix.field  )
		
	def is_gameover(self):
		#假如存在0元素，则游戏一定还未结束
		if  not all(all(value  for value in row) for row in self.matrix.field):
			return False
		else: #否则检查是否存在相邻元素相等
			if any(any(row[j] == row[j+1] for j in range(0,self.matrix.width - 1))for row in self.matrix.field):
				return False
			elif any(any(row[j] == row[j+1] for j in range(0,self.matrix.width - 1))for row in self.matrix.transpose()):
				return False
			else:
				return True
			
	def game_state(self):
		if self.is_win():
			return 'Win'
		
		elif self.is_gameover():
			return 'Fail'
			
		else :
			return 'Gaming'
	
	#画棋盘	
	def draw(self,screen):
		helpstring1 = "W(up) S(down) A(left) D(right)"
		
		def draw_line():
				
			line = ('+------'*4+'+')
				
			#defaultdict可以为字典中不存在的关键字提供默认值，赋值后separator[i] = line
			separator = defaultdict(lambda:line)
			#hasattr() 函数用于判断对象是否包含对应的属性;python的函数是一种对象，它有对象的属性和自定义的属性
			'''经过测试可以发现，函数内部的属性
			   .每次函数调用，函数内部的属性是不做保留的，即每次调用，该函数的属性都会被重新定义
			   .但是，如果函数内部调用了函数，在函数内部调用子函数多次，那么该子函数的属性会被保留下来，无论该函数是定义在函数内部还是外部
			'''
				
			if not hasattr(draw_line,'counter'):
					
				draw_line.counter = 0
					
			#在屏幕中打印框架
			screen.addstr(separator[draw_line.counter]+'\n')
			draw_line.counter +=1
				
		def draw_num(row_num):
			
			screen.addstr(''.join('|{: ^5}'.format(num) for num in row_num )+'|'+'\n')
				
		screen.clear()
			
		screen.addstr(f"score:{self.score}"+ '\n')
			
		for row in self.matrix.field:
			
			draw_line()
				
			draw_num(row)
				
		draw_line()
			#打印帮助信息
		screen.addstr(helpstring1+'\n')
			
	
def main():
	#创建游戏对象
	game = Game(Win_score = 2048)
	curses.wrapper(game.Play)
	
main()
	
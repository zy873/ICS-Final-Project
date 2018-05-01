import random

S_INITIAL = '0'
S_FLAG = '1'
S_MINES = '2'
S_BLANK = '3'

#class MinesweeperGroup:
#	def __init__(self):
#		self.games = {}
#		self.game_member = {}
#		self.games_ever = 0
#	
#	def join(self, player1, player2):
#		self.games[self.games_ever + 1] = Minesweeper(player1, player2)
#		self.game_member[self.games_ever + 1] =([player1, player2])
#		self.games_ever += 1
#	
#	def find_group(self, player):
#		found = False
#		group_key = 0
#		for k in self.game_member.keys():
#			if player in self.game_member[k]:
#				found = True
#				group_key = k
#				break
#		return found, group_key
#	
#	def list_all(self, me):
#		full_list += "Games in play: -----------" + "\n"
#		full_list += str(self.game_member) + "\n"
#		return full_list

	
class Minesweeper:
	def __init__(self, player1, player2, mines_num = 10):
		self.player1 = player1
		self.player2 = player2
		self.size = 9
		self.state = {S_INITIAL:'□', S_FLAG:'!', S_MINES:'■', S_BLANK:' '}
		self.mines_num = mines_num
		self.show_frame = {}
		self.bcground = {}
		self.letters = "ABCDEFGHI"
	
	def set_mines_num(self, mines_num):
			self.mines_num = mines_num	
		
	def menu(self):
		menu = 'f __pos__: flag the __pos__ as the mine\n \
				o __pos__: open the __pos__ that you think is safe\n\n'
		print(menu)

	def board(self):
		output = ''
		width =  '  '+' '.join(self.letters) + '\n'
		output += width
		
		# print board
		for j in range(1,self.size + 1):
			output += str(j) + ' '
			for i in self.letters:
				pos = i + str(j)
				output += self.state[S_INITIAL] + ' '
				self.show_frame[pos] = self.state[S_INITIAL]
			output += str(j) + '\n'
		output += width
		return output

	def generate_mines(self):
		# generate mines
		mines_list = []
		for i in range(self.mines_num):
			pos = random.choice(self.letters) + str(random.randint(1,self.size))
			while pos in mines_list:
				pos = random.choice(self.letters) + str(random.randint(1,self.size))
			mines_list.append(pos)
		for i in mines_list:
			self.bcground[i] = self.state[S_MINES]
		print(mines_list)
		
		# update number surrounding mines according to different mines' positions
		numbers = {}
		extended_letters = 'X' + self.letters + 'Y'
		for mine in mines_list:
				letter_pos = extended_letters.find(mine[0])
				letter = [extended_letters[letter_pos - 1], mine[0], extended_letters[letter_pos + 1]]
				for i in letter:
					for j in range(int(mine[1])-1, int(mine[1])+2):
						change_number_pos = i + str(j)
						#print(change_number_pos,mine)
						if change_number_pos != mine and change_number_pos[0] != 'X' and change_number_pos[0] != 'Y' and change_number_pos[1] != '0' and change_number_pos[1:] != '10':
							if change_number_pos in numbers.keys():
								numbers[change_number_pos] += 1
							else:
								numbers[change_number_pos] = 1
							self.bcground[change_number_pos] = numbers[change_number_pos]
				#print(mine, self.bcground[mine])
		#print(numbers)

		# update the blank spaces
		for keys in self.show_frame.keys():
			if keys not in numbers.keys():
				self.bcground[keys] = self.state[S_BLANK]
		
		# refresh the mine list
		for i in mines_list:
			self.bcground[i] = self.state[S_MINES]
		print(self.bcground)
			
	def play(self,user,msg):
		
		# display the changing game board to the users
		
		
test = Minesweeper('a', 'b')
print(test.board())
test.generate_mines()

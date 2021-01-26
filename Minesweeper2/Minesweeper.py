# -*- coding: utf-8 -*-
import random
random.seed(0)

S_INITIAL = '0'
S_FLAG = '1'
S_MINES = '2'
S_BLANK = '3'

S_ALONE = 0
S_PLAYING = 1

class MinesweeperGroup:
	def __init__(self):
		self.members = {}
		self.game_grps = {}
		self.game_ever = 0
		self.grp_object = {} #key: group number, value: class object

	def join(self, name):
		self.members[name] = S_ALONE
		return

	def is_member(self, name):
		return name in self.members.keys()

	def leave(self, name):
		self.disconnect(name)
		del self.members[name]
		return

	def find_group(self, name):
		found = False
		group_key = 0
		for k in self.game_grps.keys():
			if name in self.game_grps[k]:
				found = True
				group_key = k
				break
		return found, group_key

	def connect(self, me, peer):
		# connect assuming that peer in game pool & not in a game
		self.game_ever += 1
		group_key = self.game_ever
		self.game_grps[group_key] = []
		self.game_grps[group_key].append(me)
		self.game_grps[group_key].append(peer)
		self.members[me] = S_PLAYING
		self.members[peer] = S_PLAYING
		print(self.list_me(me))
		self.grp_object[group_key] = Minesweeper(me, peer)
		return group_key

	def disconnect(self, me):
		# find myself in the group, quit
		in_group, group_key = self.find_group(me)
		if in_group == True:
			self.game_grps[group_key].remove(me)
			self.members[me] = S_ALONE
			# peer may be the only one left as well...
			if len(self.game_grps[group_key]) == 1:
				peer = self.game_grps[group_key].pop()
				self.members[peer] = S_ALONE
				del self.game_grps[group_key]
		return

	def list_all(self):
		full_list = "Users: ------------" + "\n"
		full_list += str(self.members) + "\n"
		full_list += "Groups: -----------" + "\n"
		full_list += str(self.game_grps) + "\n"
		return full_list

	def list_me(self, me):
		# return a list, "me" followed by other peers in my group
		if me in self.members.keys():
			my_list = []
			my_list.append(me)
			in_group, group_key = self.find_group(me)
			if in_group == True:
				for member in self.game_grps[group_key]:
					if member != me:
						my_list.append(member)
		return my_list

	
class Minesweeper:
	def __init__(self, player1, player2, mines_num = 10):
		self.player1 = player1
		self.player1_move = {} #key:pos, value:move
		self.player2 = player2
		self.player2_move = {}
		self.initial_user = ''
		
		self.size = 9
		self.mines_num = mines_num
		self.state = {S_INITIAL:'□', S_FLAG:'!', S_MINES:'■', S_BLANK:' '}
		self.show_frame = {} #key: pos, value: state shown on the board
		self.bcground = {} #key: pos, value: actual mine map
		self.letters = "ABCDEFGHI"
		self.count_not_mine = 0
		
		self.change_frame = [] # all the positions whose values are changed
		
		self.win = False
		
	def menu(self):
		menu = 'f __pos__: flag the __pos__ as the mine\no __pos__: open the __pos__ that you think is safe\nexample: f A7\n\n'
		return menu
	
	def initialize_state(self):
		for j in range(1,self.size + 1):
			for i in self.letters:
				pos = i + str(j)
				self.show_frame[pos] = self.state[S_INITIAL]
	
	def set_mines_num(self, mines_num):
		while mines_num <= 0:
			return 'Wrong mine number.'
			mines_num = int(input('Enter a new number: '))
		self.mines_num = mines_num
		return 'You have succesfully set your mine number. Good luck.'	
		
	def board(self, pos_state):
		output = ''
		width =  '   ' + ' '.join(self.letters) + '\n'
		underline = '   ' + '-' * (self.size * 2 - 1) + '\n'
		output += width + underline
		
		# print board
		for j in range(1,self.size + 1):
			output += str(j) + '| '
			for i in self.letters:
				pos = i + str(j)
				output += str(pos_state[pos]) + ' '
			output += "|" + str(j) + '\n'
		output += underline + width 
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

						# if not mine & not on the extended board, add one
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
		# print(self.bcground)
		
		for ele in self.bcground.values():
			if str(ele).isdigit():
				self.count_not_mine += 1
			if ele == self.state[S_BLANK]:
				self.count_not_mine += 1
			
	def set_up_play(self):
		## display the changing game board to the users
		# Initialize the game: generate new board, mine map and the first mover
		self.initialize_state()
		print(self.board(self.show_frame))
		self.generate_mines()
		
		
		choice = random.randint(1,2)
		if choice == 1:
			self.initial_user = self.player1
		else:
			self.initial_user = self.player2
		starter = self.initial_user + ' can move now.'
		return self.initial_user
	
	def move(self, player_name, msg): #msg will be in the form in the menu, no duplicate operation on the same pos
		msg = msg.split(' ')
		oper = msg[0]
		pos = msg [1]
		end_msg = ''
		
		# determine which player dictionary to refresh
		if player_name == self.player1:
			self.player1_move[pos] = oper
		else:
			self.player2_move[pos] = oper
		
		#reset valid next player
		z = [self.player1, self.player2]
		z.remove(self.initial_user)
		self.initial_user = z[0]
		
		#refresh the board according to the player's move	
		if oper == 'f':
			self.show_frame[pos] = self.state[S_FLAG]
			return self.initial_user, self.board(self.show_frame), end_msg
		elif oper == 'o':
			if self.bcground[pos] == self.state[S_MINES]:
				end_msg = 'BOOM!!!!\n'+ player_name + ' steps on the mine!!!\nYou are back to the game pool now.\n'
				self.win = True
				return self.initial_user, self.board(self.bcground), end_msg
			else:
				self.click_display(pos)
				
				#decide if win
				self.count_show_frame_not_mine = 0
				for ele in self.show_frame.values():
					if str(ele).isdigit():
						self.count_show_frame_not_mine += 1
					if ele == self.state[S_BLANK]:
						self.count_show_frame_not_mine += 1	
				if self.count_not_mine == self.count_show_frame_not_mine:
					end_msg = 'Congratulations! Both of you won :D\nYou are back to the game pool now.\n '
					self.win = True	
				return self.initial_user, self.board(self.show_frame), end_msg
	
	def click_display(self, pos):
		if pos in self.change_frame:
			return
		else:
			self.change_frame.append(pos)
		
		recur_list  = []
		if self.bcground[pos] == self.state[S_BLANK]:
			
			flag = True
			
			if self.show_frame[pos] == self.state[S_FLAG]:
				flag = False
				save = self.state[S_FLAG]
			self.show_frame[pos] = self.state[S_BLANK]
			
			extended_letters = 'X' + self.letters + 'Y'
			letter_pos = extended_letters.find(pos[0])
			letter = [extended_letters[letter_pos - 1], pos[0], extended_letters[letter_pos + 1]]
			# find the areas surrounding the current pos 
			for i in letter:
				for j in range(int(pos[1])-1, int(pos[1])+2):
					surrounding_pos = i + str(j)
					#print(change_number_pos,mine)
					if surrounding_pos != pos and surrounding_pos[0] != 'X' and surrounding_pos[0] != 'Y' and surrounding_pos[1] != '0' and surrounding_pos[1:] != '10' and surrounding_pos not in self.change_frame:
						recur_list.append(surrounding_pos)
			
			if not flag:
				self.show_frame[pos] = save
			
			if len(recur_list) == 0:
				#print(self.show_frame)
				return			
			else:
				for ele in recur_list:
					self.click_display(ele)
				#print(self.show_frame)
		elif str(self.bcground[pos]).isdigit():
			self.show_frame[pos] = self.bcground[pos]
			#print(self.show_frame)
							
			
#test = Minesweeper('a', 'b')
#test.set_up_play()
#test.move('b','o A1')
#test.move('a','o A2')
#test.move('b','o A3')
#test.move('b','o A4')
#test.move('a','o B1')
#test.move('b','o B3')
#test.move('a','o B4')
#test.move('b','o B5')
#test.move('a','o C1')
#test.move('b','o C3')
#test.move('a','o C4')
#test.move('b','o G6')
#test.move('b','f E9')
#test.move('b','o H5')
#test.move('a','o H7')
#test.move('b','o I7')
#test.move('b','o E6') 
#test.move('a','o G9')
#test.move('b','o I6')
#test.move('a','o I9')


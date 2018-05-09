"""
Created on Tue Jul 22 00:47:05 2014
@author: alina, zzhang
"""

import time
import socket
import select
import sys
import string
import indexer
import json
import pickle as pkl
from chat_utils import *
import chat_group as grp

from Minesweeper import *
import gui_board as gb

class Server:
	def __init__(self):
		self.new_clients = [] #list of new sockets of which the user id is not known
		self.logged_name2sock = {} #dictionary mapping username to socket
		self.logged_sock2name = {} # dict mapping socket to user name
		self.all_sockets = []
		self.group = grp.Group()
		self.group_key = 0

         #start server
		self.server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.bind(SERVER)
		self.server.listen(5)
		self.all_sockets.append(self.server)
		
		#initialize past chat indices
		self.indices={}
		
		# sonnet
		self.sonnet_f = open('AllSonnets.txt.idx', 'rb')
		self.sonnet = pkl.load(self.sonnet_f)
		self.sonnet_f.close()
		
		# pass to the minesweeper game
		self.minesweeper_group = MinesweeperGroup()
		self.short = '' # will be a class in Minesweeper
		self.starter = '' # game starter
		self.board = '' # game board
		self.rules = ''
		self.end_msg = ''
		
		# game leader board        
		self.start_time = 0
		self.end_time = 0
		self.top_grp = []
		self.top_time = []
		self.leaderboard = {100000:['testplayer1','testplayer2'],100020:['testplayer3','testplayer4'],100010:['testplayer5','testplayer6']} #key: time period , value: grp members' names as a list
		
	def new_client(self, sock):
		#add to all sockets and to new clients
		print('new client...')
		sock.setblocking(0)
		self.new_clients.append(sock)
		self.all_sockets.append(sock)

	def login(self, sock):
		#read the msg that should have login code plus username
		try:
			msg = json.loads(myrecv(sock))
			if len(msg) > 0:

				if msg["action"] == "login":
					name = msg["name"]
					if self.group.is_member(name) != True:
						#move socket from new clients list to logged clients
						self.new_clients.remove(sock)
						#add into the name to sock mapping
						self.logged_name2sock[name] = sock
						self.logged_sock2name[sock] = name
						#load chat history of that user
						if name not in self.indices.keys():
							try:
								self.indices[name]=pkl.load(open(name+'.idx','rb'))
							except IOError: #chat index does not exist, then create one
								self.indices[name] = indexer.Index(name)
						print(name + ' logged in')
						self.group.join(name)
						mysend(sock, json.dumps({"action":"login", "status":"ok"}))
					else: #a client under this name has already logged in
						mysend(sock, json.dumps({"action":"login", "status":"duplicate"}))
						print(name + ' duplicate login attempt')
				else:
					print ('wrong code received')
			else: #client died unexpectedly
				self.logout(sock)
		except:
			self.all_sockets.remove(sock)

	def logout(self, sock):
		#remove sock from all lists
		name = self.logged_sock2name[sock]
		pkl.dump(self.indices[name], open(name + '.idx','wb'))
		del self.indices[name]
		del self.logged_name2sock[name]
		del self.logged_sock2name[sock]
		self.all_sockets.remove(sock)
		self.group.leave(name)
		sock.close()

#==============================================================================
# main command switchboard
#==============================================================================
	def handle_msg(self, from_sock):
		#read msg code
		msg = myrecv(from_sock)
		if len(msg) > 0:
#==============================================================================
# handle connect request
#==============================================================================
			msg = json.loads(msg)
			if msg["action"] == "connect":
				to_name = msg["target"]
				from_name = self.logged_sock2name[from_sock]
				if to_name == from_name:
					msg = json.dumps({"action":"connect", "status":"self"})
				# connect to the peer
				elif self.group.is_member(to_name):
					to_sock = self.logged_name2sock[to_name]
					self.group.connect(from_name, to_name)
					the_guys = self.group.list_me(from_name)
					msg = json.dumps({"action":"connect", "status":"success"})
					for g in the_guys[1:]:
						to_sock = self.logged_name2sock[g]
						mysend(to_sock, json.dumps({"action":"connect", "status":"request", "from":from_name}))
				else:
					msg = json.dumps({"action":"connect", "status":"no-user"})
				mysend(from_sock, msg)
#==============================================================================
# handle messeage exchange: one peer for now. will need multicast later
#==============================================================================
			elif msg["action"] == "exchange":
				from_name = self.logged_sock2name[from_sock]
				the_guys = self.group.list_me(from_name)
				#said = msg["from"]+msg["message"]
				said2 = text_proc(msg["message"], from_name)
				self.indices[from_name].add_msg_and_index(said2)
				for g in the_guys[1:]:
					to_sock = self.logged_name2sock[g]
					self.indices[g].add_msg_and_index(said2)
					mysend(to_sock, json.dumps({"action":"exchange", "from":msg["from"], "message":msg["message"]}))
#==============================================================================
#                 listing available peers
#==============================================================================
			elif msg["action"] == "list":
				from_name = self.logged_sock2name[from_sock]
				msg = self.group.list_all(from_name)
				mysend(from_sock, json.dumps({"action":"list", "results":msg}))
#==============================================================================
#             retrieve a sonnet
#==============================================================================
			elif msg["action"] == "poem":
				poem_indx = int(msg["target"])
				from_name = self.logged_sock2name[from_sock]
				print(from_name + ' asks for ', poem_indx)
				poem = self.sonnet.get_sect(poem_indx)
				print('here:\n', poem)
				mysend(from_sock, json.dumps({"action":"poem", "results":poem}))
#==============================================================================
#                 time
#==============================================================================
			elif msg["action"] == "time":
				ctime = time.strftime('%d.%m.%y,%H:%M', time.localtime())
				mysend(from_sock, json.dumps({"action":"time", "results":ctime}))
#==============================================================================
#                 search
#==============================================================================
			elif msg["action"] == "search":
				term = msg["target"]
				from_name = self.logged_sock2name[from_sock]
				print('search for ' + from_name + ' for ' + term)
				search_rslt = (self.indices[from_name].search(term)).strip()
				print('server side search: ' + search_rslt)
				mysend(from_sock, json.dumps({"action":"search", "results":search_rslt}))
#==============================================================================
# the "from" guy has had enough (talking to "to")!
#==============================================================================
			elif msg["action"] == "disconnect":
				from_name = self.logged_sock2name[from_sock]
				the_guys = self.group.list_me(from_name)
				self.group.disconnect(from_name)
				the_guys.remove(from_name)
				if len(the_guys) == 1:  # only one left
					g = the_guys.pop()
					to_sock = self.logged_name2sock[g]
					mysend(to_sock, json.dumps({"action":"disconnect"}))
#==============================================================================
#                log in the Minesweeper game pool
#==============================================================================	
			elif msg['action'] == 'login_game':
				from_name = self.logged_sock2name[from_sock]
				
				# determine whether the user is already in the game pool
				if self.minesweeper_group.is_member(from_name):
					mysend(from_sock, json.dumps({"server_msg":'In pool'}))
				else:
					self.minesweeper_group.join(from_name)
					mysend(from_sock, json.dumps({"server_msg":'success'}))
					print(from_name + " joins the game pool.")
					print(self.minesweeper_group.list_all())
#==============================================================================
#                quit the Minesweeper game pool
#==============================================================================						
			elif msg['action'] == 'quit game':
				from_name = self.logged_sock2name[from_sock]
				try:
					# if the player is currently in a game and want to forcefully quit the game, let the other side know
					player = self.minesweeper_group.list_me(from_name)[1]
					to_sock = self.logged_name2sock[player]
					mysend(to_sock, json.dumps({"server_msg": "quit game"}))
				except:
					pass
				self.minesweeper_group.leave(from_name)
				print(from_name + ' leaves the game pool.')

#==============================================================================
#                quit the current game
#==============================================================================	
			elif msg['action'] == 'quit playing':
				try: # if the peer has sent back comments for the game
					if msg['forced'] == 'yes':
						output = open('Feedback.txt','a')
						output.write(str(msg['feedback'])+'\n')
						output.close()
				except:
					# if the comment is from me
					from_name = self.logged_sock2name[from_sock]
					print(self.minesweeper_group.list_all())
					player = self.minesweeper_group.list_me(from_name)[1]
					to_sock = self.logged_name2sock[player]
					
					# if end game due to one wins, return the end msg
					try:
						mysend(to_sock, json.dumps({"server_msg": msg['reason'],'starter': self.starter,'board':self.board, 'end_msg':self.end_msg,'leaderboard':msg['leaderboard'],'gui_lb': self.leaderboard,'peer':player}))
					# if sb forcefully end the game, return this result
					except:
						mysend(to_sock, json.dumps({"server_msg": "quit playing"}))
					self.minesweeper_group.disconnect(from_name)
					print(from_name + ' leaves the current game.')
					# write to the file if player has commments
					try:
						output = open('Feedback.txt','a')
						output.write(str(msg['feedback'])+'\n')
						output.close()
					except:
						pass
#==============================================================================
#                connect two players, set up game
#==============================================================================				
			elif msg['action'] == "request":
				from_name = self.logged_sock2name[from_sock]
				to_name = msg["target"]
				if from_name == to_name:
					mysend(from_sock, json.dumps({'server_msg':'connect to self'}))
				else:
					# determine whether peer is in game pool
					if self.minesweeper_group.is_member(to_name):
						in_grp, grp_num = self.minesweeper_group.find_group(to_name)
						# determine whether peer is in a game
						if in_grp == False:
							mysend(from_sock, json.dumps({'server_msg':'you can connect'}))
							self.group_key = self.minesweeper_group.connect(from_name, to_name)
							print(self.minesweeper_group.game_grps)
							print(from_name + ' ' + to_name + " are connected.")
						else:
							mysend(from_sock, json.dumps({'server_msg':'in a game'}))
					else:
						mysend(from_sock, json.dumps({'server_msg':'not in pool','game_group':self.minesweeper_group.list_all()}))
			
			elif msg['action'] == 'request successful':
				from_name = self.logged_sock2name[from_sock]
				to_name = msg["target"]
				to_sock = self.logged_name2sock[to_name]
				
				# initialize the game: pass in Minesweeper class, find the starter, find the inital board, start timing
				self.short = self.minesweeper_group.grp_object[self.group_key]
				self.starter = self.short.set_up_play()
				self.board = self.short.board(self.short.show_frame)
				self.rules = self.short.menu()
				mysend(from_sock, json.dumps({'starter': self.starter,'board':self.board, 'rules': self.rules}))
				mysend(to_sock, json.dumps({'action':'request successful','from':from_name,'starter': self.starter,'board':self.board, 'rules': self.rules}))
				import time
				self.start_time = time.time()
                  
#==============================================================================
#                in the minesweeper game
#==============================================================================						
			elif msg['action'] == 'game move': #client has entered the instructions for game move
				from_name = self.logged_sock2name[from_sock]
				other = self.minesweeper_group.list_me(from_name)[1]
				to_sock = self.logged_name2sock[other]
				
				print(self.short.win)
				# if the game has not finished
				if not self.short.win:
					# determine whether client's message are valid for the game
					instr = msg["message"]
					instr = instr.split(' ')
					oper = instr[0]
					pos = instr [1]
					
					# check whether is the right player to make the move
					if from_name == self.starter:
						# check whether the position enterered has not been opend and is a valid pos on the board
						if (pos[0] in self.short.letters) and pos[1:] <='9' and pos[1:] >= '1' and (pos not in self.short.change_frame):
							
							# if valid, make the move
							self.starter, self.board, self.end_msg = self.short.move(from_name, msg["message"])
                            
							leader_msg = ''
							
							if self.short.win:
                                # append into leaderboard dict
								import time
								self.end_time = time.time()
								period = float(format(self.end_time - self.start_time, '.3f'))
								grp_member = [from_name, other]
								
								# if win, update leaderboard
								if self.end_msg == 'Congratulations! Both of you won :D\nYou are back to the game pool now.\n ':
									self.leaderboard[period] = grp_member
#									print(self.leaderboard)
									self.top_grp = []
									self.top_time = []
									
									for time in sorted(self.leaderboard.keys()):
										self.top_grp.append(self.leaderboard[time])
										self.top_time.append(time)
									
									self.top_grp = self.top_grp[:3]
									self.top_time = self.top_time[:3]
									
									for i in range(3):
										self.leaderboard[self.top_time[i]] = self.top_grp[i]
									
#								print(self.leaderboard)

								for i in range(3):
									try:
										leader_msg += 'No. ' + str(i+1) + '   ' + str(self.top_grp[i]) + '   ' + str(self.top_time[i]) +'\n'
									except:
										leader_msg += '-----------------------------------\n'
                                
							
							mysend(from_sock, json.dumps({'server_msg':'successfully moved', 'starter': self.starter,'board':self.board, 'end_msg':self.end_msg,'leaderboard':leader_msg,'gui_lb': self.leaderboard}))
							mysend(to_sock, json.dumps({'server_msg':'successfully moved','starter': self.starter,'board':self.board, 'end_msg':self.end_msg,'leaderboard':leader_msg,'gui_lb': self.leaderboard}))	
						else:
							mysend(from_sock, json.dumps({'server_msg': "Invalid move"}))
					else:
						mysend(from_sock, json.dumps({'server_msg': "Wrong player"}))
					
				else:
					print('ERROR')
                     
#==============================================================================
#                 the "from" guy really, really has had enough
#==============================================================================
		else:
			#client died unexpectedly
			self.logout(from_sock)

#==============================================================================
# main loop, loops *forever*
#==============================================================================
	def run(self):
		print ('starting server...')
		while(1):
		   read,write,error=select.select(self.all_sockets,[],[])
		   print('checking logged clients..')
		   for logc in list(self.logged_name2sock.values()):
			   if logc in read:
				   self.handle_msg(logc)
		   print('checking new clients..')
		   for newc in self.new_clients[:]:
			   if newc in read:
				   self.login(newc)
		   print('checking for new connections..')
		   if self.server in read :
			   #new client request
			   sock, address=self.server.accept()
			   self.new_client(sock)

def main():
	server=Server()
	server.run()

main()
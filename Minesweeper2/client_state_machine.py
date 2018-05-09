"""
Created on Sun Apr  5 00:00:32 2015

@author: zhengzhang
"""
from chat_utils import *
import json
from Minesweeper import *
import gui_board as gb

class ClientSM:
    def __init__(self, s):
        self.state = S_OFFLINE
        self.peer = ''
        self.me = ''
        self.out_msg = ''
        self.s = s
        
    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def set_myname(self, name):
        self.me = name

    def get_myname(self):
        return self.me

    def connect_to(self, peer):
        msg = json.dumps({"action":"connect", "target":peer})
        mysend(self.s, msg)
        response = json.loads(myrecv(self.s))
        if response["status"] == "success":
            self.peer = peer
            self.out_msg += 'You are connected with '+ self.peer + '\n'
            return (True)
        elif response["status"] == "busy":
            self.out_msg += 'User is busy. Please try again later\n'
        elif response["status"] == "self":
            self.out_msg += 'Cannot talk to yourself (sick)\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False)

    def disconnect(self):
        msg = json.dumps({"action":"disconnect"})
        mysend(self.s, msg)
        self.out_msg += 'You are disconnected from ' + self.peer + '\n'
        self.peer = ''

    def proc(self, my_msg, peer_msg):
        self.out_msg = ''
#==============================================================================
# Once logged in, do a few things: get peer listing, connect, search
# And, of course, if you are so bored, just go
# This is event handling instate "S_LOGGEDIN"
#==============================================================================
        if self.state == S_LOGGEDIN:
            # todo: can't deal with multiple lines yet
            if len(my_msg) > 0:

                if my_msg == 'q':
                    self.out_msg += 'See you next time!\n'
                    self.state = S_OFFLINE

                elif my_msg == 'time':
                    mysend(self.s, json.dumps({"action":"time"}))
                    time_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += "Time is: " + time_in

                elif my_msg == 'who':
                    mysend(self.s, json.dumps({"action":"list"}))
                    logged_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += 'Here are all the users in the system:\n'
                    self.out_msg += logged_in

                elif my_msg[0] == 'c':
                    peer = my_msg[1:]
                    peer = peer.strip()
                    if self.connect_to(peer) == True:
                        self.state = S_CHATTING
                        self.out_msg += 'Connect to ' + peer + '. Chat away!\n\n'
                        self.out_msg += '-----------------------------------\n'
                    else:
                        self.out_msg += 'Connection unsuccessful\n'

                elif my_msg[0] == '?':
                    term = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"search", "target":term}))
                    search_rslt = json.loads(myrecv(self.s))["results"].strip()
                    if (len(search_rslt)) > 0:
                        self.out_msg += search_rslt + '\n\n'
                    else:
                        self.out_msg += '\'' + term + '\'' + ' not found\n\n'

                elif my_msg[0] == 'p' and my_msg[1:].isdigit():
                    poem_idx = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"poem", "target":poem_idx}))
                    poem = json.loads(myrecv(self.s))["results"].strip()
                    if (len(poem) > 0):
                        self.out_msg += poem + '\n\n'
                    else:
                        self.out_msg += 'Sonnet ' + poem_idx + ' not found\n\n'

                elif my_msg == 'ping blah blah':
                    self.out_msg += 'pong blah blah'
               
                elif my_msg == "g":
                    
                    mysend(self.s,json.dumps({'action':'login_game'}))
                    server_msg = json.loads(myrecv(self.s))["server_msg"]
                    if server_msg == 'In pool':
                        self.out_msg += 'You are already in the game pool.\n'
                    else:
                        self.state = S_GAME  
                        self.out_msg += "\nYou have just joined the game pool. Play now!\n"
                        self.out_msg += "Enter in the format of '@@ __partner__' to play the game with your partner.\n"
                        self.out_msg += '-----------------------------------\n'


            if len(peer_msg) > 0:
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "connect":
                    self.peer = peer_msg["from"]
                    self.out_msg += 'Chat Request from ' + self.peer + '\n'
                    self.out_msg += 'You are connected with ' + self.peer
                    self.out_msg += '. Chat away!\n\n'
                    self.out_msg += '------------------------------------\n'
                    self.state = S_CHATTING
                if peer_msg['action'] == 'request':
                    self.peer = peer_msg["from"]
                    self.out_msg += 'Game Request from ' + self.peer + '\n'
                    self.out_msg += 'Please enter g to join the game pool first.'

#==============================================================================
# Start chatting, 'bye' for quit
# This is event handling instate "S_CHATTING"
#==============================================================================
        elif self.state == S_CHATTING:
            if len(my_msg) > 0:     # my stuff going out
                mysend(self.s, json.dumps({"action":"exchange", "from":"[" + self.me + "]", "message":my_msg}))
                if my_msg == 'bye':
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ''
            if len(peer_msg) > 0:    # peer's stuff, coming in
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "connect":
                    self.out_msg += "(" + peer_msg["from"] + " joined)\n"
                elif peer_msg["action"] == "disconnect":
                    self.state = S_LOGGEDIN
            # Display the menu again
            if self.state == S_LOGGEDIN:
                self.out_msg += menu
#==============================================================================
# In the game pool, but not in a game
#==============================================================================
        elif self.state == S_GAME:
            if len(peer_msg) > 0:    # peer's stuff, coming in
                peer_msg = json.loads(peer_msg)
                if peer_msg['action'] == 'request successful':
                    self.peer = peer_msg["from"]
                    self.out_msg += 'Request from ' + self.peer + '\n'
                    self.out_msg += 'You are now in the game with ' + self.peer + '. Sweep mines now!\n'
                    self.out_msg += '------------------------------------\n\n'
                    
                    # print the inital game board and starter
                    self.out_msg += peer_msg['starter'] + ' should make the move.\n' + peer_msg['board'] + '\n' + peer_msg['rules'] + '\n'
                    self.state = S_PLAYING
                    
            if len(my_msg) > 0: # input g someone to connect with sb in game
                if my_msg == 'quit game':
                    msg = json.dumps({"action":"quit game"})
                    mysend(self.s, msg)
                    self.out_msg += 'You have logged out of the game pool.'
                    self.state = S_LOGGEDIN # and then print chat menu?
                else:
                    if my_msg[:2] == '@@':
                        peer = my_msg[2:]
                        peer = peer.strip()
                        
                        msg = json.dumps({"action":"request", "target":peer})
                        mysend(self.s, msg)

                        #if your partner is in the pool and is not in a game
                        server_msg = json.loads(myrecv(self.s))
                        if server_msg['server_msg'] == 'you can connect':
                            self.state = S_PLAYING
                            self.out_msg += 'You are now in the game with ' + peer + '. Sweep mines now!\n'
                            self.out_msg += '-----------------------------------\n\n'
                            mysend(self.s,json.dumps({'action':'request successful','target':peer}))
                            
                            # print the inital game board and starter and rules
                            server_msg = json.loads(myrecv(self.s))
                            self.out_msg += server_msg['starter'] + ' should make the move.\n' + server_msg['board'] + '\n' + server_msg['rules'] + '\n'
                            
                        elif server_msg['server_msg'] == 'in a game':
                            self.out_msg += 'Your partner is in a game now. Do you want to play the game with others?\n'
                        elif server_msg['server_msg'] == 'not in pool':
                            self.out_msg += 'Your partner is not in the game pool yet!\n' 
                            #now can only quit game, enter chat system, connect with peer, and then ask him to join
                            self.out_msg += server_msg['game_group']
                            #self.out_msg += json.loads(myrecv(self.s))['game_group']
                        elif server_msg['server_msg'] == 'connect to self':
                            self.out_msg += "Don't game with yourself! (sick)"
                    else:
                        self.out_msg += "Please make sure that you have entered the right instruction.\nEnter in the format of '@@ __partner__' to play the game with your partner.\n"

#==============================================================================
# In a game 
#==============================================================================
        elif self.state == S_PLAYING:
            
            if len(my_msg) > 0:
                if my_msg == 'quit playing':
                    msg = json.dumps({"action":"quit playing"})
                    mysend(self.s, msg)
                    self.out_msg += 'You have ended this game.'
                    self.state = S_GAME
                elif my_msg == 'quit game':
                    msg = json.dumps({"action":"quit game"})
                    mysend(self.s, msg)
                    self.out_msg += 'You have logged out of the game pool.'
                    self.state = S_LOGGEDIN
                else:
                    # making the game move
                    if my_msg[0] == 'f' or my_msg[0] == 'o':
                        mysend(self.s, json.dumps({"action": "game move", "from":"[" + self.me + "]", "message":my_msg}))
                        
                        # receive the server's judgement:
                        server_msg = json.loads(myrecv(self.s))
                        if server_msg["server_msg"] == 'successfully moved':
                            
                            # if the game has not finished
                            if server_msg['end_msg'] == '':
                                self.out_msg += '\n\n-----------------------------------\n'
                                self.out_msg += server_msg['starter'] + ' should make the next move.\n' + server_msg['board'] + '\n' 
                           
                            # if the game has finished
                            else:
                                print(server_msg['board'] + '\n' + server_msg['end_msg'] + '\n')
                                
                                # plus leaderboard
                                leaderboard = server_msg['leaderboard']
                                # because socket makes the keys str, need them back to float
                                leader_info = {}
                                for key in server_msg['gui_lb'].keys():
                                    leader_info[float(key)] = server_msg['gui_lb'][key]
                                
                                gb.main(self.me,leader_info)
                                try:
                                    comment, name = gb.get_data(1)
                                except:
                                    comment, name = '', ''

                                msg = json.dumps({"action":"quit playing",'reason':'game over', 'leaderboard':'LEADERBOARD\n' + leaderboard,'feedback': [comment + name]})
                                mysend(self.s, msg)
                                self.state = S_GAME
                                
                        elif server_msg['server_msg'] == "Invalid move":
                            self.out_msg += 'Please enter a valid move.\n'
                        
                        elif server_msg['server_msg'] == "Wrong player":
                            self.out_msg += 'This is not your turn yet! Please wait for your partner to move.\n'
                        
                        elif server_msg['server_msg'] == 'game over':
                            self.out_msg += server_msg['board'] + '\n' + server_msg['end_msg'] + '\n'
                            msg = json.dumps({"action":"quit playing"})
                            self.state = S_GAME
                            mysend(self.s, msg)
                    else:
                        pass
                        
            if len(peer_msg) > 0:
                
                peer_msg = json.loads(peer_msg) 
                if peer_msg['server_msg'] == "quit playing" or peer_msg['server_msg'] == "quit game":
                    self.out_msg += "You are forced to quit this game bc your partner has quited the game/game pool.\n"                    
                    self.state = S_GAME
                elif peer_msg['server_msg'] == 'game over':
                    print(peer_msg['board'] + '\n' + peer_msg['end_msg'] + '\n')
                    self.state = S_GAME

                    leaderboard = peer_msg['leaderboard']
                    leader_info = peer_msg['gui_lb']
                    gb.main(peer_msg['peer'],leader_info)
                    
                    try:
                        comment, name = gb.get_data(1)
                    except:
                        comment, name = '', ''
                    
                    # if receives feedback, send to the server
                    if comment != '' and name != '':
                        msg = json.dumps({"action":"quit playing",'reason':'game over', 'leaderboard':'LEADERBOARD\n' + leaderboard,'feedback': [comment + name],'forced': 'yes'})
                        mysend(self.s, msg)
                    else:
                        pass

                elif peer_msg['server_msg'] == 'successfully moved':
                    if '■' in peer_msg['board']:
                        pass
                    else:
                        self.out_msg += '\n\n-----------------------------------\n'
                        self.out_msg += peer_msg['starter'] + ' should make the next move.\n' + peer_msg['board'] + '\n'
                        self.out_msg += 'Your partner has made the move. Now it is your turn.'
                else:
                    self.out_msg += 'ERROR'
              
#==============================================================================
# invalid state
#==============================================================================
        else:
            self.out_msg += 'How did you wind up here??\n'
            print_state(self.state)
        
        return self.out_msg

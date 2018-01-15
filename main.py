###############################################################################
#
# Andrea Estrada | andrea9973@gmail.com
# Girls Who Code Summer 2018 Application 
# Main file handling all major gameplay
# Basic server outline (starter code): https://kdchin.gitbooks.io/sockets-module-manual/content/
# 
###############################################################################
import sys
import pygame
import time

from random import *

#multiplayer
import socket
import threading
from queue import Queue

#set up server
import server
import subprocess #allow user to start subprocess of running server

import userPort

###############################################################################
#
# INITIAL SERVER HANDLING
# 
###############################################################################

def setUpServer(data):
	data.p = subprocess.Popen(['python3', 'server.py'])

def joinServer(data):
	data.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	data.server.connect((userPort.host,int(data.port)))
	serverMsg = Queue(100)
	data.server = data.server
	threading.Thread(target = handleServerMsg, args = (data.server, serverMsg, data)).start()
	data.justJoined = True

def handleServerMsg(server, serverMsg, data):
	data.serverMsg = serverMsg
	server.setblocking(1)
	msg = ""
	command = ""
	while True:
		msg += data.server.recv(10).decode("UTF-8")
		command = msg.split("\n")
		while (len(command) > 1):
			readyMsg = command[0]
			msg = "\n".join(command[1:])
			data.serverMsg.put(readyMsg)
			command = msg.split("\n")

#write selected port number to file
def replacePort(data, dataFile, line, port):
	lines = open(dataFile, 'r').readlines()
	lines[line] = "port = %s\n" % port
	out = open(dataFile, 'w')
	out.writelines(lines)
	out.close()

###############################################################################
#
# GAMEPLAY
# 
###############################################################################

class RockPaperScissors(object):

	#################################
	#
	# Initialize game
	# 
	#################################

	def init(data):
		data.port = ""

		data.myMove = None
		data.myScore = 0

		data.opponentMove = None
		data.opponentScore = 0
		data.printedWaiting = False

		data.meReady = False
		data.opponentReady = False

		data.roundTie = False
		data.waiting = True

		data.rounds = 3
		data.winningScore = data.rounds//2 + 1 #guaranteed win

		data.gameStart = False
		data.gameDone = False

		data.justJoined = False

	#################################
	#
	# RPS Game
	# 
	#################################

	#manages gameplay
	def playGame(data):
		if not data.roundTie and not data.myMove and not data.opponentMove: data.gameOver() 
		if not data.gameDone:
			if data.myMove:
				if data.opponentMove:
					roundWinner = data.findWinner()
					data.printRoundInfo(roundWinner)
					data.printedWaiting = False
					data.clearRound()
				elif not data.printedWaiting:
					print("Waiting for opponent...")
					data.printedWaiting = True
			else: data.getMove()

	#get one valid move per player per round
	def getMove(data):
		while data.myMove == None:
			data.myMove = input("Please select a move. 1) rock 2) paper or 3) scissors: ")
			data.myMove = data.myMove.lower()
			if data.myMove == "1" or data.myMove == "rock": data.myMove = "rock"
			elif data.myMove == "2" or data.myMove == "paper": data.myMove = "paper"
			elif data.myMove == "3" or data.myMove == "scissors": data.myMove = "scissors"
			else:
				print("Command not recognized. Try again.")
				data.myMove = None
		msg = "OpponentChose %s \n" % data.myMove
		data.server.send(msg.encode())

	#determine winner of each round
	def findWinner(data):
		if data.myMove == "rock":
			if data.opponentMove == "rock": return False #tie
			elif data.opponentMove == "paper":
				data.opponentScore += 1
				return "opponent"
			else: 
				data.myScore += 1 #opponent move is scissors
				return "me"
		elif data.myMove == "paper":
			if data.opponentMove == "paper": return False #tie
			elif data.opponentMove == "scissors":
				data.opponentScore += 1
				return "opponent"
			else: 
				data.myScore += 1 #opponent move is rock
				return "me"
		#my move is scissors
		elif data.opponentMove == "scissors": return False #tie
		elif data.opponentMove == "rock": 
			data.opponentScore += 1
			return "opponent"
		else:
			data.myScore += 1 #opponent move is paper
			return "me"

	#displays outcome of each round
	def printRoundInfo(data, roundWinner):
		if not roundWinner: #tie game
			data.roundTie = True
			print("Tie! You played %s and your opponent also played %s. " % (data.myMove, data.opponentMove))
		else: #there is a winner of the round
			if roundWinner == "me":
				print("You win the round. Current standings:")
			else:
				print("Opponent wins the round. Current standings:")
			if data.myScore > data.opponentScore:
				print("\t1) You: %d" % data.myScore)
				print("\t2) Opponent: %d" % data.opponentScore)
			elif data.myScore < data.opponentScore:
				print("\t1) Opponent: %d" % data.opponentScore)
				print("\t2) You: %d" % data.myScore)
			else:
				print("\t1) You: %d" % data.myScore)
				print("\t1) Opponent: %d" % data.opponentScore)
			data.roundTie = False

	#resets info for each new round
	def clearRound(data):
		data.myMove = None
		data.opponentMove = None

	#print final game info
	def gameOver(data):
		if data.myScore == data.winningScore:
			print("Congrats! You won with a score of %d out of a possible %d. Your opponent's final score is %d." 
					% (data.myScore, data.rounds, data.opponentScore))
			data.gameDone = "True"
		elif data.opponentScore== data.winningScore:
			print("Opponent won with a score of %d out of a possible %d. Your final score is %d." 
					% (data.opponentScore, data.rounds, data.myScore))
			data.gameDone = "True"
		elif data.myScore + data.opponentScore >= data.winningScore:
			print("Continuing gameplay to resolve tie.")

	#################################
	#
	# Player game setup
	# 
	#################################

	def startGame(data):
		data.menu = None
		while data.menu == None:
			data.menu = input("Welcome to Rock, Paper, Scissors! You may 1) start a new game or 2) join an existing game. ")
			data.menu = data.menu.lower()
			if data.menu == "1" or data.menu == "new game" or data.menu == "start a new game" or data.menu == "start": data.menu = "start"
			elif data.menu == "2" or data.menu == "existing game" or data.menu == "join an existing game" or data.menu == "join": data.menu = "join"
			else: print("Command not recognized. Try again.")
		if data.menu == "start":
			print("Create a new game using a game code of your choice.")
			data.getCode()
			replacePort(data, "userPort.py", 0, data.port)
			print("Initializing...")
			setUpServer(data)
			time.sleep(3)
		if data.menu == "join":
			print("Join existing game via game code.")
			data.getCode()
			try: 
				print("Joining...")
				joinServer(data)
			except Exception as ex:
				print(ex)
				print("Oops! Something went wrong. Failed to join game.")
			time.sleep(3)

	def getCode(data):
		while True:
			data.port = input("Enter game code. Game code must be between 10000 and 65535. ")
			#valid value
			if str(data.port).isdigit() and len(str(data.port)) == 5 and int(data.port) <= 65535 \
				and int(data.port)>= 10000 : break
			else: print("Invalid value. Try again.")

	#################################
	#
	# Timer Fired: deal with server
	# 
	#################################

	#send message alerting opponent that player is ready
	def playerReady(data):
		data.selfReady = True
		msg = "OpponentReady ExtraneousDetail \n"
		data.server.send(msg.encode())
		if data.selfReady and data.otherReady:
			data.playing = True
			data.currTimer = 0

	def timerFired(data, dt):
		if not data.gameDone:
			#game play
			if data.meReady and data.opponentReady: data.gameStart = True
			if data.gameStart: data.playGame()
			elif not data.meReady and not data.justJoined: data.startGame()
			elif not data.printedWaiting:
				print("Waiting for opponent to join...")
				data.printedWaiting = True
			elif data.justJoined:
				data.justJoined = False
				print("Press enter to continue.")
			#server management
			if data.serverMsg and (data.serverMsg.qsize() > 0):
				msg = data.serverMsg.get(False)
				msg = msg.split()
				command = msg[0]

				if (command == "MyIDis"):
					data.myId = msg[1]
					print(data.myId)
					data.meReady = True
					if data.myId == "Player2": data.opponentReady = True

				elif (command == "PlayerJoined"): 
					data.opponentReady = True

				elif (command == "OpponentChose"): 
					data.opponentMove = msg[2]

				data.serverMsg.task_done()

	#################################
	#
	# Framework
	# 
	#################################

	def run(data, serverMsg = None, server = None):

		clock = pygame.time.Clock()

		data.serverMsg = serverMsg
		data.server = server

		data.currTimer = 0

		# call game-data initialization
		data.init()
		playing = True

		while playing:

			time = clock.tick(50)
			data.timerFired(time)
			seconds = clock.tick()/1000
			data.currTimer += seconds

		pygame.quit()


def main():

	game = RockPaperScissors()
	game.run()

if __name__ == "__main__":
   main()
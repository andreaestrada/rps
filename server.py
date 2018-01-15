###############################################################################
#
# Andrea Estrada | andrea9973@gmail.com
# Girls Who Code Summer 2018 Application 
# Handles player-to-player interactions
# Server outline (starter code): https://kdchin.gitbooks.io/sockets-module-manual/content/
# 
###############################################################################
import socket
import threading
from queue import Queue
import fileinput
import main
import sys

#designate which computer will host game
HOST = "" #insert IP Address for cross-computer game play

#port for gameplay: change until gameplay is smooth
PORT = 0 #RESTRICT S.T.: 10000 < PORT < 80000

def runServer():
  import userPort
  HOST = userPort.host
  PORT = int(userPort.port)

  #number of players who can join game
  BACKLOG = 2 #2 player game

  server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create socket
  server.bind((HOST,PORT)) #connect socket to specified values
  server.listen(BACKLOG)

  #note messages sent before player is added will not be sent later

  def handleClient(client, serverChannel, cID, clientele):
    client.setblocking(1)
    msg = ""
    while True:
      try:
        msg += client.recv(10).decode("UTF-8") #bytestring --> text string
        command = msg.split("\n") #signals end of message
        while (len(command) > 1): #string formatting of message
          readyMsg = command[0]
          msg = "\n".join(command[1:])
          serverChannel.put(str(cID) + " " + readyMsg) #put action on server thread
          command = msg.split("\n")
      except: return #error occured

  #Message restrictions: first instruction must be 1 word
  #Details *must* be included after instruction
  #End every message with a newline
  #NO SPACES BETWEEN COMMANDS
  def serverThread(clientele, serverChannel):
    while True:
      msg = serverChannel.get(True, None)
      msgList = msg.split(" ")
      senderID = msgList[0]
      instruction = msgList[1]
      details = " ".join(msgList[2:])
      if (details != ""):
        for cID in clientele:
          if cID != senderID:
            sendMsg = instruction + " " + senderID + " " + details + "\n"
            clientele[cID].send(sendMsg.encode())
      serverChannel.task_done()

  clientele = dict() #server thread
  playerNum = 0 #waiting for players to join

  serverChannel = Queue(100)
  threading.Thread(target = serverThread, args = (clientele, serverChannel)).start()

  names = ["Player1", "Player2"]

  while True:
    try:
      client, address = server.accept()
      # myID is the key to the client in the clientele dictionary
      myID = names[playerNum]
      for cID in clientele:
        clientele[cID].send(("PlayerJoined %s\n" % myID).encode())
        client.send(("PlayerJoined %s\n" % cID).encode())
      clientele[myID] = client
      client.send(("MyIDis %s \n" % myID).encode())
      #print("Connection recieved from %s" % myID)
      threading.Thread(target = handleClient, args = 
                            (client ,serverChannel, myID, clientele)).start()
      playerNum += 1
    except: pass
      #print("Max players previously reached. Could not join.")

if __name__ == '__main__': runServer()

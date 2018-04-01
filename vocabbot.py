#!/usr/binn/python3
import datetime
import requests
import socket
import time

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = "irc.snoonet.org"
channel = "#motitest" 
botnick = "VocabBot"
adminname = "MotivatorAFK"
exitcode = "bye " + botnick
host = "user/Motivator"

def joinchan(chan):
	ircsock.send(bytes("JOIN "+ chan +"\n", "UTF-8"))
	#Below is the original join code.
	#ircmsg = ""
	#while ircmsg.find("End of message of the day.") == -1:
		#ircmsg = ircsock.recv(2048).decode("UTF-8")
		#ircmsg = ircmsg.strip('\n\r')
		#print(ircmsg)

def sendmsg(msg, target=channel):
	ircsock.send(bytes("PRIVMSG "+ target +" :"+ msg +"\n", "UTF-8"))

if __name__ == '__main__':
	ircsock.connect((server, 6667))
	ircsock.send(bytes("USER "+ botnick +" "+ botnick +" "+ botnick + " " + botnick + "\n", "UTF-8"))
	ircsock.send(bytes("NICK "+ botnick +"\n", "UTF-8"))
	
	while True:
		ircmsg = ircsock.recv(2048).decode("UTF-8")
		ircmsg = ircmsg.strip('\n\r')
		print(ircmsg)
		
		try:
			msgcode = ircmsg.split()[0] #splitting the first part of RAW irc message
		except:
			pass
		msgcodet = ircmsg.split()[1]

		if msgcode == "001": #code that snoonet sends out when ready for join command
			joinchan(channel)
			
		joinchan(channel) #needs a second join command to connect to channel successfully
		
		if msgcodet == "PRIVMSG": 
			name = ircmsg.split('!',1)[0][1:] #splitting out the name from msgcodet
			namehost = ircmsg.split('@',1)[1].split(' ',1)[0]
			message = ircmsg.split('PRIVMSG',1)[1].split(':',1)[1]
			source = ircmsg.split('PRIVMSG ',1)[1].split(':',1)[0]
			print (source)
			print (namehost)
			
			if len(name) < 22: #username limit
				ircmsg = ircmsg.lower()
				botnick = botnick.lower()
				message = message.lower()
				if message.find('hi ' + botnick) != -1:
					print (message)
					sendmsg("Hello " + name + "!")
				
				if source == botnick:
					sendmsg(message, adminname)
					
				if host == namehost and message.strip() == "bye " + botnick:
					sendmsg("As you wish. :'(")
					ircsock.send(bytes("QUIT \n", "UTF-8"))
					ircsock.close() #broken?
		elif msgcode == "PING":
			ircsock.send(bytes("PONG " + ircmsg.split()[1] + "\r\n", "UTF-8")) #sending back a pong including custom ping code
print("Sent PONG " + ircmsg.split()[1])

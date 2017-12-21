#!/usr/binn/python3
import socket
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = "irc.snoonet.org"
channel = "##arctantest" 
botnick = "Botivator"
adminname = "MotivatorAFK"
exitcode = "bye " + botnick

def joinchan(chan):
	ircsock.send(bytes("JOIN "+ chan +"\n", "UTF-8"))
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
		
		msgcode = ircmsg.split()[0]
		msgcodet = ircmsg.split()[1]

		if msgcode == "001":
			joinchan(channel)
			
		joinchan(channel)
		
		if msgcodet == "PRIVMSG":
			name = ircmsg.split('!',1)[0][1:]
			message = ircmsg.split('PRIVMSG',1)[1].split(':',1)[1]

			if len(name) < 22:
				if message.find('Hi ' + botnick) != -1:
					sendmsg("Hello " + name + "!")
				if message[:5].find('.tell') != -1:
					target = message.split(' ', 1)[1]
					if target.find(' ') != -1:
						message = target.split(' ', 1)[1]
						target = target.split(' ')[0]
					else:
						target = name
						message = "Please try again. Message should in the format of '.tell [target] [message]' to work properly."
				try:
					sendmsg(message, target)
				except IndexError:
					sendmsg("Error.")
					
				if name.lower() == adminname.lower() and message.rstrip() == exitcode:
					sendmsg("As you wish. :'(")
					ircsock.send(bytes("QUIT \n", "UTF-8"))	
		elif msgcode == "PING":
			ircsock.send(bytes("PONG " + ircmsg.split()[1] + "\r\n", "UTF-8"))

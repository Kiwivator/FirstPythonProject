#!/usr/bin/python3
import socket



ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = "irc.snoonet.org" # Server
channel = "##mashlytest" # Channel
botnick = "BashlyTest" # Your bots nick
adminname = "mashly" # Your IRC nickname
exitcode = "Bye" + botnick
host = "user/mashly"
def joinchan(chan):
	ircsock.send(bytes("JOIN "+ chan +"\n", "UTF-8"))
	#ircmsg = ""
	#while ircmsg.find("End of /NAMES list.") == -1
	#	ircmsg = ircsock.recv(2048).decode("UTF-8")
	#	ircmsg = ircmsg.strip('\n\r')
	#	print (ircmsg)
def sendmsg(msg, target=channel): #sends message to the target
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
		
		if msgcode == "001": #code that snoonet sends out when ready for join command
			joinchan(channel)

		joinchan(channel)
		
		if msgcodet == "PRIVMSG":
			name = ircmsg.split('!',1)[0][1:] #splitting out name from msgcodet
			namehost = ircmsg.split('@',1)[1].split(' ',1)[1]
			message = ircmsg.split('PRIVMSG' ,1)[1].split(':',1)[1]
			source = ircmsg.split('PRIVMSG ',1)[1].split(':',1)[0]
			print (source)
			print (namehost)
			
			if len(name) < 17: #username limit
				ircmsg = ircmsg.lower()
				botnick = botnick.lower()
				message = message.lower()
				if message.find('Hi ' + botnick) != -1:
					print (message)
					sendmsg ("Hello " + name + "!")
				if source == botnick:
					sendmsg(message, adminname)
						
				if host == namehost and message[:5].find('.tell') != -1:
					print(message)
					print  (len(message))
					if len(message) == 5:
						message = "Please enter the name of a target and message. "
						target = name
					
					else:
						try:
							target = message.split(' ',1)[1]
						except IndexError:
							message = "Could not parse. The message should be in the format of '.tell [target] [message]' to work properly."
							target = name
							
						if target.find(' ') != -1:
							message = target.split(' ',1)[1]
							target = target.split(' ')[0]
						else:
							target = name
							message = "Could not parse. The message should be in the format of '.tell [target] [message]' to work properly."
					sendmsg(message, source)

				if host == namehost and message.rstrip()== exitcode:
					sendmsg("kthxbye ")
					ircsock.send(bytes("QUIT \n", "UTF-8"))
					ircsock.close()
			
		elif msgcode == "PING":
			ircsock.send(bytes("PONG " + ircmsg.split()[1] + "\r\n", "UTF-8")) #sending back a pong including custom ping code
			print("Sent PONG " + ircmsg.split()[1])

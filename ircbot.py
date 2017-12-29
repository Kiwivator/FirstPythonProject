#!/usr/binn/python3
import socket
import requests
from bs4 import BeautifulSoup

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
page = requests.get("http://www.weather.go.kr/weather/main-now-weather.jsp")
# http://www.weather.go.kr/weather/forecast/timeseries.jsp?searchType=INTEREST&wideCode=1100000000&cityCode=1159000000&dongCode=1159067000
soup = BeautifulSoup(page.content, 'html.parser')

server = "irc.snoonet.org"
channel = "#Motitest" 
botnick = "BotivatorTest"
adminname = "MotivatorAFK"
exitcode = "bye " + botnick

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
	
def gettemp(currenttemp):
	sendmsg('The current temperature in Seoul is ' + currenttemp + '°c.')
	print (currenttemp)

if __name__ == '__main__':
	ircsock.connect((server, 6667))
	ircsock.send(bytes("USER "+ botnick +" "+ botnick +" "+ botnick + " " + botnick + "\n", "UTF-8"))
	ircsock.send(bytes("NICK "+ botnick +"\n", "UTF-8"))
	
	while True:
		ircmsg = ircsock.recv(2048).decode("UTF-8")
		ircmsg = ircmsg.strip('\n\r')
		print(ircmsg)
		
		msgcode = ircmsg.split()[0] #splitting the first part of RAW irc message
		msgcodet = ircmsg.split()[1]

		if msgcode == "001": #code that snoonet sends out when ready for join command
			joinchan(channel)
			
		joinchan(channel) #needs a second join command to connect to channel successfully
		
		#Weather variables
		weather = soup.find(id="weather")
		seoul = weather.find(class_="po_seoul")
		currenttemp = seoul.find(class_="temp").get_text()
		
		if msgcodet == "PRIVMSG": 
			name = ircmsg.split('!',1)[0][1:] #splitting out the name from msgcodet
			message = ircmsg.split('PRIVMSG',1)[1].split(':',1)[1]
			
			if len(name) < 22: #username limit
				ircmsg == ircmsg.lower()
				if message.find('hi ' + botnick) != -1:
					sendmsg("Hello " + name + "!")
				if message[:5].find('.tell') != -1:
					print(message)
					print (len(message))
					if len(message) == 5: #TODO: this can probably be refactored with other error message
						message = "Please enter the name of a target and message. "
						target = name
							
					else:
						try:
							target = message.split(' ', 1)[1]
						except IndexError:
							message = "Please enter the name of a target and message. "
							target = name
							
						if target.find(' ') != -1:
							message = target.split(' ', 1)[1]
							target = target.split(' ')[0]
						else:
							target = name
							message = "Please try again. Message should be in the format of '.tell [target] [message]' to work properly."
				
					sendmsg(message, target)
				
				if message[:5].find('.temp') != -1:
					gettemp(currenttemp)					
					
				if name.lower() == adminname.lower() and message.rstrip() == exitcode:
					sendmsg("As you wish. :'(")
					ircsock.send(bytes("QUIT \n", "UTF-8"))
					ircsock.close() #broken?
		elif msgcode == "PING":
			ircsock.send(bytes("PONG " + ircmsg.split()[1] + "\r\n", "UTF-8")) #sending back a pong including custom ping code
			print("Sent PONG " + ircmsg.split()[1])
			      

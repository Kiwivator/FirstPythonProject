#!/usr/binn/python3
import socket
import requests
import time
from bs4 import BeautifulSoup

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = "irc.snoonet.org"
channel = "##motitest" 
botnick = "Botivatortest"
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
	
def gettemp(city):
	city = city.lower()
	index = "po_"
	cityi = index + city
	if city == "daejeon":
		cityi = "po_daejeoun"
	print (cityi)
	page = requests.get("http://www.weather.go.kr/weather/main-now-weather.jsp")
	soup = BeautifulSoup(page.content, 'html.parser')
	weather = soup.find(id="weather")
	citytemp = weather.find(class_=cityi)
	try:
		currenttemp = citytemp.find(class_="temp").get_text()
		currenttemp = float(currenttemp)
		currenttempf = (currenttemp * 1.8) + 32
		currenttempf = float(currenttempf)
		city = city.capitalize()
		sendmsg('The current temperature in ' + city + ' is ' + str(currenttemp) + '°C (' + str(currenttempf) + '°F).')
		print (str(currenttemp) + "/" + str(currenttempf))
	
	except:
		message = "Sorry, weather for this city isn't available, but may be added later."
		sendmsg(message, source)
                
def yaja():
	source = channel
	message = "야자타임 will now begin for 15 minutes. Everyone is free to use 반말 to each other until 야자타임 ends. Have fun and be nice!~"
	sendmsg(message, source)
	mins = 15
	while mins > 5:
		time.sleep(300)
		mins = mins - 5
		sendmsg("야자 타임 " + str(mins) + "분 남았습니다.")
		
	if mins == 5:
		sendmsg("야자 타임 " + str(mins) + "분 남았습니다. Prepare your 요s.")
		mins = mins - 1
		time.sleep(300)
	if mins == 0:
		sendmsg("야자 타임이 끝났습니다. Please speak as you would normally. If you'd like to continue speaking with someone you don't know well in 반말, it's best to ask their permission first.")
	# Make OP host list to limit command use
	# Change to 15 minutes
	# Make a break command?

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
				
				if host == namehost and message[:5].find('.tell') != -1:
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
					try:
						city = message.split(' ', 1)[1]
						print (city)
						gettemp(city)
						
					except IndexError:
						message = "Please enter .temp and the name of a city."
						target = name
						sendmsg(message, source)
						
				if message[:5].find('.yaja') != -1:
					yaja()

					
				if host == namehost and message.rstrip() == exitcode:
					sendmsg("As you wish. :'(")
					ircsock.send(bytes("QUIT \n", "UTF-8"))
					ircsock.close() #broken?
		elif msgcode == "PING":
			ircsock.send(bytes("PONG " + ircmsg.split()[1] + "\r\n", "UTF-8")) #sending back a pong including custom ping code
			print("Sent PONG " + ircmsg.split()[1])

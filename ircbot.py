#!/usr/binn/python3
import datetime
import json
import pytz
import random
import requests
import schedule
import socket
import time
import threading
import traceback
#import temp
from bs4 import BeautifulSoup

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = "irc.snoonet.org"
channel = "#Korean" 
botnick = "Botivator"
adminname = "MotivatorAFK"
exitcode = "bye " + botnick
host = "user/Motivator"
count = 6
lastshooter = "None"
oldtime = time.time()
hotpot = 0
todaypot = 0
olddate = datetime.date.today()

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

def parse_json_date(string):
	return datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%fZ')
	
def aqi():
	from pytz import timezone
	url = "http://api.airvisual.com/v2/city"
	querystring = {"city":"Seoul","state":"Seoul","country":"South Korea","key":"RwZdE7PnXSmPP5ALC"}
	response = requests.request("GET", url, params=querystring)
	print(response.text)
	#sendmsg("Raw data = " + response.text) #JUST A DEBUG MSG
	aqiapi = json.loads(response.content.decode('UTF-8'))
	#sendmsg("New dictionary = " + str(aqiapi)) #JUST A DEBUG MSG
	tp = aqiapi['data']['current']['weather']['tp']
	updatetime = aqiapi['data']['current']['pollution']['ts']
	utctime = parse_json_date(updatetime)
	korea_time = utctime.astimezone(timezone('Asia/Seoul'))
	korea_time = korea_time.strftime("%H:%M")
	print (str(utctime))
	try:
		sendmsg("Seoul's current AQI is " + str(aqiapi['data']['current']['pollution']['aqius']) + ". Reading taken at " + str(korea_time) + ". The temperature is " + str(tp) + "°C.")
	except Exception as e:
		sendmsg("You fucked up " + name + ". Try again.")
		print(traceback.format_exc())
	
def roulette(name):
	global count
	global lastshooter
	global oldtime
	diemsg = " BANG! Bad luck, you died."
	i = random.randint(1, count)
	if count == 1:
		misfire = random.randint(1, 3)
		if misfire == 3:
			sendmsg('Misfire! 운이 참 좋으시네요.')
		else:
			print ("Dead by last bullet")
			ircsock.send(bytes("KICK " + " " + channel + " " + name + " " + diemsg + "\n", "UTF-8"))
		count = 6
		oldtime = time.time()
	elif i == 1:
		print ("Dead by random number")
		ircsock.send(bytes("KICK " + " " + channel + " " + name + " " + diemsg + "\n", "UTF-8"))
		count = 6
		oldtime = time.time()
	else:
		count = count - 1
		lastshooter = name
		sendmsg('CLICK. You survived. There are ' + str(count) + ' chances left.')
	
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
	mins = mins - 5
	while mins == 10:
		time.sleep(300)
		sendmsg("야자 타임 " + str(mins) + "분 남았습니다.")
		print(str(mins) + " mins left.")
		mins = mins - 5
	if mins == 5:
		time.sleep(300)
		sendmsg("야자 타임 " + str(mins) + "분 남았습니다. Prepare your 요s.")
		print(str(mins) + " mins left.")
		mins = mins - 5
	if mins == 0:
		time.sleep(300)
		sendmsg("야자 타임이 끝났습니다. Please speak as you would normally. If you'd like to continue speaking with someone you don't know well in 반말, it's best to ask their permission first.")
	# Change to 15 minutes (warnings at 10,5,1 min left)
	# Make OP host list to limit command use 
	# Make async so that bot continues to PING/PONG and recognize commands
	# Make a break/extend command?

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
					threading.Thread(target=yaja).start()
					
				if message[:5].find('.radar') != -1:	
					sendmsg("http://www.weather.go.kr/weather/images/rader_integrate.jsp")
					
				if message[:9].find('.roulette') != -1:
					if name == lastshooter:
						sendmsg(name + "님이 방금 쐈습니다. 다른 유저가 먼저 쏴야 한번 더 쏠 수 있습니다.")
						pass
					elif time.time() - oldtime < 59:
						sendmsg("Please try again later.")
					else:
						roulette(name)
						
				if message.find('hotpot') != -1:
					print (olddate)
					if olddate < datetime.date.today():
						todaypot = 0
					olddate = datetime.date.today()
					hotpot += 1
					if hotpot == 5:
						todaypot += 5
						hotpot = 0
						sendmsg("Users in this channel have said hotpot {} times today.".format(todaypot))
					else:
						pass
					
				if message[:5].find('.aqi') != -1:
					aqi()
					
				if host == namehost and message.strip() == "bye " + botnick:
					sendmsg("As you wish. :'(")
					ircsock.send(bytes("QUIT \n", "UTF-8"))
					ircsock.close() #broken?
		elif msgcode == "PING":
			ircsock.send(bytes("PONG " + ircmsg.split()[1] + "\r\n", "UTF-8")) #sending back a pong including custom ping code
			print("Sent PONG " + ircmsg.split()[1])

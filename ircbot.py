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
# import temp
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
token = "4c65389e2ada51cbbc193f29fce77c8837ffe00c"
inf = float("inf")
levels = [("Good", 50), ("Moderate", 100), ("Unhealthy for sensitive groups", 151), ("Unhealthy", 201), ("Very unhealthy", 300), ("Hazardous", 998), ("DEATH", inf)];
pollutants = [("pm25", "PM2.5"), ("pm10", "PM10"), ("o3", "O3"), ("no2", "NO2")]

def joinchan(chan):
    ircsock.send(bytes("JOIN " + chan + "\n", "UTF-8"))


# Below is the original join code.
# ircmsg = ""
# while ircmsg.find("End of message of the day.") == -1:
# ircmsg = ircsock.recv(2048).decode("UTF-8")
# ircmsg = ircmsg.strip('\n\r')
# print(ircmsg)

def sendmsg(msg, target=channel):
    ircsock.send(bytes("PRIVMSG " + target + " :" + msg + "\n", "UTF-8"))


def parse_json_date(string):
    return datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%fZ')

def airrating(CurrentAQI):
    for a, b in levels:
        if CurrentAQI <= b:
            print(a)
            return a

def polformat(mainpol):
    for a, b in pollutants:
        if mainpol == a:
            print(b)
            return b


def aqisearch(keyword):
    # searches for location using keyword and returns the stationID
    url = "https://api.waqi.info/search/?keyword="
    searchresult = requests.request("GET", url + keyword + "&token=" + token)
    print(searchresult.text)
    searchlist = json.loads(searchresult.content.decode('UTF-8'))
    try:
        keyword = searchlist['data'][0]['uid']
        return keyword
    except:
        sendmsg("Location not found. Please try entering another area.")
        keyword = "NOTFOUND"
        return keyword

def aqi(keyword):
    #first tries to search for overall city data matching the keyword
    url = "https://api.waqi.info/feed/"
    response = requests.request("GET", url + keyword + "/?token=" + token)
    print(response.text)
    aqiapi = json.loads(response.content.decode('UTF-8'))

    status = aqiapi['status']
    if status != 'ok':
        #if no result then make a search query
        station = aqisearch(keyword)
        try:
            url = "https://api.waqi.info/feed/"
            response2 = requests.request("GET", url + "@" + str(station) + "/?token=" + token)
            #using the stationID to get detailed data - @ must come before stationID
            print(response2.text)
            aqiapi = json.loads(response2.content.decode('UTF-8'))
            #load new data into aqiapi
        except:
                print("Error1")

    else:
        pass

    #Continue parsing data from city/station feed
    try:
        CurrentAQI = aqiapi['data']['aqi']
        location = aqiapi['data']['city']['name']
        readingtime = aqiapi['data']['time']['s']
        mainpol = aqiapi['data']['dominentpol']
        sendmsg("[" + location + "]  " + "AQI: " + str(CurrentAQI) + " | Air Quality Rating: " + airrating(CurrentAQI) + " | Main pollutant: " + polformat(mainpol) + " | Reading taken: " + readingtime + " (local time)")
    except Exception as e:
        pass

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
            print("Dead by last bullet")
            ircsock.send(bytes("KICK " + " " + channel + " " + name + " " + diemsg + "\n", "UTF-8"))
        count = 6
        oldtime = time.time()
    elif i == 1:
        print("Dead by random number")
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
    print(cityi)
    page = requests.get("http://www.weather.go.kr/weather/main-now-weather.jsp")
    soup = BeautifulSoup(page.content, 'html.parser')
    weather = soup.find(id="weather")
    citytemp = weather.find(class_=cityi)
    try:
        currenttemp = citytemp.find(class_="temp").get_text()
        currenttemp = float(currenttemp)
        currenttempf = (currenttemp * 1.8) + 32
        currenttempf = round(currenttempf, 2)
        city = city.capitalize()
        sendmsg('The current temperature in ' + city + ' is ' + str(currenttemp) + '°C (' + str(currenttempf) + '°F).')
        print(str(currenttemp) + "/" + str(currenttempf))

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
        sendmsg(
            "야자 타임이 끝났습니다. Please speak as you would normally. If you'd like to continue speaking with someone you don't know well in 반말, it's best to ask their permission first.")


# Change to 15 minutes (warnings at 10,5,1 min left)
# Make OP host list to limit command use 
# Make async so that bot continues to PING/PONG and recognize commands
# Make a break/extend command?

if __name__ == '__main__':
    ircsock.connect((server, 6667))
    ircsock.send(bytes("USER " + botnick + " " + botnick + " " + botnick + " " + botnick + "\n", "UTF-8"))
    ircsock.send(bytes("NICK " + botnick + "\n", "UTF-8"))

    while True:
        ircmsg = ircsock.recv(2048).decode("UTF-8")
        ircmsg = ircmsg.strip('\n\r')
        print(ircmsg)

        try:
            msgcode = ircmsg.split()[0]  # splitting the first part of RAW irc message
        except:
            pass
        msgcodet = ircmsg.split()[1]

        if msgcode == "001":  # code that snoonet sends out when ready for join command
            joinchan(channel)

        joinchan(channel)  # needs a second join command to connect to channel successfully

        if msgcodet == "PRIVMSG":
            name = ircmsg.split('!', 1)[0][1:]  # splitting out the name from msgcodet
            namehost = ircmsg.split('@', 1)[1].split(' ', 1)[0]
            message = ircmsg.split('PRIVMSG', 1)[1].split(':', 1)[1]
            source = ircmsg.split('PRIVMSG ', 1)[1].split(':', 1)[0]
            print(source)
            print(namehost)

            if len(name) < 22:  # username limit
                ircmsg = ircmsg.lower()
                botnick = botnick.lower()
                message = message.lower()
                if message.find('hi ' + botnick) != -1:
                    print(message)
                    sendmsg("Hello " + name + "!")

                if source == botnick:
                    sendmsg(message, adminname)

                if host == namehost and message[:5].find('.tell') != -1:
                    print(message)
                    print(len(message))
                    if len(message) == 5:  # TODO: this can probably be refactored with other error message
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
                        print(city)
                        gettemp(city)

                    except IndexError:
                        message = "Please enter .temp and the name of a city."
                        target = name
                        sendmsg(message, source)

                if message[:5].find('.yaja') != -1:
                    threading.Thread(target=yaja).start()

                if message[:6].find('.radar') != -1:
                    sendmsg("http://www.weather.go.kr/weather/images/rader_integrate.jsp")

                if message[:5].find('noice') != -1:
                    sendmsg("Noice!")

                if message[:8].find('.typhoon') != -1:
                    sendmsg("http://goo.gl/xUa4Bh")

                if message[:9].find('.roulette') != -1:
                    if name == lastshooter:
                        sendmsg(name + "님이 방금 쐈습니다. 다른 유저가 먼저 쏴야 한번 더 쏠 수 있습니다.")
                        pass
                    elif time.time() - oldtime < 59:
                        sendmsg("Please try again later.")
                    else:
                        roulette(name)

                if message.find('hotpot') != -1:
                    print(olddate)
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

                if message.find('fuck me') != -1:
                    sendmsg(".dicecho lenny", "acosbot")

                if message[:5].find('.aqi') != -1:
                    try:
                        keyword = message.split(' ', 1)[1]
                        aqi(keyword)

                    except IndexError:
                        message = "Please enter .aqi and the name of a city or area."
                        target = name
                        sendmsg(message, source)

                if host == namehost and message.strip() == "bye " + botnick:
                    sendmsg("As you wish. :'(")
                    ircsock.send(bytes("QUIT \n", "UTF-8"))
                    ircsock.close()  # broken?
        elif msgcode == "PING":
            ircsock.send(
                bytes("PONG " + ircmsg.split()[1] + "\r\n", "UTF-8"))  # sending back a pong including custom ping code
            print("Sent PONG " + ircmsg.split()[1])

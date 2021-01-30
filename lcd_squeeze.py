#!/usr/bin/python
# Script to display Now playing info on a 16x2 LCD via lcdproc
#Copyright (C) 2016  Pradeep Murthy

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

# to do as of 20160326 
# make it flexible to accommodate 20x4 LCDs
# get player string instead of hardcoding

import subprocess
import urllib
import re
import threading
from time import sleep
import sys
import syslog
import board
import digitalio
import telnetlib
import adafruit_character_lcd.character_lcd as characterlcd
import html
import urllib.parse
from subprocess import Popen, PIPE
from time import sleep
from datetime import datetime

# Modify this if you have a different sized character LCD
lcd_columns = 16
lcd_rows = 2

# compatible with all versions of RPI as of Jan. 2019
# v1 - v3B+
lcd_rs = digitalio.DigitalInOut(board.D22)
lcd_en = digitalio.DigitalInOut(board.D17)
lcd_d4 = digitalio.DigitalInOut(board.D25)
lcd_d5 = digitalio.DigitalInOut(board.D24)
lcd_d6 = digitalio.DigitalInOut(board.D23)
lcd_d7 = digitalio.DigitalInOut(board.D18)


# Initialise the lcd class
lcd = characterlcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6,
                                      lcd_d7, lcd_columns, lcd_rows)

def time_update(myartist,mytitle):
    global songchangeflag
    global pauseflag
    global mode
    curartist=get_metadata("artist")
    curtitle=get_metadata("title")
    if pauseflag == 1 :
        mytimeremaining = 0
    else :
        mydur = float(get_metadata("duration"))
        mytime = float(get_metadata("time"))
        mytimeremaining = int(mydur - mytime)
    while mytimeremaining > 0 :
        if pauseflag == 1 :
            return
        if (myartist == curartist and mytitle == curtitle):
            trmin=int(mytimeremaining/60)
            trsec=mytimeremaining - trmin*60
            if trmin < 10 :
                trmin=" "+str(int(trmin))
            else:
                trmin=str(trmin)
            if trsec < 10 :
                trsec=":0"+str(trsec)
            else:
                trsec=":"+str(trsec)
            lcd.clear()
            lcd.cursor_position(0,1)
            lcd.message = trmin+trsec
            sleep(1)
            mytimeremaining = mytimeremaining - 1
            if (songchangeflag == 1) :
                curartist = get_metadata("artist")
                curtitle = get_metadata("title")
                songchangeflag = 0
        else:
            return
    return

def get_metadata(metadata):
    # metadata: one of artist, title, mode, duration, time. always returns string, even for numbers
    tn = telnetlib.Telnet(host="192.168.0.100", port=9090)
    playerMacAddress = "dc:a6:32:5e:3d:2e"
    command = playerMacAddress + " " + metadata + " ?"
    
    tn.write(command.encode('ascii') + b"\n")
    tn.write(b"exit\n")
    
    result = tn.read_all().decode('utf8').split()
    metadataPosition = result.index(metadata)
    
    if len(result) <= metadataPosition + 1: return ""

    return(urllib.parse.unquote(result[metadataPosition + 1]))

def update_display():
    global artist
    global title
    
    # get data
    artist = get_metadata("artist")
    title = get_metadata("title")

    # set data on LCD
    lcd.clear()
    scroll_it(artist, 0)
    scroll_it(title, 1)
 
    # Call time update
    # t1 = threading.Thread(target=time_update, args=(artist,title,))
    # t1.daemon = True
    # t1.start()

    return

def scroll_it(message, row):
    if len(message) <= 16:
        lcd.cursor_position(0,row)
        lcd.message = message
        return
    lcd.cursor_position(0,row)
    lcd.message = message[0:15]
    sleep(0.25)
    for i in (range(0,len(message) - 14)):
        lcd.cursor_position(0,row)
        lcd.message = message[i: 15+i]  
        sleep(0.25)

    sleep(2)
    lcd.cursor_position(0,row)
    lcd.message = message[0:14] + ".."
    
    return

# looking for an active Ethernet or WiFi device
def find_interface():
    find_device = "ip addr show"
    interface_parse = run_cmd(find_device)
    for line in interface_parse.splitlines():
        if "state UP" in line:
            dev_name = line.split(':')[1]
    return dev_name
 
# find an active IP on the first LIVE network device
def parse_ip():
    find_ip = "ip addr show %s" % interface
    find_ip = "ip addr show %s" % interface
    ip_parse = run_cmd(find_ip)
    for line in ip_parse.splitlines():
        if "inet " in line:
            ip = line.split(' ')[5]
            ip = ip.split('/')[0]
    return ip
 
# run unix shell command, return as ASCII
def run_cmd(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()[0]
    return output.decode('ascii')

#show ip and date time on start
sleep(2)
interface = find_interface()
ip_address = parse_ip()
# date and time
lcd_line_1 = datetime.now().strftime('%b %d  %H:%M:%S\n')
 
# current ip address
lcd_line_2 = "IP " + ip_address

# combine both lines into one update to the display
lcd.message = lcd_line_1 + lcd_line_2

sleep(2)

# Initialize variables
songchangeflag = 0
pauseflag = 0

# find out if the player is playing or stopped
mode=get_metadata("mode")

if mode == "play" :
    pauseflag = 0
    songchangeflag = 0
    update_display()
else :
    pauseflag = 1
    
# Now start main telnet session and listen
tn = telnetlib.Telnet(host="192.168.0.100", port=9090)
   
#p = subprocess.Popen('telnet 127.0.0.1 9090', stdin = subprocess.PIPE, stdout=subprocess.PIPE, stderr = None, shell=True, text=True)
tn.write(b"listen 1\n")

#result = tn.read_eager().decode('utf8').split()
#metadataPosition = result.index("listen 1\n")
while True:
    for line in tn.read_eager().decode('utf8').split():
    #  Some update on the telnet socket. need to find out what happened. So get updated metadata
        line = line.rstrip()
        if not (re.search('Trying', line) or re.search('Connected', line) or re.search('Escape', line) ) :
            newmode=get_metadata('mode')
            if newmode == "play" :
                newartist = get_metadata("artist")
                newtitle = get_metadata("title")
                if mode == "play" : # old and new modes are both play. So maybe new song
                    if ( artist != newartist or title != newtitle) : # defly new song
                        songchangeflag = 1
                        update_display()
                else : # mode was not play. So we got unpaused
                    pauseflag = 0
                    mode = newmode
                    update_display()
            else : # new mode is not play. so we got paused
                pauseflag = 1
                #scr1.set_backlight("off")
                mode = newmode

# clean up on exit
tn.close()
lcd.clear()

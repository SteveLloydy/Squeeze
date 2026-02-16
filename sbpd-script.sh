#!/bin/sh

# start pigpiod daemon
pigpiod -t 0 -f -l -s 10

# wait for pigpiod to initialize - indicated by 'pigs t' exit code of zero

count=10 # approx time limit in seconds
while ! pigs t >/dev/null 2>&1 ; do
	if [ $((count--)) -le 0 ]; then
		printf "\npigpiod failed to initialize within time limit\n"
		exit 1
	fi
#	printf "\nWaiting for pigpiod to initialize\n"
	sleep 1
done
printf "\npigpiod is running\n"

# load uinput module - required to be able to send keystrokes
# then set the permission to group writable, so you don't need to run sbpd with root permissions
sudo modprobe uinput
sudo chmod g+w /dev/uinput

# The full list of Jivelite key commands can be found here:
# https://github.com/ralph-irving/tcz-lirc/blob/master/jivekeys.csv

# button 1						# button-section, defines the GPIO and key-commands
SW1=5 							# GPIO (BCM, not Board)
SH1=KEY:KEY_1					# key-command for SHORT press (here: preset 1)
LO1=KEY:KEY_2					# key-command for LONG press (here: preset 2)
LMS1=250 						# milliseconds for long press

# button 2
SW2=6
SH2=KEY:KEY_3
LO2=KEY:KEY_4
LMS2=250

# button 3
SW3=13
SH3=KEY:KEY_5
LO3=KEY:KEY_6
LMS3=250

# button rotary 1
SW4=17
SH4=KEY:KEY_SPACE				# key-command for SHORT press(play/pause)
LO4=KEY:KEY_LEFTBRACE			# key-command for LONG press(special menu)
LMS4=250

# button rotary 2
SW5=12
SH5=KEY:KEY_ENTER				# key-command for SHORT press(enter, OK)
LO5=KEY:KEY_ESC					# key-command for LONG press(back)
LMS5=250

# CMD="sbpd -v -f /home/tc/sbpd_commands.cfg \
#CMD="sbpd -v \
#b,$SW1,$SH1,2,0,$LO1,$LMS1 \	# b=button, $SW1=switchnumber of button-section
#b,$SW2,$SH2,2,0,$LO2,$LMS2 \
#b,$SW3,$SH3,2,0,$LO3,$LMS3 \
#b,$SW4,$SH4,2,0,$LO4,$LMS4 \
#b,$SW5,$SH5,2,0,$LO5,$LMS5 \
#e,22,27,VOLU,2 \				# e=encoder, 22 and 27 are GPIO
#e,23,24,KEY:KEY_UP-KEY_DOWN,4 "	# e=encoder, 23 and 24 are GPIO

CMD = "sudo spd -v e,23,24,VOLU,2 b,25,KEY:KEY_SPACE,2,0,KEY:KEY_LEFTBRACE,250"	

echo $CMD
$CMD > /dev/null 2>&1 &

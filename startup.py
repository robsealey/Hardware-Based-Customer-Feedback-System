import RPi.GPIO as GPIO
import time
import datetime
import shutil
import os

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, LCD_FONT, CP437_FONT

GPIO.setmode(GPIO.BCM)

GPIO.setup(18, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(23, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(24, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(25, GPIO.IN, pull_up_down = GPIO.PUD_UP)

serial = spi(port = 0, device = 0, gpio = noop())
device = max7219(serial, cascaded = 4, block_orientation = -90, rotate = 0) 

def led(msg):
    show_message(device, msg, fill = "white", font = proportional(LCD_FONT))
def double_check():
    msg = "Press Red again to delete database or Green to start normally"
    led(msg)
    try:
        while True:
            pin1 = GPIO.input(18)
            pin3 = GPIO.input(24)

            if pin3 == False:
		msg = "Starting normally"
        	led(msg)
                os.system("python survey.py")
                time.sleep(0.5)

            elif pin1 == False:
		msg = "Delete confirmed"
        	led(msg)
                delete_database()
    except KeyboardInterrupt:
        main()

def delete_database():
	msg = "Deleting database"
	led(msg)
	now = datetime.datetime.now()
	date = now.strftime("%Y%m%d_%H%M%S")	
	source_file = "feedback.db"
	dest = str(date) + '.db'	
	shutil.copy(source_file, dest)
	os.remove("feedback.db")
	os.system("python survey.py")	
	
def startup_mode():
    global id
    print('\nUSER MODE\n\nPress "Ctrl+C" to quit.\n\n')
    try:
        while True:
            pin1 = GPIO.input(18)
            pin2 = GPIO.input(23)
            pin3 = GPIO.input(24)
	    pin4 = GPIO.input(25)

            if pin3 == False:
          	os.system("python survey.py")      
		time.sleep(0.5)

	    elif pin1 == False:
		double_check()
                time.sleep(0.5)
				
    except KeyboardInterrupt:
        main()

def main():
	msg = "Press Green to start or Red to delete database then start"
        led(msg)
        startup_mode()

if __name__ == "__main__":
    main()

import RPi.GPIO as GPIO
import time
import sqlite3

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, LCD_FONT, CP437_FONT

GPIO.setmode(GPIO.BCM)

GPIO.setup(18, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(23, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(24, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(25, GPIO.IN, pull_up_down = GPIO.PUD_UP)

conn = sqlite3.connect('feedback.db')
c = conn.cursor()

try:
    c.execute('CREATE TABLE feedback(id INT PRIMARY KEY, cust_feedback TEXT, time DATETIME)')
    id = 1

except:
    c.execute('SELECT MAX(id) FROM feedback')
    all_rows = c.fetchall()
    for row in all_rows:
        id = int(row[0]) + 1

serial = spi(port = 0, device = 0, gpio = noop())
device = max7219(serial, cascaded = 4, block_orientation = -90, rotate = 0) 

def db_entry(val):
    currTime = time.strftime("%d-%m-%Y %H:%M:%S", time.gmtime())
    print(id, val, currTime)
    c.execute('INSERT INTO feedback VALUES(?, ?, ?)',(id, val, currTime))
    conn.commit()

def led(msg):
    show_message(device, msg, fill = "white", font = proportional(LCD_FONT), scroll_delay = 0.1)

def emoji(msg):
    device = max7219(serial, cascaded = 4, block_orientation = -90, rotate = 0)
    time.sleep(0.1)
    show_message(device, msg, fill = "white", font = proportional(LCD_FONT))

def feedback_mode():
    global id
    print('\nUSER MODE\n\nPress "Ctrl+C" to quit.\n\n')
    try:
        while True:
            pin1 = GPIO.input(18)
            pin2 = GPIO.input(23)
            pin3 = GPIO.input(24)
	    pin4 = GPIO.input(25)

            if pin1 == False:
                db_entry("bad")
                time.sleep(0.5)
                id += 1

            elif pin2 == False:
                db_entry("ok")
                time.sleep(0.5)
                id += 1
			
	    elif pin3 == False:
                db_entry("good")
                time.sleep(0.5)
                id += 1
				
            elif pin4 == False:
                c.execute("SELECT SUM(CASE WHEN cust_feedback = 'good' THEN 1 END), SUM(CASE WHEN cust_feedback = 'ok' THEN 1 END), SUM(CASE WHEN cust_feedback = 'bad' THEN 1 END) FROM feedback")
                all_rows = c.fetchall()
                for row in all_rows:
                    good = str(row[0])
		    ok = str(row[1])
 		    bad = str(row[2])
                msg = "Good: "+good+"   Ok: "+ok+ "   Bad: "+bad
                led(msg)

    except KeyboardInterrupt:
        print("\nExiting user mode.\n")
        mode()

def viewRatio():
    c.execute("SELECT SUM(CASE WHEN cust_feedback = 'good' THEN 1 END) AS Good_Feedback, SUM(CASE WHEN cust_feedback = 'ok' THEN 1 END) AS Ok_Feedback, SUM(CASE WHEN cust_feedback = 'bad' THEN 1 END) AS Bad_Feedback FROM feedback")
    all_rows = c.fetchall()
    print("\nGood Feedback \t Ok Feedback \t Bad Feedback\n")
    for row in all_rows:
        print('\t {0} \t\t {1} \t\t {2}'.format(row[0], row[1], row[2]))
    viewDB()

def viewDB():
    print("\nFEEDBACK ANALYSIS MODE\n\n\t1 -> View entire DB\n\t2 -> Feedback Summary\n\t3 -> Exit")
    i = input("\nEnter your choice: ")

    if i == 1:
        c.execute('SELECT * FROM feedback')
        all_rows = c.fetchall()
        print("\nID \t Feedback \t Date & Time\n")
        for row in all_rows:
            print('{0} \t {1} \t\t {2} '.format(row[0], row[1], row[2]))
        viewDB()

    elif i == 2:
        viewRatio()

    elif i == 3:
        mode()

    else:
        print("Invalid Option. Try again!")
        viewDB()

def mode():
    print("\nMAIN MENU\n\n\t1 -> User Mode\n\t2 -> Feedback Analysis Mode \n\t3 -> Exit")
    i = input("\nEnter your choice: ")
    if i == 1:
        feedback_mode()
    elif i == 2:
        viewDB()
    elif i == 3:
        quit()
    else:
        print("Invalid option. Try again!")
        mode()

def main():
	msg = "Ready"
        led(msg)
        feedback_mode()

if __name__ == "__main__":
    main()

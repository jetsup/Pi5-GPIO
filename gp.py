from RPi import GPIO
from time import sleep
from random import choice

LED_ONE = 14
LED_TWO = 15
LED_THREE = 18

TIME_DELAY = 0.1

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_ONE, GPIO.OUT)
GPIO.setup(LED_TWO, GPIO.OUT)
GPIO.setup(LED_THREE, GPIO.OUT)

while True:
    random_pin = choice([LED_ONE, LED_TWO, LED_THREE])
    try:
        GPIO.output(random_pin, GPIO.HIGH)
        print("Pin ON")
        sleep(TIME_DELAY)
        GPIO.output(random_pin, GPIO.LOW)
        print("Pin OFF")
        sleep(TIME_DELAY)
    except KeyboardInterrupt as e:
        print(f"Quitting...")
        break

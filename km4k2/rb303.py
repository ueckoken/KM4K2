import time

import wiringpi

wiringpi.wiringPiSetupGpio()
wiringpi.pwmSetMode(wiringpi.PWM_MODE_MS)
wiringpi.pwmSetRange(2000)
wiringpi.pwmSetClock(192)


def servo(angle):
    angle = int(angle * 200 / 180 + 50)
    wiringpi.pwmWrite(12, angle)
def servo_start():
    wiringpi.pinMode(12, wiringpi.GPIO.PWM_OUTPUT)
def servo_end():
    wiringpi.pinMode(12, wiringpi.GPIO.INPUT)

def unlock():
    servo_start()
    servo(180)
    time.sleep(0.4)
    servo(90)
    time.sleep(0.4)
    servo_end()


def lock():
    servo_start()
    servo(0)
    time.sleep(0.4)
    servo(90)
    time.sleep(0.4)
    servo_end()


if __name__ == "__main__":
    while True:
        angle = int(input())
        servo(angle)
        print("Angle: " + str(angle))

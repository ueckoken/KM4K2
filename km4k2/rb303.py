import time
from logging import getLogger

import wiringpi

logger = getLogger(__name__)


wiringpi.wiringPiSetupGpio()
wiringpi.pinMode(12, wiringpi.GPIO.PWM_OUTPUT)
wiringpi.pwmSetMode(wiringpi.PWM_MODE_MS)
wiringpi.pwmSetRange(2000)
wiringpi.pwmSetClock(192)


def servo(angle):
    angle = int(angle * 200 / 180 + 50)
    wiringpi.pwmWrite(12, angle)


def unlock():
    servo(180)
    time.sleep(1)
    servo(90)


def lock():
    servo(0)
    time.sleep(1)
    servo(90)


def reset():
    servo(90)


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.DEBUG)
    while True:
        angle = int(input())
        servo(angle)
        logger.debug("Angle: %d", angle)

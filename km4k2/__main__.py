import os

import redis
from RPi import GPIO

import km4k2.rb303 as servo
from km4k2.card_sdk import CardSDK
from km4k2.km4k import start_system


def main():
    isopen = False
    okled_pin = 19
    ngled_pin = 26

    # Redisに接続
    conn = redis.StrictRedis(
        host=os.environ["REDIS_HOST"],
        port=os.environ["REDIS_PORT"],
        db=os.environ["REDIS_DB"],
    )

    servo.reset()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(okled_pin, GPIO.OUT)
    GPIO.setup(ngled_pin, GPIO.OUT)

    card = CardSDK("https://card.ueckoken.club", os.environ["API_KEY"])

    try:
        print("Welcome to Koken Kagi System")
        start_system(isopen, okled_pin, ngled_pin, conn, card)
    except Exception as e:  # noqa: BLE001
        print("An error has occured!")
        print(e)


if __name__ == "__main__":
    main()

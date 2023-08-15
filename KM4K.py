#!/usr/bin/python3

import binascii
import os
import sys
import time

import nfc
import redis
from RPi import GPIO

import rb303 as servo
from card_sdk import CardSDK

suica = nfc.clf.RemoteTarget("212F")
suica.sensf_req = bytearray.fromhex("0000030000")

# Redisに接続
conn = redis.StrictRedis(
    host=os.environ["REDIS_HOST"],
    port=os.environ["REDIS_PORT"],
    db=os.environ["REDIS_DB"],
)


def read_nfc():
    while True:
        with nfc.ContactlessFrontend("usb") as clf:
            target = clf.sense(suica, iterations=3, interval=1.0)
            while target:
                tag = nfc.tag.activate(clf, target)
                tag.sys = 3
                return binascii.hexlify(tag.idm)


def start_system(isopen, okled_pin, ngled_pin, card: CardSDK):
    while True:
        idm = read_nfc()
        if idm:
            verified = False
            # Redisに登録されているか確認
            if conn.get(idm.decode()) is not None:
                verified = True
            else:
                # Card Managerで登録されているか確認
                is_registered_sso = card.verify(idm.decode())
                if is_registered_sso:
                    # 有効期限を1週間でRedisに保存
                    conn.set(idm.decode(), 60 * 60 * 24 * 7)
                    verified = True
            if verified:
                print("Registered (idm:" + idm.decode() + ")")

                GPIO.output(okled_pin, GPIO.HIGH)
                time.sleep(0.1)
                GPIO.output(okled_pin, GPIO.LOW)
                time.sleep(0.1)
                GPIO.output(okled_pin, GPIO.HIGH)
                time.sleep(0.1)
                GPIO.output(okled_pin, GPIO.LOW)

                if not isopen:
                    servo.unlock()
                    isopen = not isopen
                    print("open")
                else:
                    servo.lock()
                    isopen = not isopen
                    print("lock")

                time.sleep(1.7)
            else:
                print("Unregistered (idm:" + idm.decode() + ")")
                GPIO.output(ngled_pin, GPIO.HIGH)
                time.sleep(0.1)
                GPIO.output(ngled_pin, GPIO.LOW)
                time.sleep(0.1)
                GPIO.output(ngled_pin, GPIO.HIGH)
                time.sleep(0.1)
                GPIO.output(ngled_pin, GPIO.LOW)
                time.sleep(1.7)


def main(_):
    isopen = False
    okled_pin = 19
    ngled_pin = 26

    servo.reset()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(okled_pin, GPIO.OUT)
    GPIO.setup(ngled_pin, GPIO.OUT)

    card = CardSDK("https://card.ueckoken.club", os.environ["API_KEY"])

    try:
        print("Welcome to Koken Kagi System")
        start_system(isopen, okled_pin, ngled_pin, card)
    except Exception as e:  # noqa: BLE001
        print("An error has occured!")
        print(e)


if __name__ == "__main__":
    main(sys.argv)

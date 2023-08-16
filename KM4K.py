#!/usr/bin/python3

import nfc
import binascii
import sys
import RPi.GPIO as GPIO
import time
import rb303 as servo
import requests
import json
import os
import redis

suica = nfc.clf.RemoteTarget("212F")
suica.sensf_req = bytearray.fromhex("0000030000")

# Redisに接続
conn = redis.StrictRedis(
    host=os.environ["REDIS_HOST"],
    port=os.environ["REDIS_PORT"],
    db=os.environ["REDIS_DB"],
)


# 有効期間1週間
CACHE_EXPIRES_SECONDS = 60 * 60 * 24 * 7


def read_nfc():
    while True:
        with nfc.ContactlessFrontend("usb") as clf:
            target = clf.sense(suica, iterations=3, interval=1.0)
            while target:
                tag = nfc.tag.activate(clf, target)
                tag.sys = 3
                idm = binascii.hexlify(tag.idm)
                return idm


def check_card_manager(idm):
    url = "https://card.ueckoken.club/api/card/verify"
    payload = json.dumps({"idm": idm})
    headers = {"X-Api-Key": os.environ["API_KEY"], "Content-Type": "application/json"}
    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        status = json.loads(response.text)
        if status["verified"] is not None and status["verified"]:
            return True
        return False
    except Exception as e:
        print(e)
        return False


def start_system(isopen, okled_pin, ngled_pin):
    while True:
        idm = read_nfc()
        if idm:
            verified = False
            # Redisに登録されているか確認
            if conn.get(idm.decode()) is not None:
                verified = True
            else:
                # Card Managerで登録されているか確認
                isRegisteredSSO = check_card_manager(idm.decode())
                if isRegisteredSSO:
                    # 有効期限付きでRedisに保存
                    # 値は今のところ使わないので適当に1にしておいた
                    conn.set(idm.decode(), 1, ex=CACHE_EXPIRES_SECONDS)
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
                    servo.open()
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


def main(argv):
    isopen = False
    okled_pin = 19
    ngled_pin = 26

    servo.reset()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(okled_pin, GPIO.OUT)
    GPIO.setup(ngled_pin, GPIO.OUT)

    try:
        print("Welcome to Koken Kagi System")
        start_system(isopen, okled_pin, ngled_pin)
    except Exception as e:
        print("An error has occured!")
        print(e)


if __name__ == "__main__":
    main(sys.argv)

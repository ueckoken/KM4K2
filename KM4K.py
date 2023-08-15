#!/usr/bin/python3

import binascii
import json
import os
import sys
import time

import nfc
import redis
import requests
from RPi import GPIO

import rb303 as servo

suica = nfc.clf.RemoteTarget("212F")
suica.sensf_req = bytearray.fromhex("0000030000")


def read_nfc():
    while True:
        with nfc.ContactlessFrontend("usb") as clf:
            target = clf.sense(suica, iterations=3, interval=1.0)
            while target:
                tag = nfc.tag.activate(clf, target)
                tag.sys = 3
                return binascii.hexlify(tag.idm)


def check_card_manager(idm):
    url = "https://card.ueckoken.club/api/card/verify"
    payload = json.dumps({"idm": idm})
    headers = {"X-Api-Key": os.environ["API_KEY"], "Content-Type": "application/json"}
    response = requests.request("GET", url, headers=headers, data=payload)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(e)
        return False

    try:
        status = response.json()
    except requests.exceptions.JSONDecodeError as e:
        print(e)
        return False

    return status["verified"] is not None and status["verified"]


def start_system(isopen, okled_pin, ngled_pin, cache: redis.Redis):
    while True:
        idm = read_nfc()
        if idm:
            verified = False
            # Redisに登録されているか確認
            if cache.get(idm.decode()) is not None:
                verified = True
            else:
                # Card Managerで登録されているか確認
                is_registered_sso = check_card_manager(idm.decode())
                if is_registered_sso:
                    # 有効期限を1週間でRedisに保存
                    cache.set(idm.decode(), 60 * 60 * 24 * 7)
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

    try:
        print("Welcome to Koken Kagi System")
        start_system(isopen, okled_pin, ngled_pin, conn)
    except Exception as e:  # noqa: BLE001
        print("An error has occured!")
        print(e)


if __name__ == "__main__":
    main(sys.argv)

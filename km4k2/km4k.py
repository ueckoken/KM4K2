import binascii
import time

import nfc
import redis
from RPi import GPIO

import km4k2.rb303 as servo
from km4k2.card_sdk import CardSDK

suica = nfc.clf.RemoteTarget("212F")
suica.sensf_req = bytearray.fromhex("0000030000")


# 有効期間1週間
CACHE_EXPIRES_SECONDS = 60 * 60 * 24 * 7


def read_nfc():
    while True:
        with nfc.ContactlessFrontend("usb") as clf:
            target = clf.sense(suica, iterations=3, interval=1.0)
            while target:
                tag = nfc.tag.activate(clf, target)
                tag.sys = 3
                return binascii.hexlify(tag.idm)


def start_system(isopen, okled_pin, ngled_pin, cache: redis.Redis, card: CardSDK):
    while True:
        idm = read_nfc()
        if idm:
            verified = False
            # Redisに登録されているか確認
            if cache.get(idm.decode()) is not None:
                verified = True
            else:
                # Card Managerで登録されているか確認
                is_registered_sso = card.verify(idm.decode())
                if is_registered_sso:
                    # 有効期限付きでRedisに保存
                    # 値は今のところ使わないので適当に1にしておいた
                    cache.set(idm.decode(), 1, ex=CACHE_EXPIRES_SECONDS)
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

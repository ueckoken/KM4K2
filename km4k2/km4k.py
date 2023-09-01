import binascii
import time
from logging import getLogger

import nfc
from RPi import GPIO

import km4k2.rb303 as servo
from km4k2.card_verifier_interface import CardVerifierInterface

logger = getLogger(__name__)

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


def start_system(isopen, okled_pin, ngled_pin, verifier: CardVerifierInterface):
    while True:
        idm = read_nfc()
        if idm:
            verified = verifier.verify(idm.decode())
            if verified:
                logger.info("Registered (idm: %s)", idm.decode())

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
                    logger.info("open")
                else:
                    servo.lock()
                    isopen = not isopen
                    logger.info("lock")

                time.sleep(1.7)
            else:
                logger.info("Unregistered (idm: %s)", idm.decode())
                GPIO.output(ngled_pin, GPIO.HIGH)
                time.sleep(0.1)
                GPIO.output(ngled_pin, GPIO.LOW)
                time.sleep(0.1)
                GPIO.output(ngled_pin, GPIO.HIGH)
                time.sleep(0.1)
                GPIO.output(ngled_pin, GPIO.LOW)
                time.sleep(1.7)

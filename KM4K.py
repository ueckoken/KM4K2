#!/usr/bin/python3

import nfc
import binascii
import sqlite3
import sys
import RPi.GPIO as GPIO
import time
import rb303 as servo

suica = nfc.clf.RemoteTarget("212F")
suica.sensf_req = bytearray.fromhex("0000030000")

mode = 2


def sql_add(cur, name, idm):
    cur.execute("INSERT INTO users (name, idm) VALUES (?, ?)", (name, idm))


def sql_del(res):
    for row in res:
        print(row)


def add_nfc(cur):
    assert mode == 0, "mode is not 0"
    name = input("name> ")
    print("Touch your Suica")
    idm = read_nfc()
    if idm:
        cur.execute("SELECT * FROM users WHERE idm=?", (idm,))
        res = cur.fetchall()
        if len(res) > 0:
            print("This key has already registered.")
        else:
            sql_add(cur, name, idm)
            print("Registered (idm:" + idm.decode() + ")")


def delete_nfc(cur):
    assert mode == 1, "mode is not 1"
    name = input("name> ")
    cur.execute("SELECT * FROM users WHERE name=?", (name,))
    res = cur.fetchall()
    if len(res) == 0:
        print("Unregistered name:" + name)
    else:
        # sql_del(res)
        cur.execute("DELETE FROM users WHERE name=?", (name,))
        print("Deleted (name:" + name + ")")


def read_nfc():
    while True:
        with nfc.ContactlessFrontend("usb") as clf:
            target = clf.sense(suica, iterations=3, interval=1.0)
            while target:
                tag = nfc.tag.activate(clf, target)
                tag.sys = 3
                idm = binascii.hexlify(tag.idm)
                return idm


def start_system(cur, isopen, okled_pin, ngled_pin):
    while True:
        idm = read_nfc()
        if idm:
            cur.execute("SELECT * FROM users WHERE idm=?", (idm,))
            res = cur.fetchall()
            if len(res) > 0:
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
    global mode
    dbname = "database.db"
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    isopen = False
    okled_pin = 19
    ngled_pin = 26

    servo.reset()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(okled_pin, GPIO.OUT)
    GPIO.setup(ngled_pin, GPIO.OUT)

    if len(argv) == 2:
        mode = int(argv[1])

    try:
        cur.execute(
            "CREATE TABLE IF NOT EXISTS users (name TEXT NOT NULL, idm BLOB NOT NULL, date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
        )
        if mode == 0:
            print("Add User")
            add_nfc(cur)
        elif mode == 1:
            print("Delete User")
            delete_nfc(cur)
        else:
            print("Welcome to Koken Kagi System")
            start_system(cur, isopen, okled_pin, ngled_pin)
    except Exception as e:
        print("An error has occured!")
        print(e)
    finally:
        conn.commit()
        conn.close()


if __name__ == "__main__":
    main(sys.argv)

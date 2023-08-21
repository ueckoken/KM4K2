import os
from datetime import timedelta

import redis
from RPi import GPIO

import km4k2.rb303 as servo
from km4k2.card_sdk import CardSDK
from km4k2.km4k import start_system
from km4k2.redis_cache_aside_card_verifier import RedisCacheAsideCardVerifier


def main():
    isopen = False
    okled_pin = 19
    ngled_pin = 26
    # 有効期間1週間
    cache_expires_delta = timedelta(weeks=1)

    # Redisに接続
    conn = redis.StrictRedis(
        host=os.environ["REDIS_HOST"],
        port=os.environ["REDIS_PORT"],
        db=os.environ["REDIS_DB"],
    )
    api_verifier = CardSDK("https://card.ueckoken.club", os.environ["API_KEY"])
    redis_cached_api_verifier = RedisCacheAsideCardVerifier(
        api_verifier,
        conn,
        cache_expires_delta,
    )

    servo.reset()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(okled_pin, GPIO.OUT)
    GPIO.setup(ngled_pin, GPIO.OUT)

    try:
        print("Welcome to Koken Kagi System")
        start_system(isopen, okled_pin, ngled_pin, redis_cached_api_verifier)
    except Exception as e:  # noqa: BLE001
        print("An error has occured!")
        print(e)


if __name__ == "__main__":
    main()

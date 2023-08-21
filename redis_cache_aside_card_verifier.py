from datetime import timedelta

from redis import Redis

from card_verifier_interface import CardVerifierInterface


class RedisCacheAsideCardVerifier:
    verifier: CardVerifierInterface
    cache: Redis
    expire_in: timedelta

    def __init__(
        self,
        verifier: CardVerifierInterface,
        cache: Redis,
        expire_in: timedelta,
    ):
        super().__init__()
        self.verifier = verifier
        self.cache = cache
        self.expire_in = expire_in

    def verify(self, idm: str) -> bool:
        # Redisに登録されているか確認
        if self.cache.get(idm) is not None:
            return True

        verified = self.verifier.verify(idm)
        if not verified:
            return False

        # 有効期限付きでRedisに保存
        # 値は今のところ使わないので適当に1にしておいた
        self.cache.set(idm, 1, ex=self.expire_in)
        return True

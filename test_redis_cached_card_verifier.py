# ruff: noqa: S101
import os
import time
from unittest import TestCase
from unittest.mock import create_autospec

from redis import StrictRedis

from card_verifier_interface import CardVerifierInterface
from redis_cache_aside_card_verifier import RedisCacheAsideCardVerifier


class TestRedisCachedCardVerifier(TestCase):
    def setUp(self):
        super().setUp()
        self.cache = StrictRedis(
            host=os.environ["REDIS_HOST"],
            port=os.environ["REDIS_PORT"],
            db=os.environ["REDIS_DB"],
        )
        self.verifier = create_autospec(CardVerifierInterface)
        self.cached_verifier = RedisCacheAsideCardVerifier(
            self.verifier,
            self.cache,
            5,
        )

    def tearDown(self) -> None:
        super().tearDown()
        self.cache.flushdb()

    def test_cache_miss_verified(self):
        self.verifier.verify.return_value = True
        self.assertTrue(self.cached_verifier.verify("345678"))
        self.verifier.verify.assert_called_once()

    def test_cache_miss_invalid(self):
        self.verifier.verify.return_value = False
        self.assertFalse(self.cached_verifier.verify("345678"))
        self.verifier.verify.assert_called_once()

    def test_cache_hit_verified(self):
        self.verifier.verify.return_value = True
        self.cached_verifier.verify("345678")  # init cache
        self.verifier.verify.assert_called_once()  # called first
        self.assertTrue(self.cached_verifier.verify("345678"))
        self.verifier.verify.assert_called_once()  # not called again

    def test_cache_hit_invalid(self):
        self.verifier.verify.return_value = False
        self.cached_verifier.verify("345678")  # init cache
        self.verifier.verify.assert_called_once()  # called first
        self.assertFalse(self.cached_verifier.verify("345678"))
        self.assertEqual(self.verifier.verify.call_count, 2)  # called again

    def test_cache_expire(self):
        self.verifier.verify.return_value = True
        self.cached_verifier.verify("345678")  # init cache
        self.verifier.verify.assert_called_once()  # called first
        time.sleep(self.cached_verifier.expire_in)  # wait for expiration
        self.assertTrue(self.cached_verifier.verify("345678"))
        self.assertEqual(self.verifier.verify.call_count, 2)  # called again

    def test_obsoleted_cache_hit(self):
        self.verifier.verify.return_value = True
        self.cached_verifier.verify("345678")  # init cache
        self.verifier.verify.return_value = False  # changes
        self.assertTrue(
            self.cached_verifier.verify("345678"),
        )  # still returns obsoleted result

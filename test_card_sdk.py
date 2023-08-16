# ruff: noqa: S101
from unittest import TestCase

import requests_mock

from card_sdk import CardSDK


class TestCardSDK(TestCase):
    def test_verify_invalid_api_key(self):
        card = CardSDK("https://card.ueckoken.club", "dummy_api_key")

        with requests_mock.Mocker() as m:
            m.get(
                "https://card.ueckoken.club/api/card/verify",
                status_code=401,
                reason="Unauthorized",
                json={"error": "Unauthorized"},
            )

            self.assertFalse(card.verify("dummy_idm"))

    def test_verify_invalid_request(self):
        card = CardSDK("https://card.ueckoken.club", "dummy_api_key")

        with requests_mock.Mocker() as m:
            m.get(
                "https://card.ueckoken.club/api/card/verify",
                status_code=400,
                reason="Bad Request",
                json={"error": "Bad request"},
            )

            self.assertFalse(card.verify("dummy_idm"))

    def test_verify_does_not_exist(self):
        card = CardSDK("https://card.ueckoken.club", "dummy_api_key")

        with requests_mock.Mocker() as m:
            m.get(
                "https://card.ueckoken.club/api/card/verify",
                status_code=404,
                reason="Not Found",
                json={"error": "Not found"},
            )

            self.assertFalse(card.verify("dummy_idm"))

    def test_verify_forbidden(self):
        card = CardSDK("https://card.ueckoken.club", "dummy_api_key")

        with requests_mock.Mocker() as m:
            m.get(
                "https://card.ueckoken.club/api/card/verify",
                status_code=403,
                reason="Forbidden",
                json={"error": "Forbidden"},
            )

            self.assertFalse(card.verify("dummy_idm"))

    def test_verify_verified(self):
        card = CardSDK("https://card.ueckoken.club", "dummy_api_key")

        with requests_mock.Mocker() as m:
            m.get(
                "https://card.ueckoken.club/api/card/verify",
                status_code=200,
                reason="OK",
                json={"verified": True},
            )

            self.assertTrue(card.verify("dummy_idm"))

# ruff: noqa: S101
import contextlib
import os
from unittest import TestCase
from unittest.mock import Mock, patch

import requests_mock
from redis import StrictRedis

rpi_mock = Mock()
nfc_mock = Mock()
wiringpi_mock = Mock()


@patch.dict(
    "sys.modules",
    {
        "RPi": rpi_mock,
        "RPi.GPIO": rpi_mock.GPIO,
        "nfc": nfc_mock,
        "wiringpi": wiringpi_mock,
    },
)
class TestKM4K(TestCase):
    def setUp(self):
        self.conn = StrictRedis(
            host=os.environ["REDIS_HOST"],
            port=os.environ["REDIS_PORT"],
            db=os.environ["REDIS_DB"],
        )

    def tearDown(self):
        self.conn.flushdb()

    def test_check_card_manager_fail_without_api_key(self):
        from KM4K import check_card_manager

        with self.assertRaises(KeyError):
            check_card_manager("dummy")

    @patch.dict(
        "os.environ",
        {
            "API_KEY": "dummy",
        },
    )
    def test_check_card_manager_invalid_api_key(self):
        with requests_mock.Mocker() as m:
            m.get(
                "https://card.ueckoken.club/api/card/verify",
                status_code=401,
                reason="Unauthorized",
                json={"error": "Unauthorized"},
            )

            from KM4K import check_card_manager

            self.assertFalse(check_card_manager("dummy"))

    @patch.dict(
        "os.environ",
        {
            "API_KEY": "dummy",
        },
    )
    def test_check_card_manager_invalid(self):
        with requests_mock.Mocker() as m:
            m.get(
                "https://card.ueckoken.club/api/card/verify",
                status_code=400,
                reason="Bad Request",
                json={"error": "Bad request"},
            )

            from KM4K import check_card_manager

            self.assertFalse(check_card_manager("dummy"))

    @patch.dict(
        "os.environ",
        {
            "API_KEY": "dummy",
        },
    )
    def test_check_card_manager_does_not_exist(self):
        with requests_mock.Mocker() as m:
            m.get(
                "https://card.ueckoken.club/api/card/verify",
                status_code=404,
                reason="Not Found",
                json={"error": "Not found"},
            )

            from KM4K import check_card_manager

            self.assertFalse(check_card_manager("dummy"))

    @patch.dict(
        "os.environ",
        {
            "API_KEY": "dummy",
        },
    )
    def test_check_card_manager_forbidden(self):
        with requests_mock.Mocker() as m:
            m.get(
                "https://card.ueckoken.club/api/card/verify",
                status_code=403,
                reason="Forbidden",
                json={"error": "Forbidden"},
            )

            from KM4K import check_card_manager

            self.assertFalse(check_card_manager("dummy"))

    @patch.dict(
        "os.environ",
        {
            "API_KEY": "dummy",
        },
    )
    def test_check_card_manager_verified(self):
        with requests_mock.Mocker() as m:
            m.get(
                "https://card.ueckoken.club/api/card/verify",
                status_code=200,
                reason="OK",
                json={"verified": True},
            )

            from KM4K import check_card_manager

            self.assertTrue(check_card_manager("dummy"))

    @patch("KM4K.servo", autospec=True)
    @patch("KM4K.read_nfc", side_effect=[b"345678", InterruptedError])
    @patch("KM4K.check_card_manager", return_value=False)
    def test_start_system_with_closed_door_and_unregistered_card(
        self,
        mocked_check_card_manager,  # noqa: ARG002
        mocked_read_nfc,  # noqa: ARG002
        mocked_servo,
    ):
        from KM4K import start_system

        with contextlib.suppress(InterruptedError):
            start_system(isopen=False, okled_pin=19, ngled_pin=26)

        mocked_servo.open.assert_not_called()
        mocked_servo.lock.assert_not_called()

    @patch("KM4K.servo", autospec=True)
    @patch("KM4K.read_nfc", side_effect=[b"345678", InterruptedError])
    @patch("KM4K.check_card_manager", return_value=True)
    def test_start_system_with_closed_door_and_registered_card(
        self,
        mocked_check_card_manager,  # noqa: ARG002
        mocked_read_nfc,  # noqa: ARG002
        mocked_servo,
    ):
        from KM4K import start_system

        with contextlib.suppress(InterruptedError):
            start_system(isopen=False, okled_pin=19, ngled_pin=26)

        mocked_servo.open.assert_called_once()
        mocked_servo.lock.assert_not_called()

    @patch("KM4K.servo", autospec=True)
    @patch("KM4K.read_nfc", side_effect=[b"345678", InterruptedError])
    @patch("KM4K.check_card_manager", return_value=False)
    def test_start_system_with_open_door_and_unregistered_card(
        self,
        mocked_check_card_manager,  # noqa: ARG002
        mocked_read_nfc,  # noqa: ARG002
        mocked_servo,
    ):
        from KM4K import start_system

        with contextlib.suppress(InterruptedError):
            start_system(isopen=True, okled_pin=19, ngled_pin=26)

        mocked_servo.open.assert_not_called()
        mocked_servo.lock.assert_not_called()

    @patch("KM4K.servo", autospec=True)
    @patch("KM4K.read_nfc", side_effect=[b"345678", InterruptedError])
    @patch("KM4K.check_card_manager", return_value=True)
    def test_start_system_with_open_door_and_registered_card(
        self,
        mocked_check_card_manager,  # noqa: ARG002
        mocked_read_nfc,  # noqa: ARG002
        mocked_servo,
    ):
        from KM4K import start_system

        with contextlib.suppress(InterruptedError):
            start_system(isopen=True, okled_pin=19, ngled_pin=26)

        mocked_servo.open.assert_not_called()
        mocked_servo.lock.assert_called_once()

    @patch("KM4K.servo", autospec=True)
    @patch("KM4K.read_nfc", side_effect=[b"345678", b"345678", InterruptedError])
    @patch("KM4K.check_card_manager", return_value=True)
    def test_start_system_with_redis_cache(
        self,
        mocked_check_card_manager,
        mocked_read_nfc,  # noqa: ARG002
        mocked_servo,
    ):
        from KM4K import start_system

        with contextlib.suppress(InterruptedError):
            start_system(isopen=True, okled_pin=19, ngled_pin=26)

        mocked_servo.open.assert_called_once()
        mocked_servo.lock.assert_called_once()
        mocked_check_card_manager.assert_called_once()

    @patch("KM4K.servo", autospec=True)
    @patch("KM4K.read_nfc", side_effect=[b"456789", b"456789", InterruptedError])
    @patch("KM4K.check_card_manager", side_effect=[True, False])
    def test_start_system_unregistered_card_with_redis_cache(
        self,
        mocked_check_card_manager,
        mocked_read_nfc,  # noqa: ARG002
        mocked_servo,
    ):
        from KM4K import start_system

        with contextlib.suppress(InterruptedError):
            start_system(isopen=True, okled_pin=19, ngled_pin=26)

        mocked_servo.open.assert_called_once()
        mocked_servo.lock.assert_called_once()
        mocked_check_card_manager.assert_called_once()

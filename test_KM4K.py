# ruff: noqa: S101
import contextlib
import os
import time
from datetime import timedelta
from unittest import TestCase
from unittest.mock import Mock, create_autospec, patch

from redis import StrictRedis

from card_sdk import CardSDK

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

    @patch("KM4K.servo", autospec=True)
    @patch("KM4K.read_nfc", side_effect=[b"345678", InterruptedError])
    def test_start_system_with_closed_door_and_unregistered_card(
        self,
        mocked_read_nfc,  # noqa: ARG002
        mocked_servo,
    ):
        card = create_autospec(CardSDK)
        card.verify.return_value = False

        from KM4K import start_system

        with contextlib.suppress(InterruptedError):
            start_system(
                isopen=False,
                okled_pin=19,
                ngled_pin=26,
                cache=self.conn,
                card=card,
            )

        mocked_servo.unlock.assert_not_called()
        mocked_servo.lock.assert_not_called()

    @patch("KM4K.servo", autospec=True)
    @patch("KM4K.read_nfc", side_effect=[b"345678", InterruptedError])
    def test_start_system_with_closed_door_and_registered_card(
        self,
        mocked_read_nfc,  # noqa: ARG002
        mocked_servo,
    ):
        card = create_autospec(CardSDK)
        card.verify.return_value = True

        from KM4K import start_system

        with contextlib.suppress(InterruptedError):
            start_system(
                isopen=False,
                okled_pin=19,
                ngled_pin=26,
                cache=self.conn,
                card=card,
            )

        mocked_servo.unlock.assert_called_once()
        mocked_servo.lock.assert_not_called()

    @patch("KM4K.servo", autospec=True)
    @patch("KM4K.read_nfc", side_effect=[b"345678", InterruptedError])
    def test_start_system_with_open_door_and_unregistered_card(
        self,
        mocked_read_nfc,  # noqa: ARG002
        mocked_servo,
    ):
        card = create_autospec(CardSDK)
        card.verify.return_value = False

        from KM4K import start_system

        with contextlib.suppress(InterruptedError):
            start_system(
                isopen=True,
                okled_pin=19,
                ngled_pin=26,
                cache=self.conn,
                card=card,
            )

        mocked_servo.unlock.assert_not_called()
        mocked_servo.lock.assert_not_called()

    @patch("KM4K.servo", autospec=True)
    @patch("KM4K.read_nfc", side_effect=[b"345678", InterruptedError])
    def test_start_system_with_open_door_and_registered_card(
        self,
        mocked_read_nfc,  # noqa: ARG002
        mocked_servo,
    ):
        card = create_autospec(CardSDK)
        card.verify.return_value = True

        from KM4K import start_system

        with contextlib.suppress(InterruptedError):
            start_system(
                isopen=True,
                okled_pin=19,
                ngled_pin=26,
                cache=self.conn,
                card=card,
            )

        mocked_servo.unlock.assert_not_called()
        mocked_servo.lock.assert_called_once()

    @patch("KM4K.servo", autospec=True)
    @patch("KM4K.read_nfc", side_effect=[b"345678", b"345678", InterruptedError])
    def test_start_system_with_redis_cache(
        self,
        mocked_read_nfc,  # noqa: ARG002
        mocked_servo,
    ):
        card = create_autospec(CardSDK)
        card.verify.return_value = True

        from KM4K import start_system

        with contextlib.suppress(InterruptedError):
            start_system(
                isopen=True,
                okled_pin=19,
                ngled_pin=26,
                cache=self.conn,
                card=card,
            )

        mocked_servo.unlock.assert_called_once()
        mocked_servo.lock.assert_called_once()
        card.verify.assert_called_once()

    @patch("KM4K.servo", autospec=True)
    @patch("KM4K.read_nfc", side_effect=[b"456789", b"456789", InterruptedError])
    def test_start_system_unregistered_card_with_redis_cache(
        self,
        mocked_read_nfc,  # noqa: ARG002
        mocked_servo,
    ):
        card = create_autospec(CardSDK)
        card.verify.side_effect = [True, False]

        from KM4K import start_system

        with contextlib.suppress(InterruptedError):
            start_system(
                isopen=True,
                okled_pin=19,
                ngled_pin=26,
                cache=self.conn,
                card=card,
            )

        mocked_servo.unlock.assert_called_once()
        mocked_servo.lock.assert_called_once()
        card.verify.assert_called_once()

    @patch("KM4K.CACHE_EXPIRES_DELTA", timedelta(seconds=5))
    @patch("KM4K.servo", autospec=True)
    @patch("KM4K.read_nfc", side_effect=[b"456789", b"456789", InterruptedError])
    def test_start_system_with_redis_cache_expires(
        self,
        mocked_read_nfc,  # noqa: ARG002
        mocked_servo,
    ):
        card = create_autospec(CardSDK)
        card.verify.side_effect = [True, False]

        from KM4K import start_system

        with contextlib.suppress(InterruptedError):
            start_system(
                isopen=True,
                okled_pin=19,
                ngled_pin=26,
                cache=self.conn,
                card=card,
            )

        mocked_servo.unlock.assert_called_once()
        mocked_servo.lock.assert_called_once()
        card.verify.assert_called_once()

        time.sleep(10)

        self.assertEqual(self.conn.exists("456789"), 0)
        self.assertIsNone(self.conn.get("456789"))

# ruff: noqa: S101
import contextlib
from unittest import TestCase
from unittest.mock import Mock, create_autospec, patch

from card_verifier_interface import CardVerifierInterface

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
        self.verifier = create_autospec(CardVerifierInterface)

    @patch("KM4K.servo", autospec=True)
    @patch("KM4K.read_nfc", side_effect=[b"345678", InterruptedError])
    def test_start_system_with_closed_door_and_unregistered_card(
        self,
        mocked_read_nfc,  # noqa: ARG002
        mocked_servo,
    ):
        self.verifier.verify.return_value = False

        from KM4K import start_system

        with contextlib.suppress(InterruptedError):
            start_system(
                isopen=False,
                okled_pin=19,
                ngled_pin=26,
                verifier=self.verifier,
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
        self.verifier.verify.return_value = True

        from KM4K import start_system

        with contextlib.suppress(InterruptedError):
            start_system(
                isopen=False,
                okled_pin=19,
                ngled_pin=26,
                verifier=self.verifier,
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
        self.verifier.verify.return_value = False

        from KM4K import start_system

        with contextlib.suppress(InterruptedError):
            start_system(
                isopen=True,
                okled_pin=19,
                ngled_pin=26,
                verifier=self.verifier,
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
        self.verifier.verify.return_value = True

        from KM4K import start_system

        with contextlib.suppress(InterruptedError):
            start_system(
                isopen=True,
                okled_pin=19,
                ngled_pin=26,
                verifier=self.verifier,
            )

        mocked_servo.unlock.assert_not_called()
        mocked_servo.lock.assert_called_once()

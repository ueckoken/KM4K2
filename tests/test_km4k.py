# ruff: noqa: S101
import contextlib
from unittest import TestCase
from unittest.mock import Mock, create_autospec, patch

from km4k2.card_verifier_interface import CardVerifierInterface

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
class TestKm4k(TestCase):
    def setUp(self):
        self.verifier = create_autospec(CardVerifierInterface)

    def test_start_system_with_closed_door_and_unregistered_card(self):
        self.verifier.verify.return_value = False

        from km4k2.km4k import start_system

        # なぜか @patch だと2個目以降のテストメソッドでパッチが当たらないので、しかたな
        # く with でべた書き。たぶんこのファイルのトップレベルで km4k2.card_sdk をインポ
        # ートしたことで振る舞いが変わっている。
        # km4k2.card_sdk をすべてテストメソッド内でローカルインポートするようにすれば
        # @patch が効くようになるが、ほかのファイルで1つでもトップレベルで km4k2 のモジ
        # ュールをインポートしていたら効かなくなる
        # パッケージ化する前(__init__.py)は効いてたのでパッケージの読み込みとかに関係
        # してそう
        with patch(
            "km4k2.km4k.read_nfc",
            side_effect=[b"345678", InterruptedError],
        ), patch(
            "km4k2.km4k.servo",
            autospec=True,
        ) as mocked_servo, contextlib.suppress(
            InterruptedError,
        ):
            start_system(
                isopen=False,
                okled_pin=19,
                ngled_pin=26,
                verifier=self.verifier,
            )

        mocked_servo.unlock.assert_not_called()
        mocked_servo.lock.assert_not_called()

    def test_start_system_with_closed_door_and_registered_card(self):
        self.verifier.verify.return_value = True

        from km4k2.km4k import start_system

        with patch(
            "km4k2.km4k.read_nfc",
            side_effect=[b"345678", InterruptedError],
        ), patch(
            "km4k2.km4k.servo",
            autospec=True,
        ) as mocked_servo, contextlib.suppress(
            InterruptedError,
        ):
            start_system(
                isopen=False,
                okled_pin=19,
                ngled_pin=26,
                verifier=self.verifier,
            )

        mocked_servo.unlock.assert_called_once()
        mocked_servo.lock.assert_not_called()

    def test_start_system_with_open_door_and_unregistered_card(self):
        self.verifier.verify.return_value = False

        from km4k2.km4k import start_system

        with patch(
            "km4k2.km4k.read_nfc",
            side_effect=[b"345678", InterruptedError],
        ), patch(
            "km4k2.km4k.servo",
            autospec=True,
        ) as mocked_servo, contextlib.suppress(
            InterruptedError,
        ):
            start_system(
                isopen=True,
                okled_pin=19,
                ngled_pin=26,
                verifier=self.verifier,
            )

        mocked_servo.unlock.assert_not_called()
        mocked_servo.lock.assert_not_called()

    def test_start_system_with_open_door_and_registered_card(self):
        self.verifier.verify.return_value = True

        from km4k2.km4k import start_system

        with patch(
            "km4k2.km4k.read_nfc",
            side_effect=[b"345678", InterruptedError],
        ), patch(
            "km4k2.km4k.servo",
            autospec=True,
        ) as mocked_servo, contextlib.suppress(
            InterruptedError,
        ):
            start_system(
                isopen=True,
                okled_pin=19,
                ngled_pin=26,
                verifier=self.verifier,
            )

        mocked_servo.unlock.assert_not_called()
        mocked_servo.lock.assert_called_once()

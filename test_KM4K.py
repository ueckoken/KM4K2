import sqlite3
from unittest import TestCase
from unittest.mock import patch, Mock

rpi_mock = Mock()
nfc_mock = Mock()
wiringpi = Mock()


@patch.dict(
    "sys.modules",
    {"RPi": rpi_mock, "RPi.GPIO": rpi_mock.GPIO, "nfc": nfc_mock, "wiringpi": wiringpi},
)
class TestKM4K(TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()
        # mock CURRENT_TIMESTAMP
        self.conn.create_function(
            "CURRENT_TIMESTAMP", -1, lambda: "2006/01/02 15:04:05"
        )
        # init schema
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS users (name TEXT NOT NULL, idm BLOB NOT NULL, date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
        )

    def tearDown(self):
        self.conn.close()

    @patch("KM4K.mode", 0)
    @patch("KM4K.input", return_value="kokentaro")
    @patch("KM4K.read_nfc", return_value=b"456789")
    def test_add_nfc_with_new_card(self, mocked_read_nfc, mocked_input):
        from KM4K import add_nfc

        add_nfc(self.cur)

        mocked_read_nfc.assert_called_once()
        mocked_input.assert_called_once()

        self.cur.execute("SELECT * FROM users")
        users = self.cur.fetchall()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]["name"], "kokentaro")
        self.assertEqual(users[0]["idm"], b"456789")
        self.assertEqual(users[0]["date"], "2006/01/02 15:04:05")

    @patch("KM4K.mode", 0)
    @patch("KM4K.input", return_value="kokentaro")
    @patch("KM4K.read_nfc", return_value=b"456789")
    def test_add_nfc_with_registered_card(self, mocked_read_nfc, mocked_input):
        self.cur.execute(
            "INSERT INTO users (name, idm) VALUES(?, ?)", ("kokenjiro", b"456789")
        )

        from KM4K import add_nfc

        add_nfc(self.cur)

        mocked_read_nfc.assert_called_once()
        mocked_input.assert_called_once()

        self.cur.execute("SELECT * FROM users")
        users = self.cur.fetchall()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]["name"], "kokenjiro")
        self.assertEqual(users[0]["idm"], b"456789")
        self.assertEqual(users[0]["date"], "2006/01/02 15:04:05")

    @patch("KM4K.mode", 1)
    @patch("KM4K.input", return_value="kokenjiro")
    def test_delete_nfc_with_registerd_user(self, mocked_input):
        self.cur.execute(
            "INSERT INTO users (name, idm) VALUES(?, ?)", ("kokenjiro", b"567890")
        )

        from KM4K import delete_nfc

        delete_nfc(self.cur)

        mocked_input.assert_called_once()

        self.cur.execute("SELECT * FROM users")
        users = self.cur.fetchall()
        self.assertEqual(len(users), 0)

    @patch("KM4K.mode", 1)
    @patch("KM4K.input", return_value="kokenjiro")
    def test_delete_nfc_with_unregistered_user(self, mocked_input):
        from KM4K import delete_nfc

        delete_nfc(self.cur)

        mocked_input.assert_called_once()

        self.cur.execute("SELECT * FROM users")
        users = self.cur.fetchall()
        self.assertEqual(len(users), 0)

    @patch("KM4K.mode", 2)
    @patch("KM4K.servo", autospec=True)
    @patch("KM4K.read_nfc", side_effect=[b"345678", InterruptedError])
    def test_start_system_with_closed_door_and_registered_card(
        self, mocked_read_nfc, mocked_servo
    ):
        self.cur.execute(
            "INSERT INTO users (name, idm) VALUES(?, ?)", ("kokensaburo", b"345678")
        )

        from KM4K import start_system

        try:
            start_system(self.cur, False, 19, 26)
        except InterruptedError:
            pass

        mocked_servo.open.assert_called_once()
        mocked_servo.lock.assert_not_called()

    @patch("KM4K.mode", 2)
    @patch("KM4K.servo", autospec=True)
    @patch("KM4K.read_nfc", side_effect=[b"345678", InterruptedError])
    def test_start_system_with_closed_door_and_unregistered_card(
        self, mocked_read_nfc, mocked_servo
    ):
        from KM4K import start_system

        try:
            start_system(self.cur, False, 19, 26)
        except InterruptedError:
            pass

        mocked_servo.open.assert_not_called()
        mocked_servo.lock.assert_not_called()

    @patch("KM4K.mode", 2)
    @patch("KM4K.servo", autospec=True)
    @patch("KM4K.read_nfc", side_effect=[b"345678", InterruptedError])
    def test_start_system_with_open_door_and_registered_card(
        self, mocked_read_nfc, mocked_servo
    ):
        self.cur.execute(
            "INSERT INTO users (name, idm) VALUES(?, ?)", ("kokensaburo", b"345678")
        )

        from KM4K import start_system

        try:
            start_system(self.cur, True, 19, 26)
        except InterruptedError:
            pass

        mocked_servo.open.assert_not_called()
        mocked_servo.lock.assert_called_once()

    @patch("KM4K.mode", 2)
    @patch("KM4K.servo", autospec=True)
    @patch("KM4K.read_nfc", side_effect=[b"345678", InterruptedError])
    def test_start_system_with_open_door_and_unregistered_card(
        self, mocked_read_nfc, mocked_servo
    ):
        from KM4K import start_system

        try:
            start_system(self.cur, True, 19, 26)
        except InterruptedError:
            pass

        mocked_servo.open.assert_not_called()
        mocked_servo.lock.assert_not_called()

    @patch("KM4K.start_system")
    @patch("KM4K.delete_nfc")
    @patch("KM4K.add_nfc")
    @patch("KM4K.servo", autospec=True)
    def test_main_without_args(
        self, mocked_servo, mocked_add_nfc, mocked_delete_nfc, mocked_start_system
    ):
        from KM4K import main

        # No additional positional argument implicitly means mode 2: to run the daemon that authorizes IC card and locks/unlocks.
        main(["KM4K.py"])

        # To run the daemon, it should call start_system, not add_nfc or delete_nfc.
        mocked_servo.reset.assert_called_once()
        mocked_add_nfc.assert_not_called()
        mocked_delete_nfc.assert_not_called()
        mocked_start_system.assert_called_once()

    @patch("KM4K.start_system")
    @patch("KM4K.delete_nfc")
    @patch("KM4K.add_nfc")
    @patch("KM4K.servo", autospec=True)
    def test_main_with_0(
        self, mocked_servo, mocked_add_nfc, mocked_delete_nfc, mocked_start_system
    ):
        from KM4K import main

        # Mode 0 means to add a user.
        main(["KM4K.py", "0"])

        # To add a user, it should call add_nfc, not delete_nfc or start_system.
        mocked_servo.reset.assert_called_once()
        mocked_add_nfc.assert_called_once()
        mocked_delete_nfc.assert_not_called()
        mocked_start_system.assert_not_called()

    @patch("KM4K.start_system")
    @patch("KM4K.delete_nfc")
    @patch("KM4K.add_nfc")
    @patch("KM4K.servo", autospec=True)
    def test_main_with_1(
        self, mocked_servo, mocked_add_nfc, mocked_delete_nfc, mocked_start_system
    ):
        from KM4K import main

        # Mode 1 means to delete a user.
        main(["KM4K.py", "1"])

        # To delete a user, it should call delete_nfc, not add_nfc or start_system.
        mocked_servo.reset.assert_called_once()
        mocked_add_nfc.assert_not_called()
        mocked_delete_nfc.assert_called_once()
        mocked_start_system.assert_not_called()

    @patch("KM4K.start_system")
    @patch("KM4K.delete_nfc")
    @patch("KM4K.add_nfc")
    @patch("KM4K.servo", autospec=True)
    def test_main_with_2(
        self, mocked_servo, mocked_add_nfc, mocked_delete_nfc, mocked_start_system
    ):
        from KM4K import main

        # Mode 2 means to run the daemon that authorizes IC card and locks/unlocks.
        main(["KM4K.py", "2"])

        # To run the daemon, it should call start_system, not add_nfc or delete_nfc.
        mocked_servo.reset.assert_called_once()
        mocked_add_nfc.assert_not_called()
        mocked_delete_nfc.assert_not_called()
        mocked_start_system.assert_called_once()

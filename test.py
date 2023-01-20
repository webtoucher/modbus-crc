from src import add_crc, check_crc
from unittest import TestCase, TestSuite, TextTestRunner


class _UnitTest(TestCase):
    def test_add_crc(self):
        package = b'\x00\x12\x34\xAB\xCD\xEF'
        self.assertEqual(add_crc(package), b'\x00\x12\x34\xAB\xCD\xEF\xD2\xD4')

    def test_check_valid_crc(self):
        valid_signed_package = b'\x00\x12\x34\xAB\xCD\xEF\xD2\xD4'
        self.assertTrue(check_crc(valid_signed_package))

    def test_check_invalid_crc(self):
        invalid_signed_package = b'\x00\x12\x34\xAB\xCD\xEF\xAB\xCD'
        self.assertFalse(check_crc(invalid_signed_package))


if __name__ == '__main__':
    suite = TestSuite()
    suite.addTest(_UnitTest('test_add_crc'))
    suite.addTest(_UnitTest('test_check_valid_crc'))
    suite.addTest(_UnitTest('test_check_invalid_crc'))
    runner = TextTestRunner()
    runner.run(suite)

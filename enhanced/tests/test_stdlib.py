import unittest
import subprocess
import os

class TestStdlib(unittest.TestCase):
    def setUp(self):
        self.enhc_path = os.path.join(os.path.dirname(__file__), '..', 'enhc.py')

    def test_file_io(self):
        example_path = os.path.join(os.path.dirname(__file__), '..', 'examples', 'read_file.en')
        result = subprocess.run(['python', self.enhc_path, example_path, '--ir'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"Error: {result.stdout} {result.stderr}")
        self.assertIn("call i8* @enhanced_read_file", result.stdout)
        self.assertIn("call void @enhanced_write_file", result.stdout)
        self.assertIn("call i32 @enhanced_file_exists", result.stdout)

    def test_http_get(self):
        example_path = os.path.join(os.path.dirname(__file__), '..', 'examples', 'http_get.en')
        result = subprocess.run(['python', self.enhc_path, example_path, '--ir'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"Error: {result.stdout} {result.stderr}")
        self.assertIn("call i8* @enhanced_http_get", result.stdout)

    def test_discord_rpc_mock(self):
        example_path = os.path.join(os.path.dirname(__file__), '..', 'examples', 'discord_rpc_mock.en')
        result = subprocess.run(['python', self.enhc_path, example_path, '--ir'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"Error: {result.stdout} {result.stderr}")
        self.assertIn("FFI Call to Discord_Initialize", result.stdout)
        self.assertIn("FFI Call to Discord_UpdatePresence", result.stdout)
        self.assertIn("FFI Call to Discord_Shutdown", result.stdout)
        self.assertIn("call void @enhanced_sleep", result.stdout)

if __name__ == '__main__':
    unittest.main()

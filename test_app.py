import unittest
import subprocess
import tempfile
import time
import shutil
from pathlib import Path

class TestClientServerApp(unittest.TestCase):
    def setUp(self):
        """Set up temporary directories and start the server before each test."""
        # Create a temporary environment to safely run tests without cluttering your system
        self.test_dir = tempfile.mkdtemp()
        self.server_dir = Path(self.test_dir) / "server_downloads"
        self.client_dir = Path(self.test_dir) / "client_files"
        self.server_dir.mkdir()
        self.client_dir.mkdir()
        
        # Create a dummy file to transmit
        self.test_filename = "test_data.txt"
        self.test_file_path = self.client_dir / self.test_filename
        self.test_file_path.write_text("Hello, this is the original file content.")
        
        # Define host and port for testing
        self.host = "127.0.0.1"
        self.port = 6007 
        
        # Start the server as a background subprocess, using the temporary directory
        self.server_process = subprocess.Popen(
            ["python", "server.py", "--host", self.host, "--port", str(self.port), "--dir", str(self.server_dir)]
        )
        
        # Give the server 1 second to start up and bind to the port
        time.sleep(1)

    def tearDown(self):
        """Kill the server and clean up temporary files after each test."""
        self.server_process.terminate()
        self.server_process.wait()
        shutil.rmtree(self.test_dir)

    def test_successful_transmission(self):
        """Test that a file is successfully transmitted and saved."""
        # Run the client as a subprocess
        subprocess.run(
            ["python", "client.py", "--host", self.host, "--port", str(self.port), "--file", str(self.test_file_path)],
            check=True
        )
        
        # Check if the file arrived safely in the server's designated directory
        received_file = self.server_dir / self.test_filename
        self.assertTrue(received_file.exists(), "File was not saved by the server.")
        self.assertEqual(received_file.read_text(), "Hello, this is the original file content.")

    def test_overwrite_prevention(self):
        """Test that an existing file is not overwritten."""
        # 1. Pre-create a file in the server directory with the exact same name but DIFFERENT content
        received_file = self.server_dir / self.test_filename
        received_file.write_text("PRE-EXISTING DATA")
        
        # 2. Run the client to transmit the file (which has the "Hello..." content)
        subprocess.run(
            ["python", "client.py", "--host", self.host, "--port", str(self.port), "--file", str(self.test_file_path)]
        )
        
        # 3. Verify the file content remains the pre-existing data, proving it was not overwritten
        self.assertTrue(received_file.exists())
        self.assertEqual(
            received_file.read_text(), 
            "PRE-EXISTING DATA", 
            "The server incorrectly overwrote the existing file!"
        )

if __name__ == "__main__":
    unittest.main()
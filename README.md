# Client-Server File Transmission App

## Description
A simple client-server application written in Python. 

The server listens for incoming connections and saves transmitted files to a designated directory. To ensure data integrity, if a client attempts to send a file that already exists in the destination folder, the server rejects the transmission to prevent overwriting. The client accepts an input file path and displays a dynamic progress bar during the file transmission. Both server and client have configurable file path, host and port via command line arguments.

## Project Structure
* `README.md`: An overview and instructions.
* `server.py`: The Server implementation.
* `client.py`: The Client implementation.
* `test_app.py`: The automated integration test suite.


## How to Run

**1. Start the Server**
The server must be started first so it can wait for a client connection. 

* **Syntax:** `python server.py --host <IP_ADDRESS> --port <PORT> --dir <DIRECTORY_PATH>`
* **Example (Copy/Paste):**
  ```bash
  python server.py --host 127.0.0.1 --port 8080 --dir ./received_files
  ```

**2. Run the Client**
Open a second, separate terminal window. Run the client to connect to the server and transmit a file.

* **Syntax:** `python client.py --host <IP_ADDRESS> --port <PORT> --file <FILE_PATH>`
* **Example (Copy/Paste):**
  ```bash
  python client.py --host 127.0.0.1 --port 8080 --file ./test_file.txt
  ```

**3. Run the Automated Tests**
To verify the application's core requirements without starting the server manually, run the included `unittest` suite. This starts up an isolated background server and creates temporary files to test the transmission and overwrite-prevention logic.

* **Command:**
  ```bash
  python -m unittest test_app.py -v
  ```
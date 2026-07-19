import socket
import argparse
import sys
from pathlib import Path

def start_client(host, port, file_path_str):
    file_path = Path(file_path_str)
    
    # Ensure the input file exists before attempting to connect
    if not file_path.exists() or not file_path.is_file():
        print(f"Error: The file '{file_path}' does not exist or is not a valid file.")
        return

    # Extract filename and calculate the file size
    filename = file_path.name
    filesize = file_path.stat().st_size

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(f"Connecting to server at {host}:{port}...")
        try:
            s.connect((host, port))
        except ConnectionRefusedError:
            print("Error: Connection refused. Is the server running?")
            return

        # Send the metadata header expected by the server
        # Format: "filename|filesize\n"
        header = f"{filename}|{filesize}\n"
        s.sendall(header.encode('utf-8'))
        
        print(f"Starting transmission of '{filename}' ({filesize} bytes)...")

        # Transmit the file in chunks and display progress
        bytes_sent = 0
        chunk_size = 4096

        with file_path.open('rb') as f:
            while bytes_sent < filesize:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                
                # Send the chunk to the server
                s.sendall(chunk)
                bytes_sent += len(chunk)
                
                # Calculate percentage and display progress
                percentage = (bytes_sent / filesize) * 100 if filesize > 0 else 100
                sys.stdout.write(f"\rTransmitting: [{bytes_sent}/{filesize} bytes] {percentage:.2f}%")
                sys.stdout.flush()
                
        print("\nFile transmission successfully completed.")

if __name__ == "__main__":
    # Setup argparse for configuration and input file path
    parser = argparse.ArgumentParser(description="File Transfer Client")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Server IP address to connect to")
    parser.add_argument("--port", type=int, default=6006, help="Server port to connect to")
    parser.add_argument("--file", type=str, required=True, help="Path to the file to be transmitted")
    
    args = parser.parse_args()
    
    # Run the client
    start_client(args.host, args.port, args.file)
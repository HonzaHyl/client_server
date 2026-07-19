import socket
import argparse
from pathlib import Path

def start_server(host, port, save_directory):
    # Setup the designated directory using pathlib
    target_dir = Path(save_directory)
    target_dir.mkdir(parents=True, exist_ok=True)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Allow immediate port reuse
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        s.bind((host, port))
        s.listen()
        print(f"Server listening on {host}:{port}...")
        print(f"Waiting for files to save to: {target_dir.resolve()}")
        
        # Keep the server running to accept multiple client connections sequentially
        while True:
            conn, addr = s.accept()
            with conn:

                print(f"\nConnection established with {addr}")

                # Set timeout to prevent server hanging if the client stops working
                conn.settimeout(15.0)
                
                try:
                    # Read the metadata header (assuming format: "filename|filesize\n")
                    header_data = b""
                    while b"\n" not in header_data:
                        chunk = conn.recv(1)
                        if not chunk:
                            break
                        header_data += chunk
                    
                    if not header_data:
                        continue
                    
                    # Parse the header
                    header = header_data.decode('utf-8').strip()
                    filename, filesize_str = header.split('|')
                    filesize = int(filesize_str)

                    # Use this to prevent unwanted overwriting of sensitive directories 
                    filename = Path(filename).name
             
                    # Create the full path for the incoming file
                    file_path = target_dir / filename
                    
                    # Check if file already exists to prevent overwriting
                    if file_path.exists():
                        print(f"File '{filename}' already exists. Transmission aborted to prevent overwrite.")
                        continue # Drops the connection and waits for the next client
                    
                    # Receive the file data and save it
                    print(f"Receiving '{filename}' ({filesize} bytes)...")
                    bytes_received = 0
                    
                    with file_path.open('wb') as f:
                        while bytes_received < filesize:
                            # Read chunks of up to 4096 bytes
                            data = conn.recv(min(4096, filesize - bytes_received))
                            if not data:
                                break
                            f.write(data)
                            bytes_received += len(data)
                    
                    if bytes_received == filesize:
                        print(f"File successfully saved to {file_path}")
                    else:
                        print("Connection dropped before file transmission completed.")
                
                except socket.timeout:
                    print("Error: Connection timed out. Client disconnected unexpectedly.")
                except ValueError:
                    print("Error: Invalid header format received.")
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Setup argparse for configuration
    parser = argparse.ArgumentParser(description="File Transfer Server")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Server IP address to bind to")
    parser.add_argument("--port", type=int, default=6006, help="Port to listen on")
    parser.add_argument("--dir", type=str, default="./received_files", help="Designated directory for received files")
    
    args = parser.parse_args()
    
    # Run the server
    start_server(args.host, args.port, args.dir)
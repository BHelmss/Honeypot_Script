'''
This script will mimick an SSH server (port 22) that logs connection attempts and fakes a login prompt.

It will also log the IP address of the attacker, timpestamp, and input ('root' or 'user').
Responds with “Password:” (but never authenticates—just logs and stalls).

Output: Text file or console log like “192.168.1.100 connected at 2025-03-08 15:00, tried root.”
'''

import socket
import logging

#Set up logging to a file called 'honeypot.log'
logging.basicConfig(filename='honeypot.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def start_honeypot(port=22):
    # Create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Set options for the socket; (socket level option, socket reuse address, value)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to the host and port
    s.bind(('0.0.0.0', port))
    s.listen(5)  # Allow up to 5 queued connections

    print(f"Honeypot listening on port {port}...")
    while True:
        # Accept a connection
        conn, addr = s.accept()
        print(f"Connection from {addr} accepted.")
        try: 
            # Send a fake login banner
            conn.sendall(b"SSH-2.0-OpenSSH_7.2\r\n")

            # Log the connection attempt
            logging.info(f"Connection from {addr} accepted.")

            # Send a fake login prompt
            conn.sendall(b"root@localhost's password: ")

            # Receive the password attempt
            data = conn.recv(1024)
            if data:
                password_attempt = data.decode('utf-8').strip()
                logging.info(f"Password attempt from {addr}: {password_attempt}")

                # Respond with "Password:"
                conn.sendall(b"Password: ")
                
        except Exception as e:
            (f"Error handling connection from {addr}: {str(e)}")

        finally:
            # Close the connection
            conn.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='SSH Honeypot.')
    parser.add_argument('--port', type=int, default=22, help='Port to listen on (default: 22)')
    args = parser.parse_args()

    try:
        start_honeypot(port=args.port)
    except PermissionError:
        print(f"Error: Port {args.port} requires root privileges (e.g., sudo). Try a higher port like 2222.")
    except Exception as e:
        print(f"Failed to start honeypot: {str(e)}")
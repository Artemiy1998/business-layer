import socket
import time
import sys


buffer_size = 2048

sock_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_client.connect(('192.168.0.107', 9099))
sock_client.send(b't')

# Telega imitator.
while True:
    data = sock_client.recv(buffer_size)
    messages = data.decode()
    print(messages)
    messages = messages.split('|')
    for message in messages:
        if message == 'e':
            sys.exit()
        if not message:
            continue
        # Return formatted message with data key.
        response = f'"t": "{message[2:-2]}"|'
        time.sleep(1)
        sock_client.send(response.encode())

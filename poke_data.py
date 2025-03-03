import socket
import time
import binascii
import os

# Function to send a command over the socket, adding CRLF at the end.
def sendCommand(s, content):
    s.sendall((content + '\r\n').encode())

# Create and connect a TCP socket to the target IP and port.
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("192.168.1.73", 5000))

# Open "input" in binary mode and read 344 bytes (the expected size).
file = open("input", "rb")
inject = file.read(344)

# Convert binary data to a hex string.
inject = str(binascii.hexlify(inject), "utf-8")

# Send a "poke" command with the hex data to a specified memory address.
# Replace 0x042DA8E8 with your target address.
sendCommand(s, f"poke 0x042DA8E8 0x{inject}")

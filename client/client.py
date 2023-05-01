"""
The client side of a TCP connection
Should run on the command line with 3 parameters, server ip, server port number 
and requested file name.

Author: Sam Clark 
Date: 18/08/2021
Version: 2
"""

import socket
import sys
import os
from datetime import datetime

# ------------------------------------------------------------------------------

def main():
    """ The main function, see module docstring """
    server_address, filename = get_parameters()
    if filename is None:
        exit()
    client = initialise_client_socket(server_address, filename)
    message = form_file_request(filename)
    if message is None:
        client.close()
        exit()
    client.send(message)
    try:
        read_server_response(client, filename, server_address[0])
    except socket.timeout:
        print_server_message(f"Connection with {server_address} has timed out.", "TIMEOUT")
    print_server_message("Closing Socket ...", "SOCKET STATUS")
    client.close()
    print_server_message("Socket close successful", "SOCKET CLOSED")
    
# ------------------------------------------------------------------------------


def get_parameters():
    """
    Retrieves the required socket parameters:
        - address:  the server ip_address or address name
        - port: the server port number 
        - file_name:  the name of the file requested
    and returns:
        - server_address: combines the servers ip and port into a tuple. 
        - file_name: same as above but, the file must not exist in same
                     directory as this program.
    
    This function exits the program if the parameters are invalid.
    """
    args = sys.argv
    print_server_message(f"Checking client parameters ...", "STATUS")
    try: 
        address = args[1]
        port = int(args[2])
        file_request = args[3]
        server_address = socket.getaddrinfo(address, port)[0][4]    
        if len(args) != 4:
            raise Exception
    except:
        print_server_message("The client takes 3 arguments (server_address, server_port, file_request).", "ERROR")
        exit()
    
    print_server_message(f"Checking if {file_request} already exists ....", "STATUS")
    try:
        if os.path.isfile(file_request):
            print_server_message("The file requested already exists in this directory.", "ERROR")
            file_request = None
            
        return server_address, file_request
        
    except:
        print_server_message("Something went wrong checking for the file.", "ERROR")
        exit()



def initialise_client_socket(server_address, file_request):
    """
    Attempts to initialise the client socket and connect it to the server.
    If at any point the initialisation fails, the client prints an error
    message and exits the program.
    """
    print_server_message("Initialising the client socket and connecting to server ...", "INITIALISING")
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(1)
    except:
        print_server_message("An error occured while initialising the socket.", "ERROR")
        exit()
    else:
        print_server_message("Socket initialisation was successful, connected to server ...", "INITIALISED")
        try:
            client.connect(server_address)
            client.settimeout(1)
            
            print_server_message("Socket connection successful, sending file request", "CONNECTED")
            return client
        except:
            print_server_message("An error occured while connecting to the server. Check the server_address and port are correct.", "ERROR")
            client.close()
            exit()



def form_file_request(file_name):
    """
    Takes a filename and forms a filerequest to send to the server. 
    if the length of the filename is longer than 1024 bytes or less than 1 byte
    an error message is printed and the program returns None signalling the main
    function to close the socket and exit.
    Messages consist of:
        - 16 bit magic number
        - 8 bit Type
        - 16 bit filename length in bytes (n)
        - 8 * n bit Filename encoded from utf-8
    """
    magic_no = 0x497E
    msg_type = 1
    filename_bytes = file_name.encode('utf-8')
    filename_len = len(filename_bytes)
    
    # exit on invalid 
    if filename_len > 1024 or filename_len < 1:
        print_server_message("The file requested must be of length between 1 and 1024.", "ERROR")
        return None
    
    message = bytearray()
    message.append(magic_no >> 8)
    message.append(magic_no & 0xFF)
    message.append(msg_type)
    message.append(filename_len >> 8)
    message.append(filename_len & 0xFF)
    message += filename_bytes
    print_server_message("File Request formed, sending request to server...", "SENDING REQUEST")
    return message
    
def read_server_response(client, filename, server_ip):
    """
    Reads the server response any of the following paths may occur :
      - If the server replies with an incorrect magic number or type 
            * An error message is printed
            * the message is discarded
      - If the server replies with a status of 0
            * A message saying the request couldn't be found is printed
      - If the prior 3 parameters are met
            * The client program prompts the user of success and begins writing
              the results to a file with the requested filesname
            * Received bytes are processed 4096 bytes at a time.
            * When the full length is received the file is closed and a message
              is sent telling the user how many bytes were received
              
    """
    print_server_message("Server response received ...", "RESPONSE")
    magic_no = int(client.recv(2).hex(), 16)
    msg_type = int(client.recv(1).hex(), 16)
    status = int(client.recv(1).hex(), 16)
    if magic_no != 0x497E:
        print_server_message("The reply had the incorrect magic number and has been discarded.", "INVALID RESPONSE")
    elif msg_type != 2:
        print_server_message("The reply had the incorrect message type and has been discarded.", "INVALID RESPONSE")
    elif status == 0:
        print_server_message("The file requested could not be returned, the file may not exist.", "RESPONSE")
    else:
        length = int(client.recv(4).hex(), 16)
        remaining = length
        print_server_message(f"Writing data to file {filename} ...", "RESPONSE")
        try:
            
            data_file = open(f"{filename}", 'w')
            while remaining > 0:
                if remaining >= 4096:
                    filedata = client.recv(4096).decode('utf-8')
                    remaining -= 4096
                else:
                    filedata = client.recv(remaining).decode('utf-8')
                    remaining = 0
                data_file.write(filedata)
            data_file.close()
            print_server_message(f"{length + 8} bytes received from {server_ip}", "RECEIVED")
            print_server_message(f"Server data writing to {filename} is complete.", "COMPLETE")
        except:
            print_server_message(f"An error occured while writing to {filename}", "ERROR")


# ------------------------------------------------------------------------------

def print_server_message(message, category):
    hour = datetime.now().hour
    minute = datetime.now().minute
    second = datetime.now().second    
    print(f"{hour:02d}:{minute:02d}:{second:02d} [{category:^16s}] {message}")

# ------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
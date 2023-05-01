"""
The server side of a socket program using TCP
Should run on the command line with one parameter, the port number 

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
    """ The main view module docstring """
    port_number = get_port_number()
    server = initialise_server(port_number)
    server.listen()
    while True:
        client_con, client_addr = accept_client(server)
        try:
            filename, status = receive_request(client_con, client_addr, server)
            if status != -1:
                send_response(client_con, client_addr, filename, status)
        except socket.timeout:
            print_server_message(f"Connection with {client_addr} has timed out.", "TIMEOUT")
        client_con.close()
        print_server_message(f"{client_addr} has disconnected.", "DISCONNECTION")

# ------------------------------------------------------------------------------

def get_port_number():
    """ 
    Gets the portnumber from the command line when starting the program call.
    If the port number is invalid the server prints error messages and exits
    the program.
    A valid server call must have:
        - Exactly 1 parameter, the port number
        - A port number must be a valid integer
        - Port number must be between 1024 and 64000
    """
    try:
        args = sys.argv
        port_number = int(args[1])
        valid = True
        if len(args) != 2:
            print_server_message("Socket server takes exactly one argument (port number)", "ERROR")
            valid = False       
        if port_number > 64000 or port_number < 1024:
            print_server_message("The port number must be between 1024 and 64000(inclusive)", "ERROR")
            valid = False
    except ValueError:
        print_server_message("The port number must be an integer value", "ERROR")
        valid = False
    except:
        print_server_message("An Error has occured retrieving parameters, program exited", "ERROR")
        valid = False
        
    if valid:
        return port_number
    else:
        exit()


def initialise_server(port_number):
    """
    Uses the pre obtained port number to initialise a socket and bind it to the
    port number.
    """
    print_server_message("Setting up server, binding ip address", "SERVER START")
    try:
        ip_address = socket.gethostbyname(socket.gethostname())
        print(ip_address)
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((ip_address, port_number))
        print_server_message("setup successful, server starting", "SERVER START")
        return server   
    except PermissionError:
        print_server_message("This port may already be in use.", "ERROR")
        exit()
    except:
        print_server_message("An Error has occured while starting up the server.", "ERROR")
        exit()
    

def accept_client(server):
    """ Accepts clients, helper function it to print server messages """
    print_server_message("listening ...", "SERVER STATUS")
    try:
        client_con, client_addr = server.accept()
        client_con.settimeout(1)
        print_server_message(f"{client_addr} has connected", "CONNECTION")
        return client_con, client_addr
    except:
        print_server_message("An Error has occured while connecting a client.", "ERROR")
        return accept_client(server)


def receive_request(client_con, client_addr, server):
    """
    This function retreives the file request and returns it. The function also 
    returns a status code:
        - (-1) an error occurred trying to retreive the file request
        - ( 0) The request was retrieved but the file couldn't be found
        - ( 1) The request was retrieved and can be found, return the data
    """
    try:
        header = int(client_con.recv(5).hex(), 16)
        magic_no = header >> 24
        msg_type = (header >> 16)  & 0xFF
        filename_length = header & 0xFFFF
        if magic_no != 0x497E:
            print_server_message(f"{client_addr} used incorrect Magic no", "INVALID REQUEST")
            status = 0
            filename = None
        elif msg_type != 1:
            print_server_message(f"{client_addr} used incorrect Type", "INVALID REQUEST")
            status = 0
            filename = None
        else:
            filename = client_con.recv(filename_length).decode('utf-8')
            print_server_message(f"{client_addr} has has requested {filename}", "REQUEST")
            if os.path.isfile(filename):
                status = 1
            else:
                status = 0
                print_server_message(f"The file requested by {client_addr} could not be found", "ERROR")
    except:
        print_server_message(f"Could not retreive request from {client_addr}", "ERROR")
        filename = None
        status = -1
    return filename, status


def send_response(client_con, client_addr, filename, status):
    """
    Sends the appropriate response message to the client. 
    
    All messages consist of:
        - 16 bit magic number
        - 8 bit Type
        - 8 bit status code
    
    If the filename couldn't be found a status code of 0 is added and 
        - 32 bit data length bytes of 0 is added
    
    Otherwise the remainder of the response consists of:
        - 32 bit data length in bytes (n)
        - n * 8 bit filedata is added
    """
    message = bytearray()
    
    magic_no = 0x497E
    msg_type = 2    
    
    message.append(magic_no >> 8)
    message.append(magic_no & 0xFF)
    message.append(msg_type)   
    message.append(status)
    
    if status == 0:
        
        message.append(0 << 31)
        print_server_message(f"Sending failure message", "SENDING")
    else:
        print_server_message(f"The file requested was found, sending now ...", "SENDING")
        
        infile = open(filename)
        content = infile.read()
        infile.close()
        # Data length
        
        file_bytes = content.encode('utf-8')
        length = len(file_bytes)
        
        message.append((length >> 24) & 0xFF)
        message.append((length >> 16) & 0xFF)
        message.append((length >> 8) & 0xFF)
        message.append(length & 0xFF)
        # File data

        message += file_bytes
        
    client_con.send(message)
    print_server_message(f"Server sent a total of {len(message)} bytes to {client_addr}", "SENT")
    

# ------------------------------------------------------------------------------

def print_server_message(message, category):
    hour = datetime.now().hour
    minute = datetime.now().minute
    second = datetime.now().second    
    print(f"{hour:02d}:{minute:02d}:{second:02d} [{category:^16s}] {message}")

# ------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
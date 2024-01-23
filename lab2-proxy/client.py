import socket

    

def main():

    # bind the socket to a public host, and a port
    host_name = "127.0.0.1"
    port = 12345

    # Create a TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # same local address can be used for multiple connections
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    #client_socket.bind((host_name, port))
    client_socket.connect((host_name, port))

    """
    def send_msg():
        while True:
            msg = input("Enter a message")
            client_socket.send(msg.encode("utf-8"))

    send_msg()"""

    

        

if __name__ == "__main__":
    print("--- Starting client ---")
    
    main()

     
   

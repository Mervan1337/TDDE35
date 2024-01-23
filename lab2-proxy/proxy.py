# std library's
import socket
import gzip


class Header:
    def __init__(self, bytes):
        # Split the bytes into a list of strings by line
        header_lines = bytes.decode("utf-8").split("\r\n")
        self.first_line = header_lines[0]   # Store the first line separately
        self.headers = [item.split(":", 1) for item in header_lines[1:-2]]  # Split the headers into key-value pairs
        # Convert the list of pairs into a dictionary with lowercase
        self.headers = {key.lower():value.strip() for key, value in self.headers}

    # Set and get items in the headers dictionary
    def __setitem__(self, key, value):
        self.headers[key] = value
    
    def __getitem__(self, key):
        return self.headers[key]
    
    #get value of a header by key
    def get(self, key, default=None):
        return self.headers.get(key, default)

    def convert_to_bytes(self):
        """ Convert the header back to bytes """
        header_bytes = self.first_line.encode("utf-8") + b"\r\n"    # Convert the first line to bytes and add a line break
        for key, value in self.headers.items(): # Convert each header key-value pair to bytes and concatenate with CRLF(a line break)
            header_bytes += key.encode("utf-8") + b": " +value.encode("utf-8") + b"\r\n"
        header_bytes += b"\r\n" # Add an extra linebreak after the headers to separate from content
        return header_bytes

class HTTP:
    """Used to receive and send HTTP requests and responses"""
    def __init__(self):
        # initialize content and headers to empty
        self.content = b""
        self.content_length = 0
        self.header = None

    def receive_content(self, socket):
        # receive the content in packets of 1024 bytes until all content is received
        while len(self.content) < self.content_length:
            packet_data = socket.recv(1024)
            # if no more data is received, break the loop
            if not packet_data:
                break
            self.content += packet_data
        return self.content

    
    def receive_header(self, socket):
        header = b""
        content = b""
        # receive the header in packets of 1024 bytes until the header is complete
        while(True):
            packet_data = socket.recv(1024)
            header += packet_data
            # if no more data is received
            if header == b"":
                return
            if b"\r\n\r\n" in header:
                # Split the header and content from the received data
                header, content = header.split(b"\r\n\r\n", 1)
                header += b"\r\n\r\n"
                break
       
        self.header = Header(header)
        # set the content and content length
        self.content = content
        self.content_read = len(content)
        self.content_length = int(self.header.get("content-length", 0))


    def send(self, socket, new_data):
        # send the header and content to the socket
        if not new_data == None:
            socket.send(self.header.convert_to_bytes() + new_data)
        else:
            socket.send(self.header.convert_to_bytes() + self.content)
        


class Request(HTTP):
    def __init__(self):
        super().__init__()

    def receive_header(self, socket_):
        """ Receives header and then handles it """
        super().receive_header(socket_)

        if self.header == None:
            return
    
        # Modify the request header
        self.header.first_line = (self.header.first_line.replace("http://", "")).replace(self.header["host"], "")
        if ":" not in self.header["host"]:
            self.header["host"] += ":80"
        
        # If not HTTP connection we set header = None
        if not self.header["host"].endswith(":80"):
            self.header = None
            return

    def send(self, socket_):
        """ sends request to host via socket_ """
        #Parse the host address and port from the header
        host_addr, host_port = self.header["host"].split(":")
        host_ip = socket.gethostbyname(host_addr)
        host_port = int(host_port)

        # Connect to the host and send the modified header
        socket_.connect((host_ip, host_port))
        super().send(socket_, None)

    
class Response(HTTP):
    def __init__(self):
        super().__init__()

    #change content
    def handle_content(self):
        #handles the jpg 
        if "text" not in self.header.get("content-type", ""):
            return self.content

        if "gzip" in self.header.get("content-encoding", ""):
            data = gzip.decompress(self.content)
            data = data.decode("utf-8")
        else:
            data = self.content.decode("utf-8")

        if "Stockholm" in data:
            data = data.replace(" Stockholm", " Linköping")

        if "Smiley" in data:
            data = data.replace(" Smiley", " Trolly")

        if "./smiley.jpg" in data:
            data = data.replace("./smiley.jpg", "trolly.jpg")

        #print("\n" + data)
        new_content_length = len(data.encode("utf-8"))

        # Update the Content-Length header
        self.header["content-length"] = str(new_content_length)

        # Return the modified content
        return data.encode("utf-8")
        
        
def main():
    while True:
        # Accept the incoming request
        request_socket, address = server_socket.accept()
        
        # Initialize the Request object and receive the header and content of the request
        request = Request()
        request.receive_header(request_socket)    
        request.receive_content(request_socket)

        #request is invalid. Close the request socket and continue listening
        if request.header == None: 
           request_socket.close()
           continue
       
        # Initialize a new socket to communicate with the target server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
        # Send the request header and content to the target server
        request.send(client_socket)

        # Initialize the Response object and receive the header and content of the response from the target server
        response = Response()
        response.receive_header(client_socket)
        response.receive_content(client_socket)

        # Handle the content of the response (e.g., modify text and images)
        new_data = response.handle_content()
        
        # Send the modified response to the client
        response.send(request_socket, new_data)
        
        # Close the client and request sockets
        client_socket.close()
        request_socket.close()
        


if __name__ == "__main__":

    host_name = "127.0.0.1"
    port = 12345

    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # same local address can be used for multiple connections
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # bind the socket to a public host, and a port
    server_socket.bind((host_name, port))
    server_socket.listen()
    
    print("--- Starting proxy server ---")
    main()
   
 

   

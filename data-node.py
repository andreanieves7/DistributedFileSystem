###############################################################################
#
# Filename: data-node.py
# Author: Jose R. Ortiz and Andrea V. Nieves Rivera
#
# Description:
# 	data node server for the DFS
#

from Packet import *

import sys
import socket
import socketserver
import uuid
import os.path

def usage():
    print ("""Usage: python %s <server> <port> <data path> <metadata port,default=8000>""" % sys.argv[0])
    sys.exit(0)

def register(meta_ip, meta_port, data_ip, data_port):
    """Creates a connection with the metadata server and
    register as data node
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((meta_ip, meta_port))
    
    try:
        response = "NAK"
        sp = Packet()
        while response == "NAK":
            sp.BuildRegPacket(data_ip, data_port)
            sock.sendall(bytes(sp.getEncodedPacket(),encoding="utf-8"))
            response = sock.recv(1024)
            response = response.decode("utf-8")           
            if response == "DUP":
                print("Duplicate Registration")
            if response == "NAK":
                print("Registration ERROR")
                
    finally:
        print("Registration Success!")
        sock.close()
	

class DataNodeTCPHandler(socketserver.BaseRequestHandler):
    
    def handle_put(self, p):
        """Receives a block of data from a copy client, and 
		   saves it with an unique ID.  The ID is sent back to the
		   copy client.
		"""
        
        #self.request.send(b'OK')

		# Generates an unique block id.
        blockid = str(uuid.uuid1())
        fname = DATA_PATH + "\\"+blockid
        fsize = p.getFileInfo()[1]
		# Open the file for the new data block.  
        file = open(fname,"wb")
        self.request.sendall(b'OK')
        print("Receiving data...")
		# Receive the data block.
        total = 0
        while True:
            read = self.request.recv(1024)
            file.write(read)                      
            if read == b'OK' or not read or total >= fsize-1024:
                break  
            total += len(read)                   
        file.close()
		# Send the block id back
        self.request.sendall(bytes(blockid,encoding="utf-8"))
        print("Finished!")


		# Fill code
        
    def handle_get(self, p):
		
		# Get the block id from the packet
        blockid = p.getBlockID()
		# Read the file with the block id data
        fname = DATA_PATH + "\\"+blockid
        file = open(fname,"rb")
        fsize = os.path.getsize(fname)
        print("Sending data...")     
# =============================================================================
# # =============================================================================
# # 		# Send it back to the copy client.
        totalread = 0
        while True:
            read = file.read(1024)
            self.request.sendall(read)
            if totalread >= fsize:
                break           
            totalread += len(read)
        self.request.sendall(b'OK')
        print("Finished!")
        file.close()

    def handle(self):
        msg = self.request.recv(1024)
        print(msg)
        msg = msg.decode("utf-8")
        
        
        p = Packet()
        p.DecodePacket(msg)
        
        cmd = p.getCommand()
        if cmd == "put":
            self.handle_put(p)
            
        elif cmd == "get":
            self.handle_get(p)
		

if __name__ == "__main__":
    
    META_PORT = 8000
    if len(sys.argv) < 4:
        usage()
        
    try:
        HOST = sys.argv[1]
        PORT = int(sys.argv[2])
        DATA_PATH = sys.argv[3]
 
#i literally could never get the program to accept
#my arguments with this part on. i dont know how im
#supposed to send the arguments to this because
#i tried everything and it didnt work. if it doesnt work
#just comment this out

#im only leaving ths in to make it like its required
#to be

# =============================================================================
        if len(sys.argv > 4):
            META_PORT = int(sys.argv[4])        
# =============================================================================

        if not os.path.isdir(DATA_PATH):
            print("Error: Data path %s is not a directory." % DATA_PATH)
            usage()
    except:
        usage()


    register("localhost", META_PORT, HOST, PORT)
    server = socketserver.TCPServer((HOST, PORT), DataNodeTCPHandler)
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

###############################################################################
#
# Filename: copy.py
# Author: Jose R. Ortiz and Andrea V. Nieves Rivera
#
# Description:
# 	Copy client for the DFS
#
#

import socket
import sys
import os.path
import math

from Packet import *

def usage():
	print ("""Usage:\n\tFrom DFS: python %s <server>:<port>:<dfs file path> <destination file>\n\tTo   DFS: python %s <source file> <server>:<port>:<dfs file path>""" % (sys.argv[0], sys.argv[0]))
	sys.exit(0)

def copyToDFS(address, fname, path):
    """ Contact the metadata server to ask to copy file fname,
    get a list of data nodes. Open the file in path to read,
	    divide in blocks and send to the data nodes. 
        """

	# Create a connection to the data server
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(address)
        print("Socket created")
    except socket.error as err:
        print("socket creation failed. error %s" %(err))  
        sys.exit(0)

	# Read file

    try:
        fsize = os.path.getsize(fname)
    except:
        print("File to copy not found.")
        sock.close()
        sys.exit(0)

	# Create a Put packet with the fname and the length of the data,
	# and sends it to the metadata server 
    p = Packet()
    p.BuildPutPacket(path,fsize)
    sock.sendall(bytes(p.getEncodedPacket(),encoding="utf-8"))
    
    data = sock.recv(1024)
    data = data.decode("utf-8")
     
	# If no error or file exists
    if not data == "DUP":
        p.DecodePacket(data)
        dataList = p.getDataNodes()
	# Get the list of data nodes.
	# Divide the file in blocks
    
    #divide file code     
        div = math.ceil(fsize/len(dataList))
        remaining = fsize
        file = open(fname,'rb')

        blocklist = []
        print("Sending data...")
	# Send the blocks to the data servers
        for ip, port in dataList:
            datasock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            datasock.connect((ip,port))
            #aprox bytes to send
            #not exact
            tosend = min(remaining,div)
            p.BuildPutPacket(path,tosend)
            datasock.sendall(bytes(p.getEncodedPacket(),encoding="utf-8"))
            ok = datasock.recv(1024)
# =============================================================================
# # =============================================================================
         #data transfer code
         #receive ok to make sure data node is prepared to receive data
            if ok == b'OK':
                totalread = 0
                while True:
                    read = file.read(1024)
                    datasock.sendall(read)                      
                    if totalread >= (div-1024) or remaining <= 1024:
                        break                                                                            
                    totalread += len(read)
                    remaining -= len(read)
                datasock.sendall(b'OK')
    # # =============================================================================      
    # =============================================================================
               #save blockid and store it in blocklist
                blockid = datasock.recv(1024)
                blockid = blockid.decode("utf-8")
                block = (ip,port,blockid)
                blocklist.append(block)                
                datasock.close()
            else:
                file.close()
                datasock.close()
                sys.exit(0)
        file.close()
        # Notify the metadata server where the blocks are saved.
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        p.BuildDataBlockPacket(path, blocklist)
        sock.connect(address)
        sock.sendall(bytes(p.getEncodedPacket(),encoding="utf-8"))
        sock.close() 
        
	
    else:
        print("File already exists in server")
        sys.exit(0)
      
    

def copyFromDFS(address, fname, path):
    """ Contact the metadata server to ask for the file blocks of
	    the file fname.  Get the data blocks from the data nodes.
	    Saves the data in path.
	"""
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(address)
        print("Socket created")
    except socket.error as err:
        print("socket creation failed. error %s" %(err))
        sys.exit(0)

   	# Contact the metadata server to ask for information of fname
    p = Packet()
    p.BuildGetPacket(fname)
    sock.sendall(bytes(p.getEncodedPacket(),encoding="utf-8"))
    data = sock.recv(1024)
    data = data.decode("utf-8")
     
	# If no error or file exists
    # If there is no error response Retreive the data blocks
    if not data == "NFOUND":
        p.DecodePacket(data)
        dataList = p.getDataNodes()
        file = open(path,'wb')
        
        print("Receiving data...")
        for ip, port, blockid in dataList:
            datasock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            datasock.connect((ip,port))
            p.BuildGetDataBlockPacket(blockid)
            datasock.sendall(bytes(p.getEncodedPacket(),encoding="utf-8"))            
# =============================================================================
#         #data transfer code
            while True:
                read = datasock.recv(1024)               
                if read == b'OK':
                    break    
                file.write(read)
# =============================================================================
            datasock.close()
    	# Save the file
        print("File received.")
        file.close()
	
    

if __name__ == "__main__":
#	client("localhost", 8000)
	if len(sys.argv) < 3:
		usage()

	file_from = sys.argv[1].split(":")
	file_to = sys.argv[2].split(":")

	if len(file_from) > 1:
		ip = file_from[0]
		port = int(file_from[1])
		from_path = file_from[2]
		to_path = sys.argv[2]

		if os.path.isdir(to_path):
			print ("Error: path %s is a directory.  Please name the file." % to_path)
			usage()

		copyFromDFS((ip, port), from_path, to_path)

	elif len(file_to) > 2:
		ip = file_to[0]
		port = int(file_to[1])
		to_path = file_to[2]
		from_path = sys.argv[1]

		if os.path.isdir(from_path):
			print ("Error: path %s is a directory.  Please name the file." % from_path)
			usage()

		copyToDFS((ip, port), from_path, to_path)



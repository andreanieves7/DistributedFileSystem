###############################################################################
#
# Filename: meta-data.py
# Author: Jose R. Ortiz and Andrea V. Nieves Rivera
#
# Description:
# 	MySQL support library for the DFS project. Database info for the 
#       metadata server.
#
# Please modify globals with appropiate info.

from mds_db import *
from Packet import *
import sys
import socketserver


def usage():
	print ("""Usage: python %s <port, default=8000>""" % sys.argv[0] )
	sys.exit(0)


class MetadataTCPHandler(socketserver.BaseRequestHandler):

    def handle_reg(self,db,p):
        """Register a new client to the DFS  ACK if successfully REGISTERED
 			NAK if problem, DUP if the IP and port already registered
 		"""
        try:
            if db.AddDataNode(p.getAddr(),p.getPort()):
                self.request.sendall(b'ACK')
            else:
                self.request.sendall(b'DUP')
        except:
            self.request.sendall(b'NAK')
            
    def handle_list(self,db):
        """Get the file list from the database and send list to client"""
        try:
            p = Packet()
            p.BuildListResponse(db.GetFiles())
            self.request.sendall(bytes(p.getEncodedPacket(),encoding="utf-8"))
        except:
            self.request.sendall(b'NAK')	
            
            
    def handle_put(self, db, p):
        """Insert new file into the database and send data nodes to save
 		   the file.
 		"""
        info = p.getFileInfo()
        if db.InsertFile(info[0],info[1]):
            p.BuildPutResponse(db.GetDataNodes())
            self.request.sendall(bytes(p.getEncodedPacket(),encoding="utf-8"))
        else:
            self.request.sendall(b'DUP')
             
    def handle_get(self,db,p):
        """Check if file is in database and return list of
 			server nodes that contain the file.
 		"""
        fname = p.getFileName()
        fid,fsize = db.GetFileInfo(fname)
        
        if fsize:
            inode = db.GetFileInode(fname)
            p.BuildGetResponse(inode[1],inode[0])
            self.request.sendall(bytes(p.getEncodedPacket(),encoding="utf-8"))
        else:
            self.request.sendall(b'NFOUND')
            
    def handle_blocks(self,db,p):
        """Add the data blocks to the file inode"""
        fname = p.getFileName()
        fblocks = p.getDataBlocks()
        
        db.AddBlockToInode(fname,fblocks)
        
    def handle(self):
        # Establish a connection with the local database
        db = mds_db("dfs.db")
        db.Connect()
        
        # Define a packet object to decode packet messages
        p = Packet()
        
        # Receive a msg from the list, data-node, or copy clients
        msg = self.request.recv(1024)
        msg = msg.decode("utf-8")
        print(msg)
        
        # Decode the packet received
        p.DecodePacket(msg)
        
        # Extract the command part of the received packet
        cmd = p.getCommand()
        
        # Invoke the proper action 
        if cmd == "reg":
            # Registration client
            self.handle_reg(db,p)
        elif cmd == "list":
            # Client asking for a list of files
            self.handle_list(db)
        elif cmd == "put":
            # Client asking for servers to put data
            self.handle_put(db,p)
        elif cmd == "get":
            # Client asking for servers to get data
            self.handle_get(db, p)
        elif cmd == "dblks":
            # Client sending data blocks for file
            self.handle_blocks(db, p)
            
        db.Close()

if __name__ == "__main__":
    HOST, PORT = "", 8000

    if len(sys.argv) > 1:
    	try:
    		PORT = int(sys.argv[1])
    	except:
    		usage()

    server = socketserver.TCPServer((HOST, PORT), MetadataTCPHandler)
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

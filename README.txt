#============================================#
# ____     ___   ____  ___    ___ ___    ___ #
#|    \   /  _] /    ||   \  |   |   |  /  _]#
#|  D  ) /  [_ |  o  ||    \ | _   _ | /  [_ #
#|    / |    _]|     ||  D  ||  \_/  ||    _]#
#|    \ |   [_ |  _  ||     ||   |   ||   [_ #
#|  .  \|     ||  |  ||     ||   |   ||     |#
#|__|\_||_____||__|__||_____||___|___||_____|#
#============================================# 

This lovely package comes with the following files:
	• copy.py
	• createdb.py
	• data-node.py
	• ls.py
	• mds_db.py
	• meta-data.py
	• Packet.py
	• README.txt

Everything necessary to simulate a distributed file system on your computer.

Requirement: This is coded in Python 3.8.5. It utilizes the socketserver module. If you run this on a version
of python that uses SocketServer instead, it will not work. The library is essentially the same, but since
the names are different in capitalization, it won't work when calling it.

Here is a brief description of each script:

COPY.PY
	Client that connects to the meta-data server to send a request. This request can be a put or get request.
	Depending on the request, the server will return the corresponding data nodes and their connection info.
	The client then connects to each data node to send or receive data on the requested file.

CREATEDB.PY
	This script creates the SQL tables necessary for the meta-data server to manage data nodes and files.
	Creates file dfs.db. Delete dfs.db to reset the registered nodes and files.
	!!!!!THIS MUST BE RUN BEFORE THE SERVER!!!!!

DATA-NODE.PY
	Data nodes manage the actual bytes of data of the files. The client connects to these to receive the bytes
	of data or send bytes of data for the requested file. You can have many data-nodes open at a time, and the
	client will divide the bytes of the file by the amount of open data nodes. Every time you run a new one
	it will register to the meta-data server and database.

LS.PY
	Sends a request to the meta-data server to receive a list of all files currently in the database.

MDS_DB.PY
	Contains all the functions necessary to run the meta-data server and connect the script to the sql
	database.

META-DATA.PY
	Contains all the functions necessary to transfer data and manage the data in the database. Connects
	a file name to a list of data nodes which contain the data in bytes of that file. 

PACKET.PY
	Contains the Packet object and its methods. Communication between scrips relies on the format of these
	packets.

README.TXT
	You're reading this right now. It's the instructions.



 #     # ####### #     #    ####### #######    #     #  #####  ####### 
 #     # #     # #  #  #       #    #     #    #     # #     # #       
 #     # #     # #  #  #       #    #     #    #     # #       #       
 ####### #     # #  #  #       #    #     #    #     #  #####  #####   
 #     # #     # #  #  #       #    #     #    #     #       # #       
 #     # #     # #  #  #       #    #     #    #     # #     # #       
 #     # #######  ## ##        #    #######     #####   #####  ####### 
                                                                       
NOTE: Make sure all files are in the same folder, as they all require the use of Packet.py. If you wish to run the
scripts from different folders, make sure there is a copy of Packet.py in every used directory.


STARTING UP THE SERVER

1. Run createdb.py where you want to create the database file. If you already have a database file, delete it first.
	python createdb.py
2. Run meta-data.py 
	python meta-data.py <port, default=8000>
3. Run data-node.py from a separate command prompt or window. Run as many as you wish to have, with a different port
	and data storage folder each.
	python data-node.py <server address, ex:localhost> <port> <data path folder> <metadata port,default=8000, only include this if you ran meta-data.py with a port other than 8000>

INTERACTING WITH THE SERVER

1. Inserting a new file to the server utilizing the copy client.
	Run the following code from a separate command prompt or window. Utilize localhost for <server> and the meta-data port number for <port>.
	For <source file>, write the location and name of the file to transfer. In <dfs file path> write the name you would like the file to have 
	in the database. 
		python copy.py <source file> <server>:<port>:<dfs file path>
	The copy client will receive a list of open and registered data nodes from the meta-data server and connect to each to transfer part of the data. 
                                      
2. Receiving a file from the server utilizing the copy client.
	Run the following code from a separate command prompt or window. Utilize localhost for <server> and the meta-data port number for <port>.
	For <dfs file path>, write the name of the file in the dfs database. In <destination file> write the name you would like to save the file as. 
		python copy.py <server>:<port>:<dfs file path> <destination file>
	The copy client will receive a list of data nodes associated with that file from the meta-data server and connect to each to receive data.

3. Listing the files in the DFS utilizing the list client.
	Run the following code from a separate command prompt or window.  Utilize localhost for <server> and the meta-data port number for <port>.
	It will print out a list of every file name registered in the database along with their size in bytes.
		python ls.py <server>:<port, default=8000> 


  ____ ____  _____ ____ ___ _____ ____  
  / ___|  _ \| ____|  _ \_ _|_   _/ ___| 
 | |   | |_) |  _| | | | | |  | | \___ \ 
 | |___|  _ <| |___| |_| | |  | |  ___) |
  \____|_| \_\_____|____/___| |_| |____/ 
                                        
ASCII art was made with https://patorjk.com/software/taag
I also met with another student with the intent of discussing the project, but since nothing at the university was open due to 
air conditioning problems, we ended up not discussing anything. 

import sqlite3
import socket
import bcrypt

# Connects to the database
try:

	# Connect to DB and create a cursor
	sqliteConnection = sqlite3.connect('server1.db')
	cursor = sqliteConnection.cursor()
	print('DB Init')

	# Write a query and execute it with cursor
	query = 'select sqlite_version();'
	cursor.execute(query)

	# Fetch and output result
	result = cursor.fetchall()
	print('SQLite Version is {}'.format(result))

	# Close the cursor

# Handle errors
except sqlite3.Error as error:
	print('Error occurred - ', error)

# Hosts and port used for the clients to connect
host = '127.0.0.1'
port = 50001

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((host, port))
serverSocket.listen()

conn, addr = serverSocket.accept()
print("Connected from: ", str(addr))

logIn = False
UserName = False
password = False

while logIn == False:
		entry = """Please enter an option:
		1. Log in
		2. Sign up
		3. Quit
		"""
		conn.send(entry.encode())
		choice = conn.recv(1024).decode()
		if int(choice) == 1:
			conn.send("Please enter a username".encode())
			while UserName == False:
				data = conn.recv(1024).decode()
				query = 'SELECT * FROM details'
				cursor.execute(query)
				userCheck = cursor.fetchall()
				lengthUserCheck = int(len(userCheck))
				for i in range(0, lengthUserCheck):
					userName = userCheck[i][0]
					if userName == data:
						UserName = True
						conn.send("Now please enter your password".encode())
						while password == False:
							data = conn.recv(1024).decode()
							for i in range(0, lengthUserCheck):
								passCheck = userCheck[i][1]
								passSalt = userCheck[i][2]
								#check = bcrypt.hashpw(passCheck, passSalt)
								#encodedPass = passCheck.encode()
								if bcrypt.hashpw(data.encode(), passSalt) == passCheck:
									password = True
									logIn = True
									correctSend = "Correct Password! Welcome to the chat app!"
									conn.send(correctSend.encode())
									break
							if password == False:
								conn.send("Please try again".encode())
						break
				if UserName == False:
					conn.send("Please try again".encode())
		elif int(choice) == 2:
			userExists = False
			while userExists == False:
				conn.send("Enter your new username".encode())
				newUser = conn.recv(1024).decode()
				query = 'select * from details'
				cursor.execute(query)
				newUserCheck = cursor.fetchall()
				lengthDatabase = int(len(newUserCheck))
				for i in range(0, lengthDatabase):
					existingUserName = newUserCheck[i][0]
					if newUser == existingUserName:
						conn.send("That username already exists. PLease choose again".encode())
						userExists = False
						break
					else:
						userExists = True
				if userExists == True:
					conn.send("Please enter a password".encode())
					newPassword = conn.recv(1024).decode()
					salt = bcrypt.gensalt()
					hashedPassword = bcrypt.hashpw(newPassword.encode('utf-8'), salt)
					query = 'INSERT INTO details(username, password, hash) VALUES(?, ?, ?)'
					cursor.execute(query, (newUser, hashedPassword, salt))
					sqliteConnection.commit()
					logIn = True
					break			
		elif int(choice) == 3:
			quit()

#conn.send("Welcome to the chat app!!!!".encode())
newChat = conn.recv(1024).decode()
print(newChat)
if newChat =='user':
	query = "SELECT * FROM details"
	cursor.execute(query)
	result = cursor.fetchall()
	conn.send(str(len(result)).encode())
	responseData = result
else:
	responseData = "message Received"
	conn.send(responseData.encode())

serverSocket.close()
cursor.close()
sqliteConnection.close()
# Close DB Connection irrespective of success
if sqliteConnection:
	sqliteConnection.close()
	print('SQLite Connection closed')


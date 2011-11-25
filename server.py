from twisted.internet import protocol, reactor
from twisted.protocols import basic

class IMProtocol(basic.LineReceiver):
	def authorize(self, name):
		if name in self.factory.clients:
			self.send("User already logged in")
		else:
			self.deauthorize()
			self.name = name
			self.factory.clients[name] = self
			self.send("Successfully logged in")
			self.authorized = 1
	
	def connectionMade(self):
		self.factory.numClients += 1
		self.authorized = 0
		
		if self.factory.numClients > 50:
			self.disconnect("Too many connections")
		else:
			self.send("Connection accepted, type HELP for information on usage")
	
	def connectionLost(self, reason):
		self.factory.numClients -= 1
	
	def deauthorize(self):
		if self.authorized:
			self.factory.clients.pop(self.name)
	
	def disconnect(self, reason):
		self.deauthorize()
		self.send(reason)
		self.transport.loseConnection()
	
	def lineReceived(self, line):
		if len(line) < 1:
			return 0
		
		line = line.strip()
		command = line.split()[0].lower()
		args = line.split()[1:]
		
		print command
		
		if command == "quit":
			self.disconnect("Closing connection")
		elif command == "user":
			if len(args) < 1:
				self.send("No username provided")
				return 0
			
			self.authorize(args[0])
		elif command == "help":
			self.send("No help files available")
		elif command == "users":
			self.send("Active users:")
			
			for user in self.factory.clients:
				self.send(user)
		elif command == "im":
			if not self.authorized:
				return 0
			
			if len(args) < 1:
				self.send("No receiver specified")
				return 0
			elif len(args) < 2:
				self.send("No message specified")
				return 0
			else:
				if args[0] in self.factory.clients:
					self.factory.clients[args[0]].send(self.name + ": " + " ".join(args[1:]))
				else:
					self.send("Receiver doesn't exist")
		else:
			if not self.authorized:
				return 0
			
			for client in self.factory.clients:
					self.factory.clients[client].send(self.name + ": " + line);
	
	def send(self, message):
		self.transport.write(message + "\r\n")

class IMFactory(protocol.Factory):
	protocol = IMProtocol
	
	def __init__(self):
		self.numClients = 0
		self.clients = dict()

reactor.listenTCP(7000, IMFactory())
reactor.run()
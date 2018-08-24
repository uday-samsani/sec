import socket
import sys
import threading
import pickle
import getopt

print_lock = threading.Lock()


def print_safe(*args, **kwargs):
    with print_lock:
        print(*args, **kwargs)


class Server:
    serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    users = []

    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.peers = {'admin':self.serverSock.getsockname()}
        print_safe(' [*] Server starting ....', end='')
        self.serverSock.bind((self.address, self.port))
        self.serverSock.listen(5)
        print_safe('\r [*] Server listening on {0}:{1} ....'.format(self.address, str(self.port)))

        self.run()

        self.serverSock.close()

    def broadcastMsg(self, connection, msg):
        """Broadcast a message to a connection."""

        connection.send(msg)

    def handler(self, connection, address):
        """Handles all data and services."""

        while True:
            dataStr = connection.recv(4086)
            if dataStr:
                # checking peers and sending only if we have receive data
                data = pickle.loads(dataStr)

                # broad casting message to a user
                if len(data[0]):

                    # loading peerStr from dataStr we got (user, msg, peersStr)
                    self.peers={**self.peers,**data[2]}
                    print_safe('******')
                    print_safe('recevied data is {}'.format(data))
                    print_safe('******')
                    print_safe(self.peers)
                    print_safe('******')
                    # else:
                        # self.peers = pickle.loads(data[2])

                    # Broadcasting message to all
                    if data[0] == 'all':
                        for userConnection in self.users:
                            self.broadcastMsg(userConnection[0], pickle.dumps((data[0], data[1], self.peers)))

                    # broadcasting message to single user to group
                    elif self.peers[data[0]] != ():
                        for userConnection in self.users:
                            if userConnection[1] == self.peers[data[0]]:

                                # sender = (list(self.peers.keys())[list(self.peers.values()).index((connection, address))])
                                self.broadcastMsg(userConnection[0], pickle.dumps((data[0], data[1], self.peers)))

                        # Why did i do this??
                        # self.broadcastMsg(connection, msg=data)
            else:
                print_safe(' [*] {0}:{1} disconnected'.format(address[0], str(address[1])))
                self.users.remove((connection, address))
                break

    def run(self):
        """RUN will start running all services of server"""

        try:
            while True:
                connection, address = self.serverSock.accept()
                serverRunThread = threading.Thread(target=self.handler, args=(connection, address))
                serverRunThread.daemon = True
                serverRunThread.start()

                self.users.append((connection, address))
                print_safe(' [*] {0}:{1} connected'.format(address[0], str(address[1])))

        except KeyboardInterrupt:
            self.serverSock.close()
            sys.exit(0)

    def prompt(self):
        """Read Eval print_safe Loop Prompt like python."""
        pass


class Client:
    clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peers = {}

    def __init__(self, address, port, user):
        self.address = address
        self.port = port
        self.user = user
        print_safe(' [*] Trying to connect to {}:{}'.format(self.address, str(self.port)), end='')
        self.clientSock.connect((self.address, self.port))
        self.peers[user] = self.clientSock.getsockname()
        self.sendMsg('{0} is Online\n.'.format(self.user), 'all')
        print_safe('\r [*] Connected to server on {}:{}'.format(self.address, str(self.port)))



        self.run()

        self.clientSock.close()

    def sendMsg(self, msg, *users):
        """Send message to a user('s)"""

        if len(users) == 1 and users[0] == 'all':
            msg = (users[0], msg, self.peers)
            print_safe('\nsending message {}'.format(msg))
            msg = pickle.dumps(msg)
            self.clientSock.send(msg)

    def broadcastMsg(self):
        """Broadcast message to every user in server"""

        pass

    def recvMsg(self):
        """Receive Message from server"""
        try:
            while True:
                dataStr = self.clientSock.recv(2048)
                data = pickle.loads(dataStr)
                print('data out given by server is  {0}'.format(data))
                self.peers = {**self.peers, **data[2]}
                if not dataStr:
                    break
                print_safe('{0} >'.format(dataStr[0])+str(dataStr[2]))
        except KeyboardInterrupt:
            self.clientSock.close()
            sys.exit(0)

    def run(self):
        """This will run all services of client."""

        try:
            clientRunThread = threading.Thread(target=self.prompt)
            clientRunThread.daemon = True
            # clientRecvThread = threading.Thread(target=self.recvMsg)
            # clientRecvThread.daemon = True

            clientRunThread.start()
            self.recvMsg()

        except KeyboardInterrupt:
            self.clientSock.close()
            sys.exit(0)

    def prompt(self):
        """Read Eval print_safe Loop Prompt like python."""

        print_safe('''
           Commands :
              who                         :   print users who are online.
              help or commands            :   print this message.
              @[username] [message]       :   Send message to a user( \'s).
              @all [message]              :   Send message to all users who are online.
              quit or exit                :   Quit from SEC.
        ''')

        while True:
            command = input('>'.format(self.user))

            # WHO command : To see who is online
            if command == 'who':
                print_safe('\n'+'*'*20+'\n')
                print_safe('Online : ')
                for peer in self.peers:
                    print_safe(' {} '.format(peer),end='')
                print_safe('\n\n'+'*'*20+'\n')

            # HELP or COMMANDS command : To display commands or help
            elif command == 'help' or command == 'commands':

                print_safe('''
            Commands :
                  who                         :   print users who are online.
                  help or commands            :   print this message.
                  @[username] [message]       :   Send message to a user( \'s).
                  @all [message]              :   Send message to all users who are online.
                  quit or exit                :   Quit from SEC.
                            ''')

            # Terminate Program
            elif command == 'quit' or command == 'exit':
                print_safe(' [*] Closing connection')
                self.clientSock.close()
                print_safe(' [*] Connection closed')
                sys.exit(0)

            # send to all
            elif command[0:4] == '@all':
                msg = command[5:]
                self.sendMsg(msg, 'all')

            # SEND command : Direct Message a user
            elif command[0] == '@':
                user = ''
                index = 0
                for index in range(1, len(command[1:])):
                    if command[index] != ' ':
                        user += command[index]
                    else:
                        break
                msg = command[index + 1:]
                self.sendMsg(msg, user)

            else:
                print_safe(' [***] Invalid Option')


def usage():
    """Displays basic usage of SEC."""

    print_safe(' SEC : Simple Encrypted Chat')
    print_safe()
    print_safe(' Description:')
    print_safe('     SEC is a simple chat service in which you can chat in channels. SEC\'s main goal is privacy.')
    print_safe(' Author : Uday Samsani')
    print_safe()
    print_safe('     Usage : ')
    print_safe('         -h, --help              :   print_safes this usage information.')
    print_safe('         -a, --address           :   Connect to this address.')
    print_safe('         -p, --port              :   Connect to through this port.')
    print_safe('         -u, --user              :   Connect as this user.')
    print_safe('         -V, --version           :   print_safe version of the SEC using and exit.')
    print_safe()
    print_safe('     Examples:')
    print_safe('         python3 sec.py -a 192.168.1.1 -p 12345')
    print_safe('         python3 sec.py -a 192.168.1.1 -p 12345 -u uday')
    print_safe('         python3 sec.py -v')
    print_safe()
    sys.exit(0)


def version():
    """Displays the version of SEC."""

    print_safe(' SEC : Simple Encrypted Chat')
    print_safe('     Version : 1.0 (alpha)')
    sys.exit(0)


def main():
    """Main Function."""

    address = '0.0.0.0'
    port = 4444
    user = ''
    opts = ()

    if len(sys.argv) > 1:
        try:
            opts, args = getopt.getopt(sys.argv[1:], 'ha:p:u:V', ['help', 'address', 'port', 'user', 'version'])
        except getopt.GetoptError as error:
            print_safe('[***]'+str(error))
            print_safe()
            usage()
        for o, a in opts:
            if o in ('-h', '--help'):
                usage()
            elif o in ('-a', '--address'):
                address = a
            elif o in ('-p', '--port'):
                port = int(a)
            elif o in ('-u', '--user'):
                user = a
            elif o in ('-V', '--version'):
                version()
            else:
                assert False, "Invalid Option"
    else:
        usage()

    if user != '' and address != '':
        client = Client(address, port, user)
        client.run()
    else:
        server = Server(address, port)
        server.run()


if __name__ == '__main__':
    main()

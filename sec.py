import socket
import sys
import threading
import pickle
import getopt

print_lock = threading.Lock()
peers = {}


def print_safe(*args, **kwargs):
    with print_lock:
        print(*args, **kwargs)


class Server:
    serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    users = []
    global peers

    def __init__(self, address, port):
        self.address = address
        self.port = port
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
            data = connection.recv(2048)
            if data:
                # checking peers and sending only if we have receive data
                dataStr = pickle.loads(data)
                for user in self.users:
                    if user[0] != connection:
                        # broad casting message to a user
                        if len(dataStr[0]) == 1:

                            # Searching for the connection socket of user given in dataStr.
                            if peers[dataStr[0]]:
                                for userConnection in self.users:
                                    if userConnection[1] == peers[dataStr[0][2]]:
                                        self.broadcastMsg(userConnection, data)

                            self.broadcastMsg(connection, msg=data)
            elif not data:
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
    global peers

    def __init__(self, address, port, user):
        self.address = address
        self.port = port
        self.user = user
        print_safe(' [*] Trying to connect to {}:{}'.format(self.address, str(self.port)), end='')
        self.clientSock.connect((self.address, self.port))
        if user not in peers:
            peers[user] = self.clientSock.getsockname()
        print_safe('\r [*] Connected to server on {}:{}'.format(self.address, str(self.port)))

        self.run()

        self.clientSock.close()

    def sendMsg(self, msg, *users):
        """Send message to a user('s)"""

        if len(users) == 1:
            msg = (users, msg)
            msg = pickle.dumps(msg)
            self.clientSock.send(msg)

    def broadcastMsg(self):
        """Broadcast message to every user in server"""

        pass

    def recvMsg(self):
        """Receive Message from server"""

        while True:
            data = self.clientSock.recv(2048)
            dataStr = pickle.loads(data)
            if not data:
                break
            print_safe('{0} >'.format(dataStr[0])+dataStr[1])

    def run(self):
        """This will run all services of client."""

        try:
            clientRunThread = threading.Thread(target=self.prompt)
            clientRunThread.daemon = True
            clientRunThread.start()

        except KeyboardInterrupt:
            self.clientSock.close()

    def prompt(self):
        """Read Eval print_safe Loop Prompt like python."""

       # print_safe(' Commands : ')
       # print_safe('     who                         :   print users who are online.')
       # print_safe('     help or commands            :   print this message.')
       # print_safe('     @[username] [message]       :   Send message to a user( \'s).')
       # print_safe('     @all [message]              :   Send message to all users who are online.')
       # print_safe()
        while True:
            command = input('>'.format(self.user))

            # SEND command : Direct Message a user
            if command[0] == '@':
                msg = ''
                user = ''
                for index in range(1, len(command[1:])):
                    if command[index] != ' ':
                        user += command[index]
                    else:
                        msg = bytes(command[index+1:], 'utf-8')
                self.sendMsg(user, msg)

            # WHO command : To see who is online
            elif command == 'who':
                pass

            # HELP or COMMANDS command : To display commands or help
            elif command == 'help' or command == 'commands':
                pass

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

import socket
import sys
import threading
import pickle

class usernameException(Exception):
    pass


class Server:
    connections=[]
    peers=[]
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    def __init__(self, port):
        self.sock.bind(('0.0.0.0', int(port)))
        self.sock.listen(1)

    def handler(self, c, a):
        while True:
            dataStr = c.recv(2048)
            if dataStr:
                msgData = pickle.loads(dataStr)

            try:

                if msgData[0] not in self.peers:
                    self.peers.append((c, a[0], msg)
                else:
                    raise usernameException

            except usernameException:
                sys.exit(0)

            for peer in self.peers:
                if peer[0] != c:
                    peer[0].send(dataStr)
                if not dataStr:
                    print('{0} disconnected from server'.format(peer[2]))
                    self.peers.remove((c,a[0],msgData[0]))
                    break

    def run(self):
        try:
            while True:
                c, a = self.sock.accept()
                sThread = threading.Thread(target=self.handler,args=(c,a))
                sThread.daemon = True
                sThread.start()

        except KeyboardInterrupt:
            self.sock.close()


class Client:
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    def __init__(self, address, port, username):
        self.address=address
        self.username=username
        self.sock.connect((self.address,int(port)))
        try:
            cThread = threading.Thread(target=self.sendMsg)
            cThread.daemon = True
            cThread.start()

            self.recvMsg()

        except KeyboardInterrupt:
            self.sock.close()

    def broadcastMsg(self, username, msg):
        msgData = (self.username, msg)
        dataStr = pickle.dumps(msgData)
        self.sock.send(dataStr)

    def sendMsg(self):
        while True:
            msgData = (self.username,input('[{}]>>'.format(self.username)))
            dataStr = pickle.dumps(msgData)
            self.sock.send(dataStr)

    def recvMsg(self):
        while True:
            dataStr = self.sock.recv(2048)

            if not dataStr:
                break

            msgData = pickle.loads(dataStr)
            if len(msgData) == 3:
                if msgData[1] == 'exception':
                    print(' [***] ' + msgData[2])
                    print('Logging out')
                    sys.exit(0)

            elif len(msgData) == 2:
                if msgData[0] != self.username:
                    print('\r[{}]>>'.format(msgData[0]) + msgData[1] + '\n[{}]>>'.format(self.username), end='')
                else:
                    pass

def main():
    if len(sys.argv)==2:
        server = Server(sys.argv[1])
        server.run()
    else:
        client = Client(sys.argv[1], sys.argv[2], sys.argv[3])

if __name__ == '__main__':
    main()
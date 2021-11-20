from xmlrpc.client import ServerProxy

if __name__ == '__main__':
    s = ServerProxy("http://127.0.0.1:8080")
    s.put("A","mensagem")
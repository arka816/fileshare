import socket
import json
import os
import math
import sys

FILE_BUFFER_SIZE=2048*1024
s=socket.socket()
port=6666

try:
    s.bind(('', port))
    s.listen(4)
except:
    s.close()
    sys.exit()

dirname='D:\\movies\\'

def path_to_json(path):
    try:
        d={'name':os.path.basename(path), 'date': os.path.getmtime(path)}
        if os.path.isdir(path):
            d['type']="directory"
            dirlist=os.listdir(path)
            dirlist.sort(reverse=True)
            d['children']=[path_to_json(os.path.join(path, x)) for x in dirlist]
        else:
            d['type']="file"
            fileSize = math.ceil(os.path.getsize(path)/(1024*1024))
            d['size']=str(fileSize) + " MB"
    except OSError as err:
        print(err)
    return d

while True:
    c, addr=s.accept()
    req=c.recv(1024).decode('utf-8')
    req=json.loads(req)
    if req['type'] == "filelist":
        #GENERATE FILE LIST FOR E DRIVE
        dirtree=json.dumps(path_to_json(dirname)).encode()
        c.send(dirtree)
    elif req['type'] == "file":
        #SEND FILE TO THE CLIENT
        path=dirname+req['path']
        if os.path.isdir(path):
            print("directory")
        else:
            print("sending file from: "+os.path.basename(path))
            f=open(path, 'rb')
            l=f.read(FILE_BUFFER_SIZE)
            while l:
                c.sendall(l)
                l=f.read(FILE_BUFFER_SIZE)
            f.close()
    c.close()
    
s.close()

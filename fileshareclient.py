import tkinter
from tkinter import ttk
import socket
import json
import time
import math
import sys

localdirectory="S:\\"
serveraddress="192.168.0.1"
port=6666
BUFF_SIZE=2048*1024

def receiveFile(sock, filename, fileSize):
    f=open(localdirectory+filename, "wb")
    percent=0
    while True:
        part=sock.recv(BUFF_SIZE)
        percent += 100 * float(len(part)/(1024*1024*fileSize))
        if percent <= 100:
            sys.stdout.write("\rDownloaded: " + str(math.ceil(percent)) + "%")
            sys.stdout.flush()
        else:
            sys.stdout.write("\rDownloaded: 100%")
            sys.stdout.flush()
        f.write(part)
        if not part:
            break
    sys.stdout.write("\rDownloaded: 100%")
    sys.stdout.flush()
    print("")
    f.close()
    sock.close()
    return
        
def recvall(sock):
    data=b''
    while True:
        part=s.recv(BUFF_SIZE)
        data += part
        if not part:
            break
    return data.decode('utf-8')

def generateFileTree(tree, parentnode, obj):
    name=obj['name']
    if name=="":
        name="root"
    if obj['type']=='file':
        tree.insert(parentnode, 0, iid=None, text=name, values=(obj['size'], time.ctime(obj['date'])))
    elif obj['type']=='directory':
        thisdir=tree.insert(parentnode, 0, iid=None, text=name, values=('', time.ctime(obj['date'])))
        for jsonobj in obj['children']:
            generateFileTree(tree, thisdir, jsonobj)
    return

    
#FETCH DIRECTORY TREE
s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((serveraddress, port))
req={"type":"filelist", "drive": "E"}
req=json.dumps(req)
s.send(req.encode())
res=recvall(s)
res=json.loads(res)
s.close()


#CODE FOR THE GUI
top=tkinter.Tk()
top.title("Share File (Client)")
tree=ttk.Treeview(master=top)

def downloadFile(item_iid, filename):
    fileSize=tree.item(item_iid)['values'][0].split()[0]
    path = "\\" + filename
    parent_iid=tree.parent(item_iid)
    while(parent_iid):
        nodename=tree.item(parent_iid)['text']
        if nodename!="root":
            path = "\\" + nodename + path
        parent_iid=tree.parent(parent_iid)
    path=path[1:]
    print("requesting file: " + path)
    req={"type": "file", "path": path}
    req=json.dumps(req)
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((serveraddress, port))
    s.send(req.encode())
    receiveFile(s, filename, int(fileSize))
    return

def downloadDir(item_iid, dirname, children):
    for child_iid in children:
        subchildren=tree.get_children(child_iid)
        if len(subchildren) == 0:
            downloadFile(child_iid, tree.item(child_iid)['text'])
        else:
            downloadDir(child_iid, tree.item(child_iid)['text'], subchildren)
    return
    

def decideDownload(event):
    #DECIDE WHETHER SINGLE FILE DOWNLOAD OR DIRECTORY DOWNLOAD
    item_iid=tree.selection()[0]
    dirname=tree.item(item_iid)['text']
    children=tree.get_children(item_iid)
    if len(children) == 0:
        #DOWNLOAD SINGLE FILE
        downloadFile(item_iid, dirname)
    else:
        #DOWNLOAD ENTIRE DIRECTORY
        downloadDir(item_iid, dirname, children)
        

tree["columns"]=("one", "two")
tree.column('#0', width="260")
tree.column("one", width="160")
tree.column("two", width="200")
tree.heading("#0", text="file name")
tree.heading("one", text="file size")
tree.heading("two", text="date modified")

generateFileTree(tree, "", res)
tree.bind("<Double-1>", decideDownload)

tree.pack(side=tkinter.LEFT, expand=0, fill=tkinter.BOTH)
top.mainloop()

import socket               # Import socket module
import time                 # Import time module
import platform             # Import platform module to get our OS
import os
import pickle
import random
from _thread import *
import threading
import sys
import Simple_FTP_receiver
import Simple_FTP_sender

rcv_rfc_num = ''  #record rfc_num for rdt_recv()
rcv_rfc_title = ''

def get_filename(rfc_num):
    global rcv_rfc_title
    current_path = os.getcwd()
    OS = platform.system()
    if OS == "Windows":  # determine rfc path for two different system
        rfc_path = current_path + "\\rfc\\"
    else:
        rfc_path = current_path + "/rfc/"
    files = os.listdir(rfc_path)
    m = rfc_num.split()
    rfc_num = "".join(m)
    for item in files:
        if str(rfc_num) in item:
            return rfc_path + item
    return rfc_path + "rfc" + str(rfc_num) + ", " +str(rcv_rfc_title)+".pdf"

def p2p_get_request(rfc_num, peer_host, peer_upload_port):
    global upload_socket
    global rcv_rfc_num
    rcv_rfc_num = rfc_num 
    data = p2p_request_message(rfc_num, host)
    data = pickle.dumps(data)
    upload_socket.sendto(data,(peer_host, int(peer_upload_port)))

# display p2p response message
def p2p_response_message(rfc_num): # the parameter "rfc_num" should be str
    filename = "rfc"+str(rfc_num)+".txt"
    current_time = time.strftime("%a, %d %b %Y %X %Z", time.localtime())
    OS = platform.system()
    m = filename.split()
    filename = "".join(m)
    current_path = os.getcwd()
    if OS == "Windows":  # determine rfc path for two different system
        filename = "rfc\\" + filename
    else:
        filename = "rfc/" + filename
    #print (current_path+"/"+filename)
    #print (os.path.exists(current_path+"/"+filename))
    if os.path.exists(filename) == 0:
        status = "404"
        phrase = "Not Found"
        message = "P2P-CI/1.0 "+ status + " "+ phrase + "\n"\
                    "Date:" + current_time + "\n"\
                    "OS: "+str(OS)+"\n"
    else:
        status = "200"
        phrase = "OK"
        txt = open(filename)
        data = txt.read()
        last_modified = time.ctime(os.path.getmtime(filename))
        content_length = os.path.getsize(filename)
        message = ["P2P-CI/1.0 "+ status + " "+ phrase + "\n"\
                  "Date: " + current_time + "\n"\
                  "OS: " + str(OS)+"\n"\
                  "Last-Modified: " + last_modified + "\n"\
                  "Content-Length: " + str(content_length) + "\n"\
                  "Content-Type: text/text \n", str(data)]
                  #+ str(data)

    return message

# display p2p request message
def p2p_request_message(rfc_num, host):
    OS = platform.platform()
    message = "GET RFC "+str(rfc_num)+" P2P-CI/1.0 \n"\
              "Host: "+str(host)+"\n"\
              "OS: "+str(OS)+"\n"
    return message


# display p2s request message for ADD method
def p2s_add_message(rfc_num, host, port, title):  # for ADD
    message = "ADD" + " RFC " + str(rfc_num)+" P2P-CI/1.0 \n"\
              "Host: " + str(host)+"\n"\
              "Port: " + str(port)+"\n"\
              "Title: " + str(title)+"\n"
    return [message, rfc_num, host, port, title]


# display p2s request message for LOOKUP method
def p2s_lookup_message(rfc_num, host, port, title, get_or_lookup):  # LOOKUP method
    message = "LOOKUP" + " RFC " + str(rfc_num)+" P2P-CI/1.0 \n"\
              "Host: " + str(host)+"\n"\
              "Port: " + str(port)+"\n"\
              "Title: " + str(title)+"\n"
    return [message, rfc_num, get_or_lookup]


#display p2s request message for LIST methods
def p2s_list_request(host, port):
    message = "LIST ALL P2P-CI/1.0 \n"\
              "Host: "+str(host)+"\n"\
              "Port: "+str(port)+"\n"
    return message


#get the list of the local rfcs
def get_local_rfcs():
    rfcs_path = os.getcwd() + "/rfc"
    rfcs_num = [num[num.find("c")+1:num.find(",")] for num in os.listdir(rfcs_path) if 'rfc' in num]
    return rfcs_num

def get_local_rfcs_title():
    rfcs_path = os.getcwd() + "/rfc"
    rfcs_title = [title[title.find(" ")+1:title.find(".")] for title in os.listdir(rfcs_path) if 'rfc' in title]
    return rfcs_title

#pass peer's hostname, port number and rfc_num, rfc_title
def peer_information():
    keys = ["RFC Number", "RFC Title"]
    rfcs_num = get_local_rfcs()
    rfcs_title = get_local_rfcs_title() 
    for num, title in zip(rfcs_num, rfcs_title):
        entry = [num, title]
        dict_list_of_rfcs.insert(0, dict(zip(keys, entry)))
    return [upload_port_num, dict_list_of_rfcs]  # [port, rfcs_num, rfcs_title]


upload_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#print("UPLOAD PORT: ", upload_port_num)
upload_port_num = 65000+random.randint(1, 500)  # generate a upload port randomly in 65000~65500
upload_socket.bind(('', upload_port_num))
dict_list_of_rfcs = []  # list of dictionaries of RFC numbers and Titles.
s=socket.socket()          # Create a socket object
#s.setsockopt(socket.SOL_SOCKET, socket.SO_RESUEDADDR, 1)
host = socket.gethostname()  # Get local machine name
#host = "10.139.62.163"
port = 7734                  # Reserve a port for your service.
s.connect((host, port))
data = pickle.dumps(peer_information())  # send all the peer information to server
s.send(data)
data = s.recv(1024)
print(data.decode('utf-8'))
s.close


def print_combined_list(dictionary_list, keys):
    for item in dictionary_list:
        print(' '.join([item[key] for key in keys]))

def get_user_input(strr, i):
    user_input = input("> Enter ADD, LIST, LOOKUP, GET, or EXIT:  \n")
    if user_input == "EXIT":
        data = pickle.dumps("EXIT")
        #s.send(bytes('1', "utf-8"))
        s.send(data)
        #stopped = threading.Event()
        #time.sleep(3)
        #threading.Timer(1, stopped.set).start()
        s.close                     # Close the socket when done
        #sys.exit()
        os._exit(1)
    elif user_input == "ADD":
        user_input_rfc_number = input("> Enter the RFC Number: ")
        user_input_rfc_title = input("> Enter the RFC Title: ")
        data = pickle.dumps(p2s_add_message(user_input_rfc_number, host, upload_port_num, user_input_rfc_title))
        s.send(data)
        server_data = s.recv(1024)
        print(server_data.decode('utf-8'))
        get_user_input("hello", 1)
    elif user_input == "LIST":
        data = pickle.dumps(p2s_list_request(host, port))
        s.send(data)
        server_data = s.recv(1024)
        print(server_data.decode('utf-8'), end="")

        new_data = pickle.loads(s.recv(1000000))
        print_combined_list(new_data[0], new_data[1])

        get_user_input("hello", 1)
    elif user_input == "GET":
        user_input_rfc_number = input("> Enter the RFC Number: ")
        user_input_rfc_title = input("> Enter the RFC Title: ")
        global rcv_rfc_title
        rcv_rfc_title = str(user_input_rfc_title)
        data = pickle.dumps(p2s_lookup_message(user_input_rfc_number, host, port, user_input_rfc_title, "0"))
        s.send(data)
        server_data = pickle.loads(s.recv(1024))
        if not server_data[0]:
            print(server_data[1])
        else:  
            p2p_get_request(str(user_input_rfc_number), server_data[0]["Hostname"], server_data[0]["Port Number"])
        #get_user_input("hello", 1)
    elif user_input == "LOOKUP":
        user_input_rfc_number = input("> Enter the RFC Number: ")
        user_input_rfc_title = input("> Enter the RFC Title: ")
        data = pickle.dumps(p2s_lookup_message(user_input_rfc_number, host, port, user_input_rfc_title, "1"))
        #print(p2s_lookup_message(user_input_rfc_number, host, port, user_input_rfc_title))
        #print(data)
        s.send(data)
        server_data = pickle.loads(s.recv(1024))
        #print(server_data[0][3])
        #print(server_data[0][1])
        print(server_data[1], end="")
        keys = ['RFC Number', 'RFC Title', 'Hostname', 'Port Number']
        print_combined_list(server_data[0], keys)
        get_user_input("hello", 1)
    else:
        get_user_input("hello", 1)

start_new_thread(get_user_input, ("hello", 1))

while True:
    data_p2p, addr = upload_socket.recvfrom(1024)
    data_p2p = pickle.loads(data_p2p)
    #print(data_p2p[0])
    if data_p2p[0] == "G": #GET MSG
        indexP = data_p2p.index('P')
        indexC = data_p2p.index('C')
        rfc_num = data_p2p[indexC+1:indexP-1]
        message = p2p_response_message(rfc_num)
        filename = get_filename(rfc_num)
        #print("FILENAME: ", filename)
        upload_socket.sendto(pickle.dumps(message[0]),(addr))
        #print("SENDER ADDRESS:", addr[0])
        Simple_FTP_sender.rdt_send(filename, addr[0])
        #start_new_thread(get_user_input, ("hello", 1))
    elif data_p2p[0] == "P":    
        #global rcv_rfc_num
        filename = get_filename(rcv_rfc_num)
        Simple_FTP_receiver.rdt_recv(filename)
        rcv_rfc_num = ''
        rcv_rfc_title = ''
        start_new_thread(get_user_input, ("hello", 1))
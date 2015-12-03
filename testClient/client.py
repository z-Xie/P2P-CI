import socket
import time
import platform
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
    OS = platform.system()
    if OS == "Windows":  # determine rfc path for two different system
        rfc_path = "\\rfc\\"
    else:
        rfc_path = "/rfc/"
    files = os.listdir(os.getcwd() + rfc_path)
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
def p2p_response_message(filename): # the parameter "rfc_num" should be str
    current_time = time.strftime("%a, %d %b %Y %X %Z", time.localtime())
    OS = platform.system()
    if os.path.exists(os.getcwd()+filename) == False:
        status = "404"
        phrase = "Not Found"
        message = "P2P-CI/1.0 "+ status + " "+ phrase + "\n"\
                    "Date:" + current_time + "\n"\
                    "OS: "+str(OS)+"\n"
    else:
        status = "200"
        phrase = "OK"
        last_modified = time.ctime(os.path.getmtime(os.getcwd()+filename))
        content_length = os.path.getsize(os.getcwd()+filename)
        message = ["P2P-CI/1.0 "+ status + " "+ phrase + "\n"\
                  "Date: " + current_time + "\n"\
                  "OS: " + str(OS)+"\n"\
                  "Last-Modified: " + last_modified + "\n"\
                  "Content-Length: " + str(content_length) + "\n"\
                  "Content-Type: text/text \n"]
                  #+ str(data)

    return message, filename

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
    global upload_port_num
    user_input = input("> Enter ADD, LIST, LOOKUP, GET, or EXIT:  \n")
    if user_input == "EXIT":
        data = pickle.dumps("EXIT")
        s.send(data)
        s.close                     # Close the socket when done
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
        data = pickle.dumps(p2s_list_request(host, upload_port_num))
        s.send(data)
        server_data = s.recv(1024)
        #server_data = pickle.loads(server_data)
        print(server_data.decode('utf-8'), end="")
        #print(server_data, end="")

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
            get_user_input("hello", 1)
        else:  
            p2p_get_request(str(user_input_rfc_number), server_data[0]["Hostname"], server_data[0]["Port Number"])
        #get_user_input("hello", 1)
    elif user_input == "LOOKUP":
        user_input_rfc_number = input("> Enter the RFC Number: ")
        user_input_rfc_title = input("> Enter the RFC Title: ")
        data = pickle.dumps(p2s_lookup_message(user_input_rfc_number, host, upload_port_num, user_input_rfc_title, "1"))
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
        data = pickle.dumps("Bad Request")
        s.send(data)
        server_data = pickle.loads(s.recv(1024))
        print(server_data)
        get_user_input("hello", 1)

start_new_thread(get_user_input, ("hello", 1))

while True:
    data_p2p, addr = upload_socket.recvfrom(1024)
    data_p2p = pickle.loads(data_p2p)
    #print(data_p2p[0][0])
    if data_p2p[0] == "G": #GET MSG
        print(data_p2p)
        indexP = data_p2p.index('P')
        indexC = data_p2p.index('C')
        rfc_num = data_p2p[indexC+1:indexP-1]
        filename = get_filename(rfc_num)
        #print("FILENAME: ", filename)
        message = p2p_response_message(filename)
        #print(message)
        upload_socket.sendto(pickle.dumps(message),(addr))
        #print("SENDER ADDRESS:", addr[0])
        n = sys.argv[1]
        print("N = ", n)
        mss = sys.argv[2]
        print("MSS = ", mss)
        Simple_FTP_sender.rdt_send(os.getcwd() + filename, addr[0], n, mss)
        #start_new_thread(get_user_input, ("hello", 1))
    elif data_p2p[0][0][0] == "P":    
        #global rcv_rfc_num
        print(data_p2p[0][0])
        OS = platform.system()
        filename = data_p2p[1]
        #print("FILENAME: ", filename)
        prob_loss = sys.argv[3]
        print("LOST PROB = ", prob_loss)
        Simple_FTP_receiver.rdt_recv(os.getcwd() + filename, prob_loss)
        rcv_rfc_num = ''
        rcv_rfc_title = ''
        start_new_thread(get_user_input, ("hello", 1))
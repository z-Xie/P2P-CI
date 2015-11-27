import socket  
import sys
from collections import namedtuple
import pickle
import threading
import inspect
import time
import signal
import errno

DATA_TYPE = 0b101010101010101
data_pkt = namedtuple('data_pkt', 'seq_num checksum data_type data')

TIMEOUT = 2
base = 0  #sequence number of the oldest unacknowledged packet
nextseqnum = 0  #the smallest unsend sequence number
sndpkt = []
host = ''
port = 7735+1

sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sender_port = 62223+1
sender.bind(('', sender_port))

def carry_checksum_addition(num_1, num_2):
    c = num_1 + num_2
    return (c & 0xffff) + (c >> 16)

def calculate_checksum(message):
    checksum = 0
    for i in range(0, (len(message) - len(message) % 2), 2):
        my_message = str(message)
        w = ord(my_message[i]) + (ord(my_message[i+1]) << 8)
        checksum = carry_checksum_addition(checksum, w)
    return (not checksum) & 0xfff

def pack_data(message, seq_num):
    pkt = data_pkt(seq_num, calculate_checksum(message), DATA_TYPE, message)
    my_list = [pkt.seq_num, pkt.checksum, pkt.data_type, pkt.data]
    packed_pkt = pickle.dumps(my_list)
    return packed_pkt

def prepare_pkts(file_content):
    pkts_to_send = []
    seq_num = 0
    for item in file_content:   # Every MSS bytes should be packaged into segment Foo
        pkts_to_send.append(pack_data(item, seq_num))
        seq_num += 1
    return pkts_to_send

def timer(s,f):
    signal.setitimer(signal.ITIMER_REAL, TIMEOUT)
    global base
    global nextseqnum
    global host
    global port
    global sender
    global sndpkt
    print ("Timeout sequence number =", base)
    for i in range(base, nextseqnum):
        sender.sendto(sndpkt[i],(host, port))

def rdt_send(filename, rcv_host, N=3, MSS=100):
    #print(N, MSS, host, port, filename)
    global sender
    global host
    host = rcv_host
    global port
    signal.signal(signal.SIGALRM, timer)
    try:
        file_content = []
        #file_content.append(header)
        with open(filename, 'rb') as f:
            while True:
                chunk = f.read(int(MSS))  # Read the file MSS bytes each time Foo
                if chunk:
                    file_content.append(chunk)
                else:
                    break
    except FileNotFoundError:
        sys.exit("Failed to open file!")
    
    global sndpkt
    sndpkt = prepare_pkts(file_content)
    total_pkts = len(file_content)
    global base
    global nextseqnum
    #print("File Transfer Begins ...")
    while base < total_pkts:
        while nextseqnum < min(base + N, total_pkts):
            sender.sendto(sndpkt[nextseqnum],(rcv_host, port))
            if base == nextseqnum:
                signal.setitimer(signal.ITIMER_REAL, TIMEOUT)
            nextseqnum += 1

        try:
            data, addr = sender.recvfrom(256)
            data = pickle.loads(data)
            if data[2]=="1010101010101010":  # To ensure it is an ACK
                base = data[0] + 1
                if base == nextseqnum:
                    signal.alarm(0)
                else:
                    signal.setitimer(signal.ITIMER_REAL, TIMEOUT)
        except socket.error as e:
            if e.errno != errno.EINTR:
                raise
            else:
                continue
    base = 0  #sequence number of the oldest unacknowledged packet
    nextseqnum = 0  #the smallest unsend sequence number
    sndpkt = []
    #print("Done!")

if __name__ == "__main__":
    filename = "test_file.txt" #raw_input("Please enter filename: ")
    rdt_send(filename, socket.gethostname())
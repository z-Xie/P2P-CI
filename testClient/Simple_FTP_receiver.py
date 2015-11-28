import socket               
import pickle
import sys
from collections import namedtuple
import random
import time
import datetime

port = 7735
receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiver.bind(('', port))

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

def rdt_recv(filename, prob_loss=0.2):
    expectedseqnum = 0
    while True:
        receiver.settimeout(5)
        try:
            data, addr = receiver.recvfrom(1000000)
            receiver.settimeout(0.0)
        except socket.timeout:
            print("Session Finish!")
            break
        data = pickle.loads(data)
        #print("data: ", data)
        seq_num, checksum, data_type, message = data[0], data[1], data[2], data[3]
        rand_loss = random.random()
        if rand_loss <= float(prob_loss):
            if seq_num == expectedseqnum:
                print("Packet loss, sequence number = ", seq_num)
        else:
            if checksum != calculate_checksum(message):
                print("DATA: ", data)
                print("Packet dropped, checksum doesn't match!")
            if seq_num == expectedseqnum:
                with open(filename, 'ab') as file:
                    file.write(message)
                ack_message = [seq_num, "0000000000000000", "1010101010101010"]
                #print("Address: ", addr)
                receiver.sendto(pickle.dumps(ack_message), (addr))
                #receiver.sendto(ack_message, (addr))
                expectedseqnum += 1

if __name__ == "__main__":
     #input("Please enter server port: ")
    filename = "test_o.txt"  #raw_input("Please enter output filename: ")
    rdt_recv(filename)
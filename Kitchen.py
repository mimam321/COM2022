from gettext import find
import socket
import json
import zlib

localIP = "127.0.0.1"
localPort = 57900
bufferSize = 1024
orderList = []  # holds all orders

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))
print("Kitchen Awaiting Orders")


# function to calculate checksum
def findChecksum(x):
    return zlib.adler32(x.encode())


def READY(t_id):
    return json.dumps({
        "cmd": "READY",
        "data": {
            "table_id": t_id
        },
        "status": 202
    })


# Listen for incoming datagrams
while (True):

    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    address = bytesAddressPair[1]

    message = json.loads(bytesAddressPair[0])

    # sequence to follow if client sends CREATE command
    if (message["cmd"] == "CREATE"):
        data_json = json.dumps(message["data"])  # to calculate checksum at server
        recieverCheckSum = findChecksum(data_json)

        if recieverCheckSum == message["checksum"]:  # if checksum equal, data recieved correctly
            message['status'] = "201"
            orderList.append(message["data"])  # adds new order in orderList
            bytesToSend = str.encode(
                json.dumps({
                    "status": "201"
                })
            )
            print(orderList)
            UDPServerSocket.sendto(bytesToSend, address)

    # sequence to follow if client sends CANCEL command
    elif (message["cmd"] == "CANCEL"):
        data_json = json.dumps(message["data"])  # to calculate checksum at server
        recieverCheckSum = findChecksum(data_json)

        if recieverCheckSum == message["checksum"]:  # same checksum, correct data recieved; carry on with task
            # loop to delete canceled order from orderList
            for x in range(len(orderList)):
                if (orderList[x]["table_id"] == message["data"]["table_id"]):
                    del orderList[x]
                break

            bytesToSend = str.encode(
                json.dumps({
                    "status": "200",
                    "table_id": message["data"]["table_id"]
                })
            )
            UDPServerSocket.sendto(bytesToSend, address)

            print()
            print("Updated List: ")
            print(orderList)
            print()

    # sequence to follow if client sends WAIT command
    elif (message["cmd"] == "WAIT"):
        table = input("Enter table whose order is ready: ")
        newMssg = READY(table)
        bytesToSend = str.encode(newMssg)
        UDPServerSocket.sendto(bytesToSend, address)

    # sequence to follow if client sends COMPLETE command
    elif (message["cmd"] == "COMPLETE"):

        data_json = json.dumps(message["data"])  # to calculate checksum at server
        recieverCheckSum = findChecksum(data_json)

        if recieverCheckSum == message["checksum"]:  # checksum same, carry on with task
            # loop to delete completed order from orderList
            for x in range(len(orderList)):
                if (orderList[x]["table_id"] == message["data"]["table_id"]):
                    del orderList[x]
                break

            print("***  Order for table " + message["data"]["table_id"] + " is served  ***")
            print("Updated Order List: ")
            print(orderList)
            print("Status: 200")

            # send status code to client
            bytesToSend = str.encode(
                json.dumps({
                    "status": "200"
                })
            )

            UDPServerSocket.sendto(bytesToSend, address)

    else:
        print("Invalid Command")

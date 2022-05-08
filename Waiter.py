import socket
import json
import zlib

waiter = input("Enter waiter ID: ")
waiter_tables = []


# checkum function
# using built-in python lib
def findChecksum(x):
    return zlib.adler32(x.encode())


def CREATE(w_id, t_id):
    order = []
    orderItem = input("What would you like to order? (enter 1 item only): ")
    order.append(orderItem)

    moreOrder = True
    while (moreOrder):
        orderItem = input("Anything else? (enter No to stop ordering):  ")

        if (orderItem == 'No' or orderItem == 'no'):
            moreOrder = False
        else:
            order.append(orderItem)

    data = {
        "waiter_id": w_id,
        "table_id": t_id,
        "order": order
    }

    checkSum = findChecksum(json.dumps(data))

    return json.dumps({
        "cmd": "CREATE",
        "checksum": checkSum,
        "data": {
            "waiter_id": w_id,
            "table_id": t_id,
            "order": order
        },
        "status": ""
    })


def CANCEL(t_id):
    data = {
        "table_id": t_id
    }

    checkSum = findChecksum(json.dumps(data))

    return json.dumps({
        "cmd": "CANCEL",
        "checksum": checkSum,
        "data": {
            "table_id": t_id
        },
        "status": "",
        "error": ""
    })


def WAIT():
    return json.dumps({
        "cmd": "WAIT",
        "status": ""
    })


def COMPLETE(t_id):
    data = {
        "table_id": t_id
    }

    checkSum = findChecksum(json.dumps(data))

    return json.dumps({
        "cmd": "COMPLETE",
        "checksum": checkSum,
        "data": {
            "table_id": t_id
        },
        "status": ""
    })


serverAddressPort = ("127.0.0.1", 20001)

bufferSize = 1024

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Send to server using created UDP socket
while (True):

    # Menu for Waiter/Client
    print("***  Customer Actions  ***")
    print("1. Create new order")
    print("2. Cancel order")
    print("3. Wait for order preparation")
    print("4. Complete Order")
    print()
    choice = input("Enter choice (1-4): ")

    if choice == '1':  # to create new order and send to kitchen (server)
        table = input("Enter table ID: ")
        waiter_tables.append(table)

        mssg_json = CREATE(waiter, table)  # new order
        bytesToSend = str.encode(mssg_json)
        UDPClientSocket.sendto(bytesToSend, serverAddressPort)  # sending order to kitchen

        mssg_recv = UDPClientSocket.recvfrom(bufferSize)  # recv ack from kitchen
        mssg_recv_json = json.loads(mssg_recv[0])

        print()
        print("Status: " + mssg_recv_json["status"])
        if mssg_recv_json["status"] == "201":
            print("***  Order recieved by Kitchen  ***")
        print()

    elif choice == '2':
        table = input("Enter table ID to cancel order: ")
        mssg_json = CANCEL(table)  # to cancel order
        bytesToSend = str.encode(mssg_json)
        UDPClientSocket.sendto(bytesToSend, serverAddressPort)  # send cmd to kitchen(server)

        mssg_recv = UDPClientSocket.recvfrom(bufferSize)  # ack from kitchen
        mssg_recv_json = json.loads(mssg_recv[0])

        print()
        print("Status: " + mssg_recv_json["status"])
        if mssg_recv_json["status"] == "200":
            print("***  Order of table " + mssg_recv_json["table_id"] + " canceled successfully  ***")
        print()

    elif choice == '3':  # wait command to listen from server about READY orders
        mssg_json = WAIT()
        bytesToSend = str.encode(mssg_json)
        UDPClientSocket.sendto(bytesToSend, serverAddressPort)
        print("Waiting...")

        mssg_recv = UDPClientSocket.recvfrom(bufferSize)  # recv READY cmd for ready orders
        mssg_recv_json = json.loads(mssg_recv[0])

        if mssg_recv_json["cmd"] == "READY":
            if mssg_recv_json["data"]["table_id"] in waiter_tables:
                print()
                print("*** Order for table " + mssg_recv_json["data"]["table_id"] + " is ready ***")
                print("Please complete the order")
                print()

    elif choice == '4':
        table = input("Enter table ID to complete order: ")
        mssg_json = COMPLETE(table)  # serve ready order to customers
        bytesToSend = str.encode(mssg_json)
        UDPClientSocket.sendto(bytesToSend, serverAddressPort)  # tell kitchen that order is served

        mssg_recv = UDPClientSocket.recvfrom(bufferSize)  # recv ack
        mssg_recv_json = json.loads(mssg_recv[0])

        print()
        if mssg_recv_json["status"] == '200':
            print("Order completed successfully")
            print("Status: " + mssg_recv_json["status"])
            print()


    else:
        print("Invalid choice, enter again: ")
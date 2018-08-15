# Victor Zhang, created August 15, 2018
# Server side: Socket to get water flow rate
# version 1.0.0
# Python

import socket


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

local_hostname = socket.gethostname()

localfqdn = socket.getfqdn()

ip_address = socket.gethostbyname("")

print("This is the ip_address of server: ", ip_address)

print("This is a test with %s (%s), at %s", (local_hostname, localfqdn, ip_address))

server_address = ("133.11.164.152", 9876)

print("Attempting to bind to the %s", server_address)
sock.bind(server_address)

sock.listen(2)
file1 = open("testSocketData.dat", "w")

while True:
    print("Currently waiting for a connection")
    connection, client_address = sock.accept()

    try:
        print("Connection from %s", client_address)
        print("Connection is of type: ", type(connection))
        print("client_address is of type: ", type(client_address))
        # receive the data in small chunks and print it
        while True:
            data =  connection.recv(1024)
            dat = data.decode("utf-8")
            if dat != "done":
                with open("cryo-Environment-Data.dat", "r") as environ:
                    environmentParams = environ.readlines()

                environmentParams[29] = environmentParams[29][:environmentParams[29].index("=")+1] + " " + dat

                with open("cryo-Environment-Data.dat", "w") as environ:
                    environ.writelines(environmentParams)

                print(dat)
                file1.write(dat)
                #break
            else:
                # no more data -- quit the loop
                print ("here")
                print ("no more data.")
                print ("----------------\n")
                break
        break
    finally:
        # Clean up the connection
        connection.close()
        file1.close()
sock.close()

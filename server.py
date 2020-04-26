#!/usr/bin/env python3

from threading import Thread
import random
import time
import sys
from enum import Enum
sys.path.insert(0, "..")

from opcua import ua, Server

class DataType(Enum):
    EnumMetaType_INT32  = 1
    EnumMetaType_FLOAT  = 2
    EnumMetaType_DOUBLE = 3
    EnumMetaType_STRING = 4
    EnumMetaType_ENUM   = 5
    EnumMetaType_ARRAY  = 6
    EnumMetaType_BOOL   = 7
    EnumMetaType_STRUCT = 8
    EnumMetaType_DATE   = 9


class Change(Thread):
    def __init__(self, int_list, fload_list):
        Thread.__init__(self)
        self._stop = False
        self.int_list = int_list
        self.float_list = fload_list

    def stop(self):
        self._stop = True

    def run(self):
        while not self._stop:
            for id in self.int_list:
                id.set_value(int(random.randint(0, 1000)))
            for id in self.float_list:
                id.set_value(random.uniform(0, 100.0))

            time.sleep(1)

if __name__ == "__main__":

    # now setup our server
    server = Server()
    sv = "opc.tcp://0.0.0.0:4840/freeopcua/server/"
    server.set_endpoint(sv)
    server.set_server_name("FreeOpcUa Example Server")

    # set all possible endpoint policies for clients to connect through
    server.set_security_policy([
                ua.SecurityPolicyType.NoSecurity,
                ua.SecurityPolicyType.Basic128Rsa15_SignAndEncrypt,
                ua.SecurityPolicyType.Basic128Rsa15_Sign,
                ua.SecurityPolicyType.Basic256_SignAndEncrypt,
                ua.SecurityPolicyType.Basic256_Sign])

    # setup our own namespace
    uri = "OPCUA"
    idx = server.register_namespace(uri)
    
    # create directly some objects and variables
    simulation = server.nodes.objects.add_object(idx, "simulation")
    fload_list = []
    int_list = []
    with open('./points.md', 'r', encoding='utf-8') as f:
        for line in f.readlines()[2:]:
            data = line.split('|')
            name = data[1].strip().split('#')
            id = name[1]
            typ = int(data[3].strip())
            if typ == DataType.EnumMetaType_INT32.value:
                s = 'ns= %d;s= %s' % (idx, id)
                t = simulation.add_variable(s, id, 1)
                int_list.append(t)
            elif typ == DataType.EnumMetaType_FLOAT.value:
                s = 'ns= %d;s= %s' % (idx, id)
                t = simulation.add_variable(s, id, 1.0)
                fload_list.append(t)
            else:
                print('need to append this type : [%s] in code' % typ)
                exit(0)
    
    # start opcua server
    server.start()
    print("Start opcua server, server: %s" % sv)

    temperature_thread = Change(int_list, fload_list)  # just  a stupide class update a variable
    temperature_thread.start()

    try:
        while True:
            time.sleep(1)
    finally:
        print("Exit opcua server, port:4840...")
        temperature_thread.stop()
        server.stop()

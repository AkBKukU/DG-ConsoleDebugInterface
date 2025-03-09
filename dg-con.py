#!/usr/bin/env python3
import serial
import json
import re
import struct

class SerialWrapper(object):

        def __init__(self,serial_port="/dev/ttyUSB0"):
                print("This would be a serial device interface")
                self.ser=serial.Serial(serial_port,9600,timeout=0.1)

        def write(self,data):
                print(f"Write: {data}")
                # Send data to DECTalk
                self.ser.write( bytes(str(data),'ascii',errors='ignore') )
                return

        def read(self):
                result = ""
                return str(self.ser.read(100).decode('ascii'))



class DGnovaMicro(SerialWrapper):

        # The microNOVA Debug Console remembers whater the last value entered
        # or displayed is and will perform the next action using that value.
        #

        def __init__(self,serial_port="/dev/ttyUSB0"):
                super().__init__(serial_port)
                self.machine_name="microNOVA"
                self.sample_read={"command":"000001/\n","response":"000001 123456 "}
                self.cmd_next="\n"
                self.cmd_read="/"
                self.cmd_cancel="k"
                self.response_read_address_regex=self.cmd_read+"[0-1][0-7]{5} [0-1][0-7]{5}"

                # Init serial interface
                self.write(self.cmd_cancel)
                self.read()

        def address_read(self,address):
                address=str(oct(address)).replace("0o","")
                self.write(address)
                self.write(self.cmd_read)
                result = self.read()
                if not re.search(address+self.response_read_address_regex,result):
                        raise Exception(f"Result: {result} did not match {address+self.response_read_address_regex}")

                result=result.replace(address+self.cmd_read+address.zfill(6)+" ","")
                print({address:result})
                return int(result,8)

        def address_read_range(self,start,end=0,count=0):
                responses=[]
                if end==0:
                        end=start+count

                # Set starting address

                for address in range(start,end):
                        result=self.address_read(address)
                        responses.append(result)

                return responses

dg = DGnovaMicro(serial_port="/dev/ttyUSB1")
out_file = open("ROM-bottom.json", "w")


data = dg.address_read_range(0o77400,end=0o77557)

with open("ROM-bottom.bin", "wb") as w:
        for value in data:
                w.write(struct.pack('<H', value))


json.dump(data, out_file, indent = 6)

out_file = open("ROM-top.json", "w")
data = dg.address_read_range(0o77600,end=0o77777)

with open("ROM-top.bin", "wb") as w:
        for value in data:
                w.write(struct.pack('<H', value))
json.dump(data, out_file, indent = 6)

#!/usr/bin/env python3
import serial
import json
import re
import struct
import os

class SerialWrapper(object):

        def __init__(self,serial_port="/dev/ttyUSB0"):
                # Use standard 9600,8N1 config
                # NOTE: timeout is needed for reads that are set to be too long
                self.ser=serial.Serial(serial_port,9600,timeout=0.1)

        def write(self,data):
                print(f"Write: {data}")
                self.ser.write( bytes(str(data),'ascii',errors='ignore') )
                return

        def read(self):
                result = ""
                result = str(self.ser.read(100).decode('ascii'))
                print(f"Read: {result}")
                return result



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
                # Input address in Octal format and convert to string
                address=str(oct(address)).replace("0o","")
                # Open address in console
                self.write(address+self.cmd_read)
                # Read back data
                result = self.read()
                # Check that data matches expected format
                if not re.search(address+self.response_read_address_regex,result):
                        raise Exception(f"Result: {result} did not match {address+self.response_read_address_regex}")

                # Filter out only address value
                result=result.replace(address+self.cmd_read+address.zfill(6)+" ","")
                print({address:result})
                return int(result,8)

        def address_write(self,address, data):
                # Open address location
                self.address_read(address)
                # Format value from octal to string
                data=str(oct(data)).replace("0o","")
                # Set address value
                self.write(data+self.cmd_next)
                # Clear read buffer of echo
                result = self.read()
                return


        def address_write_file(self,address,filename):
                # Open address location
                self.address_read(address)
                # Get size of file in 16b words
                count = os.path.getsize(filename)/2

                # Open file and loop over words
                with open(filename, "rb") as f:
                        while count:
                                # Get data from file as octal value
                                data=str(oct(struct.unpack('<H', f.read(2))[0])).replace("0o","")
                                # Write data to address and move to next address
                                self.write(data+self.cmd_next)
                                # Clear read buffer of echo
                                result = self.read()
                                # Count down words to send
                                count-=1

                return

        def address_read_range(self,start,end=0,count=0):
                responses=[]
                # Prep end value
                if end==0:
                        # Count
                        end=start+count
                else:
                        # End address asumed to be range and will match end
                        # prematurely
                        end+=1

                # Read each address
                # TODO: Open starting address and cmd_next through others
                # to improve speed of reads
                for address in range(start,end):
                        result=self.address_read(address)
                        responses.append(result)

                return responses

        def address_read_range_file(self,start,filename,end=0,count=0):
                # Read address range
                if end==0:
                        data = self.address_read_range(start,count=count)
                else:
                        data = self.address_read_range(start,end=end)

                # Write out binary file with data
                with open(filename, "wb") as w:
                        for value in data:
                                w.write(struct.pack('<H', value))


dg = DGnovaMicro(serial_port="/dev/ttyUSB1")

dg.address_write_file(0o200,"ROM-bottom.bin")



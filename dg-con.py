#!/usr/bin/env python3
import serial
import json
import sys
import re
import struct
import os
import argparse
import asyncio

global verbose
verbose=False
def vprint(*args, **kwargs):
        # Verbose only printing to stderr
        if verbose:
                print(*args, file=sys.stderr, **kwargs)

class SerialWrapper(object):

        def __init__(self,serial):
                # Use standard 9600,8N1 config
                # NOTE: timeout is needed for reads that are set to be too long
                self.ser=serial

        def write(self,data):
                vprint(f"Write: {data}")
                self.ser.write( bytes(str(data),'ascii',errors='ignore') )
                return

        def read(self):
                result = ""
                result = str(self.ser.read(100).decode('ascii'))
                vprint(f"Read: {result}")
                return result



class DGnovaMicro(SerialWrapper):

        # The microNOVA Debug Console remembers whater the last value entered
        # or displayed is and will perform the next action using that value.
        #

        def __init__(self,serial):
                super().__init__(serial)
                self.machine_name="microNOVA"
                self.sample_read={"command":"000001/\n","response":"000001 123456 "}
                self.cmd_next="\n"
                self.cmd_read="/"
                self.cmd_cancel="k"
                self.response_read_address_regex=self.cmd_read+"[0-1][0-7]{5} [0-1][0-7]{5}"

        def console_cancel(self):
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
                vprint({address:result})
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


def main():
        parser = argparse.ArgumentParser(
                prog='dg-con',
                description='Data General console interface tool',
                epilog='By Shelby Jueden')
        parser.add_argument('-s', '--start', help="Starting address(in Octal) for RAM dump", default=None)
        parser.add_argument('-e', '--end', help="End address(in Octal) for RAM dump", default=None)
        parser.add_argument('-l', '--length', help="Count of addresses for RAM dump", default=1)
        parser.add_argument('-c', '--command', help="Command or data to send before receiving data back", default=None)
        parser.add_argument('-x', '--execute', help="Character to send to execute command. Sent after data in --command", default="\n")
        parser.add_argument('-w', '--receive', help="File to receive data into from Data General", default=None)
        parser.add_argument('-v', '--verbose', help="Output additional information to stderr about activity",action='store_true')

        parser.add_argument('-p', '--port', help="Serial: Port to communicate over", default="/dev/ttyUSB0")
        parser.add_argument('-b', '--buad', help="Serial: Baud rate", default=9600)
        parser.add_argument('-d', '--databits', help="Serial: Data bits count", choices=[7,8], default=8)
        parser.add_argument('-a', '--parity', help="Serial: Parity", choices=["O","E","N"], default="N")
        parser.add_argument('-o', '--stopbits', help="Serial: Stop bit count", choices=[1,2], default=1)


        parser.add_argument('input', nargs='?', help="File to send to Data General", default=None)
        args = parser.parse_args()

        ser = serial.Serial(
                args.port,
                args.buad,
                timeout=0.1,
                bytesize=args.databits,
                parity=args.parity,
                stopbits=args.stopbits
                )

        dg = DGnovaMicro(ser)

        global verbose
        verbose=args.verbose

        # If a start address is provided then you are working with the Console Debug
        if args.start is not None:
                start = int(args.start.replace("0o",""),8)
                # Prep end value
                if args.end is not None:
                        # End address asumed to be range and will match end
                        # prematurely
                        end=int(args.end.replace("0o",""),8)
                else:
                        # Count
                        end=start+int(args.length)-1

                if args.receive is not None:
                        dg.address_read_range_file(start,args.receive,end)
                else:
                        print(dg.address_read_range(start,end))

        # If a start address is provided then you are working with the Console Debug
        if args.command is not None:
                cmd = str(args.command)+args.execute
                if args.receive is not None:
                        ser.write( bytes(cmd,'ascii',errors='ignore') )
                        with open(args.receive, "wb") as w:
                                cmd_trim=False
                                read=True
                                while(read):
                                        data = ser.read(1000)
                                        if data == b'':
                                                read=False
                                                print()
                                                print("Transfer complete")
                                        else:
                                                if not cmd_trim:
                                                        data=data[len(cmd)+1:]
                                                w.write(data)
                                                print(f"Recieved data: {os.path.getsize(args.receive)} bytes",end="\r")


                else:
                        ser.write( bytes(cmd,'ascii',errors='ignore') )

                        response=""
                        read=True
                        while(read):
                                data = ser.read(100000).decode('ascii')
                                if data != "":
                                        response+=data
                                else:
                                        read=False


                        if args.receive is None:
                                print(str(response))

if __name__ == "__main__":
    main()

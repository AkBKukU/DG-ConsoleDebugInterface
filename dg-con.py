 #!/usr/bin/env python3

 class SerialWrapper(object)

         def __init__(self):
                 print("This would be a serial device interface")

         def write(self,data):
                 print(f"Write: {{data}}")

         def read(self):
                 print(f"Write: {{data}}")


 class DGnovaMicro(SerialWrapper):

         # The microNOVA Debug Console remembers whater the last value entered
         # or displayed is and will perform the next action using that value.
         #

         def __init__(self):
                 self.machine_name="microNOVA"
                 self.sample_read={"command":"000001/\n","response":"000001 123456 "}
                 self.cmd_next="\n"
                 self.cmd_read="/"
                 self.cmd_cancel="k"

        def address_read(self,address):
                self.write(address)
                self.write(self.cmd_read)
                return self.read().replace(address+" ","").strip()

        def address_read_range(self,start,end=0,count=0):
                responses=[]
                if end==0:
                        end=start+count

                # Set starting address
                self.write(start)
                self.write(self.cmd_read)

                for address in range(start,end):
                        responses.append(self.read().replace(address+" ","").strip())
                        if address == end:
                                break

                        self.write(self.cmd_next)

                return responses

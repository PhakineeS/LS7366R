#!/usr/bin/python

import spidev
from time import sleep

class LS7366R():
    #commands
    CLEAR_COUNTER = 0x20            # 0X 0010 0000 
    CLEAR_STATUS = 0x30             # 0X 0011 0000
    READ_COUNTER = 0x60             # 0X 0110 0000
    READ_STATUS = 0x70              # 0X 0111 0000
    WRITE_MODE0 = 0x88              # 0X 1000 1000
    WRITE_MODE1 = 0x90              # 0X 1001 0000
    #mode
    FOURX_COUNT = 0x03              # 0X 0000 0011
    FOURBYTE_COUNTER = 0x00         # 0X 0000 0000
    THREEBYTE_COUNTER = 0x01        # 0X 0000 0001
    TWOBYTE_COUNTER = 0x02          # 0X 0000 0010
    ONEBYTE_COUNTER = 0x03          # 0X 0000 0011
    BYTE_MODE = [ ONEBYTE_COUNTER , TWOBYTE_COUNTER , THREEBYTE_COUNTER , FOURBYTE_COUNTER ]
    MAX_VAL = 4294967295            # max value in integer
    COUNTER_SIZE = 4                # default value

    def __init__(self,CSX,SCK,BTMD):
        self.COUNTER_SIZE = BTMD        # declare counter size ( default is 4 )
        self.spi = spidev.SpiDev()      # initialize object
        self.spi = spi.open(0,CSX)      # connect the object to SPI device
        self.spi.max_speed_hz = SCK     # set speed
        print("Clearing Encoder {} Count : {}".format(CSX,self.clear_counter()))    # clear counter
        print("Clearing Encode {} STATUS : {}".format(CSX,self.clear_status()))     # clear status
        self.spi.xfer2([self.WRITE_MODE0,self.FOURX_COUNT])                         # send write command and mode0 value
        sleep(0.1)                                                                  # slow down
        self.spi.xfer2([self.WRITE_MODE1,self.BYTE_MODE[self.COUNTER_SIZE-1]])      # send write command and mode1 value ( according to byte)

    def close(self):
        print("closing...")
        self.spi.close()        # disconnect the object from SPI device

    def clear_counter(self):
        self.spi.xfer2([self.CLEAR_COUNTER])    # send clear command
        return ["DONE"]

    def clear_status(self):
        self.spi.xfer2([self.CLEAR_STATUS])     # send clear command
        return ["DONE"]

    def read_counter(self):
        readTransaction = [self.READ_COUNTER]                        # add read command in list
        for i in range(self.COUNTER_SIZE):                      
            readTransaction.append(0)                           # add random data according to counter size (byte)
        data = self.spi.xfer2(readTransaction)                  # send command and random data
        #read data
        EncoderCount = 0
        for i in range(self.COUNTER_SIZE):
            EncoderCount = (EncoderCount << 8) + data[i+1]       # shift last encoder value to the left ( 8 bits ) and add new value on the right side ( position of new value plus one because first position is read command not value )
        # check overflow
        if data[1] != 255:                                       # true if not overflow
            return EncoderCount                                  # not overflow
        return EncoderCount + (self.MAX_VAL+1)                   # overflow 
    
    def read_status(self):
        data = self.spi.xfer2([READ_STATUS, 0xFF])               # send read command and random data
        return data[1]                                           # return position one because position zero is random data

if __name__ == "__main__":                                       # true if the python interpreter is running the source file as the main program
    encoder = LS7366R(0, 1000000, 4)                             # build class
    try:
        while True:                                              
            print("Encoder count :",encoder.read_counter(),"Press CTRL-C to terminate test program.")  # keep printing count     
            sleep(.2)                                                                                  # slown down

    except KeyboardInterrupt:                                                                          # true if press ctrl+c 
        encoder.close()                                                                                # disconnect
        print("ending..")

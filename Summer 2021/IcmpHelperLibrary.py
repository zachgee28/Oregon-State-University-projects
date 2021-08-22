# Author: Zach Gee
# Description: Implement a Pinger and Trace Route program

# #################################################################################################################### #
# Imports                                                                                                              #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
# #################################################################################################################### #
import os
from socket import *
import struct
import time
import select


# #################################################################################################################### #
# Class IcmpHelperLibrary                                                                                              #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
# #################################################################################################################### #
class IcmpHelperLibrary:
    # ################################################################################################################ #
    # Class IcmpPacket                                                                                                 #
    #                                                                                                                  #
    # References:                                                                                                      #
    # https://www.iana.org/assignments/icmp-parameters/icmp-parameters.xhtml                                           #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    class IcmpPacket:
        # ############################################################################################################ #
        # IcmpPacket Class Scope Variables                                                                             #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        __icmpTarget = ""               # Remote Host
        __destinationIpAddress = ""     # Remote Host IP Address
        __header = b''                  # Header after byte packing
        __data = b''                    # Data after encoding
        __dataRaw = ""                  # Raw string data before encoding
        __icmpType = 0                  # Valid values are 0-255 (unsigned int, 8 bits)
        __icmpCode = 0                  # Valid values are 0-255 (unsigned int, 8 bits)
        __packetChecksum = 0            # Valid values are 0-65535 (unsigned short, 16 bits)
        __packetIdentifier = 0          # Valid values are 0-65535 (unsigned short, 16 bits)
        __packetSequenceNumber = 0      # Valid values are 0-65535 (unsigned short, 16 bits)
        __ipTimeout = 30
        __ttl = 255                     # Time to live
        __rtt = f''                     # RTT set after echo reply received

        __DEBUG_IcmpPacket = False      # Allows for debug output

        # ############################################################################################################ #
        # IcmpPacket Class Getters                                                                                     #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        def getIcmpTarget(self):
            return self.__icmpTarget

        def getDataRaw(self):
            return self.__dataRaw

        def getIcmpType(self):
            return self.__icmpType

        def getIcmpCode(self):
            return self.__icmpCode

        def getPacketChecksum(self):
            return self.__packetChecksum

        def getPacketIdentifier(self):
            return self.__packetIdentifier

        def getPacketSequenceNumber(self):
            return self.__packetSequenceNumber

        def getTtl(self):
            return self.__ttl

        def getRtt(self):
            return self.__rtt

        # ############################################################################################################ #
        # IcmpPacket Class Setters                                                                                     #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        def setIcmpTarget(self, icmpTarget):
            self.__icmpTarget = icmpTarget

            # Only attempt to get destination address if it is not whitespace
            if len(self.__icmpTarget.strip()) > 0:
                self.__destinationIpAddress = gethostbyname(self.__icmpTarget.strip())

        def setIcmpType(self, icmpType):
            self.__icmpType = icmpType

        def setIcmpCode(self, icmpCode):
            self.__icmpCode = icmpCode

        def setPacketChecksum(self, packetChecksum):
            self.__packetChecksum = packetChecksum

        def setPacketIdentifier(self, packetIdentifier):
            self.__packetIdentifier = packetIdentifier

        def setPacketSequenceNumber(self, sequenceNumber):
            self.__packetSequenceNumber = sequenceNumber

        def setTtl(self, ttl):
            self.__ttl = ttl

        def setRtt(self, rtt):
            self.__rtt = rtt

        # ############################################################################################################ #
        # IcmpPacket Class Private Functions                                                                           #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        def __recalculateChecksum(self):
            print("calculateChecksum Started...") if self.__DEBUG_IcmpPacket else 0
            packetAsByteData = b''.join([self.__header, self.__data])
            checksum = 0

            # This checksum function will work with pairs of values with two separate 16 bit segments. Any remaining
            # 16 bit segment will be handled on the upper end of the 32 bit segment.
            countTo = (len(packetAsByteData) // 2) * 2

            # Calculate checksum for all paired segments
            print(f'{"Count":10} {"Value":10} {"Sum":10}') if self.__DEBUG_IcmpPacket else 0
            count = 0
            while count < countTo:
                thisVal = packetAsByteData[count + 1] * 256 + packetAsByteData[count]
                checksum = checksum + thisVal
                checksum = checksum & 0xffffffff        # Capture 16 bit checksum as 32 bit value
                print(f'{count:10} {hex(thisVal):10} {hex(checksum):10}') if self.__DEBUG_IcmpPacket else 0
                count = count + 2

            # Calculate checksum for remaining segment (if there are any)
            if countTo < len(packetAsByteData):
                thisVal = packetAsByteData[len(packetAsByteData) - 1]
                checksum = checksum + thisVal
                checksum = checksum & 0xffffffff        # Capture as 32 bit value
                print(count, "\t", hex(thisVal), "\t", hex(checksum)) if self.__DEBUG_IcmpPacket else 0

            # Add 1's Complement Rotation to original checksum
            checksum = (checksum >> 16) + (checksum & 0xffff)   # Rotate and add to base 16 bits
            checksum = (checksum >> 16) + checksum              # Rotate and add

            answer = ~checksum                  # Invert bits
            answer = answer & 0xffff            # Trim to 16 bit value
            answer = answer >> 8 | (answer << 8 & 0xff00)
            print("Checksum: ", hex(answer)) if self.__DEBUG_IcmpPacket else 0

            self.setPacketChecksum(answer)

        def __packHeader(self):
            # The following header is based on http://www.networksorcery.com/enp/protocol/icmp/msg8.htm
            # Type = 8 bits
            # Code = 8 bits
            # ICMP Header Checksum = 16 bits
            # Identifier = 16 bits
            # Sequence Number = 16 bits
            self.__header = struct.pack("!BBHHH",
                                   self.getIcmpType(),              #  8 bits / 1 byte  / Format code B
                                   self.getIcmpCode(),              #  8 bits / 1 byte  / Format code B
                                   self.getPacketChecksum(),        # 16 bits / 2 bytes / Format code H
                                   self.getPacketIdentifier(),      # 16 bits / 2 bytes / Format code H
                                   self.getPacketSequenceNumber()   # 16 bits / 2 bytes / Format code H
                                   )

        def __encodeData(self):
            data_time = struct.pack("d", time.time())               # Used to track overall round trip time
                                                                    # time.time() creates a 64 bit value of 8 bytes
            dataRawEncoded = self.getDataRaw().encode("utf-8")

            self.__data = data_time + dataRawEncoded

        def __packAndRecalculateChecksum(self):
            # Checksum is calculated with the following sequence to confirm data in up to date
            self.__packHeader()                 # packHeader() and encodeData() transfer data to their respective bit
                                                # locations, otherwise, the bit sequences are empty or incorrect.
            self.__encodeData()
            self.__recalculateChecksum()        # Result will set new checksum value
            self.__packHeader()                 # Header is rebuilt to include new checksum value

        def __validateIcmpReplyPacketWithOriginalPingData(self, icmpReplyPacket):
            # Hint: Work through comparing each value and identify if this is a valid response.
            if self.getPacketSequenceNumber() == icmpReplyPacket.getIcmpSequenceNumber():   # Confirm sent sequence number matches received sequence number
                icmpReplyPacket.setIcmpSequenceNumber_isValid(True)
            if self.getPacketIdentifier() == icmpReplyPacket.getIcmpIdentifier():   # Confirm sent identifier matches received identifier
                icmpReplyPacket.setIcmpIdentifier_isValid(True)
            if self.getDataRaw() == icmpReplyPacket.getIcmpData():  # Confirm sent data matches received data
                icmpReplyPacket.setIcmpData_isValid(True)

            if (icmpReplyPacket.getIcmpSequenceNumber_isValid() and
                    icmpReplyPacket.getIcmpIdentifier_isValid() and
                    icmpReplyPacket.getIcmpData_isValid()):
                icmpReplyPacket.setIsValidResponse(True)

        # ############################################################################################################ #
        # IcmpPacket Class Public Functions                                                                            #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        def buildPacket_echoRequest(self, packetIdentifier, packetSequenceNumber):
            self.setIcmpType(8)
            self.setIcmpCode(0)
            self.setPacketIdentifier(packetIdentifier)
            self.setPacketSequenceNumber(packetSequenceNumber)
            self.__dataRaw = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
            self.__packAndRecalculateChecksum()

        def sendEchoRequest(self):
            if len(self.__icmpTarget.strip()) <= 0 | len(self.__destinationIpAddress.strip()) <= 0:
                self.setIcmpTarget("127.0.0.1")

            print("Pinging (" + self.__icmpTarget + ") " + self.__destinationIpAddress)

            mySocket = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP)
            mySocket.settimeout(self.__ipTimeout)
            mySocket.bind(("", 0))
            print("current TTL:",self.getTtl())
            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', self.getTtl()))  # Unsigned int - 4 bytes
            try:
                mySocket.sendto(b''.join([self.__header, self.__data]), (self.__destinationIpAddress, 0))
                timeLeft = 30
                pingStartTime = time.time()
                startedSelect = time.time()
                whatReady = select.select([mySocket], [], [], timeLeft)
                endSelect = time.time()
                howLongInSelect = (endSelect - startedSelect)
                if whatReady[0] == []:  # Timeout
                    print("  *        *        *        *        *    Request timed out.")
                recvPacket, addr = mySocket.recvfrom(1024)  # recvPacket - bytes object representing data received
                # addr  - address of socket sending data
                timeReceived = time.time()
                timeLeft = timeLeft - howLongInSelect
                if timeLeft <= 0:
                    print("  *        *        *        *        *    Request timed out (By no remaining time left).")

                else:
                    # Fetch the ICMP type and code from the received packet
                    icmpType, icmpCode = recvPacket[20:22]

                    if icmpType == 12:                          # Parameter Problem
                        code_desc = ["Pointer indicates the error","Missing a Required Option","Bad Length"]
                        print("  TTL=%d    RTT=%.0f ms    Type=%d    Code=%d    %s \n"
                              "  Error description: %s" %
                              (
                                  self.getTtl(),
                                  (timeReceived - pingStartTime) * 1000,
                                  icmpType,
                                  icmpCode,
                                  addr[0],
                                  code_desc[icmpCode]
                              ))

                    elif icmpType == 11:                          # Time Exceeded
                        code_desc = ["Time to Live exceeded in Transit", "Fragment Reassembly Time Exceeded"]
                        print("  TTL=%d    RTT=%.0f ms    Type=%d    Code=%d    %s \n"
                              "  Error description: %s" %
                                (
                                    self.getTtl(),
                                    (timeReceived - pingStartTime) * 1000,
                                    icmpType,
                                    icmpCode,
                                    addr[0],
                                    code_desc[icmpCode]
                                )
                              )

                    elif icmpType == 9:                           # Router Advertisement
                        code_desc = {0:"Normal router advertisement", 16:"Does not route common traffic"}
                        print("  TTL=%d    RTT=%.0f ms    Type=%d    Code=%d    %s \n"
                              "  Error description: %s" %
                              (
                                  self.getTtl(),
                                  (timeReceived - pingStartTime) * 1000,
                                  icmpType,
                                  icmpCode,
                                  addr[0],
                                  code_desc[icmpCode]
                              ))

                    elif icmpType == 5:                         # Redirect
                        code_desc = ["Redirect Datagram for the Network (or subnet)",
                                     "Redirect Datagram for the Host",
                                     "Redirect Datagram for the Type of Service and Network",
                                     "Redirect Datagram for the Type of Service and Host"]
                        print("  TTL=%d    RTT=%.0f ms    Type=%d    Code=%d    %s \n"
                              "  Error description: %s" %
                              (
                                  self.getTtl(),
                                  (timeReceived - pingStartTime) * 1000,
                                  icmpType,
                                  icmpCode,
                                  addr[0],
                                  code_desc[icmpCode]
                              )
                              )

                    elif icmpType == 3:                         # Destination Unreachable
                        code_desc = ["Net Unreachable",
                                     "Host Unreachable",
                                     "Protocol Unreachable",
                                     "Port Unreachable",
                                     "Fragmentation Needed and Don't Fragment was Set",
                                     "Source Route Failed",
                                     "Destination Network Unknown",
                                     "Destination Host Unknown",
                                     "Source Host Isolated",
                                     "Communication with Destination Network is Administratively Prohibited",
                                     "Communication with Destination Host is Administratively Prohibited",
                                     "Destination Network Unreachable for Type of Service",
                                     "Destination Host Unreachable for Type of Service",
                                     "Communication Administratively Prohibited",
                                     "Host Precedence Violation",
                                     "Precedence cutoff in effect"]
                        print("  TTL=%d    RTT=%.0f ms    Type=%d    Code=%d    %s \n"
                              "  Error description: %s" %
                              (
                                  self.getTtl(),
                                  (timeReceived - pingStartTime) * 1000,
                                  icmpType,
                                  icmpCode,
                                  addr[0],
                                  code_desc[icmpCode]
                              )
                              )

                    elif icmpType == 0:                         # Echo Reply
                        icmpReplyPacket = IcmpHelperLibrary.IcmpPacket_EchoReply(recvPacket)
                        self.__validateIcmpReplyPacketWithOriginalPingData(icmpReplyPacket)
                        icmpReplyPacket.printResultToConsole(self.getTtl(), timeReceived, addr, self.getPacketSequenceNumber(), self.getPacketIdentifier(), self.getDataRaw())
                        self.setRtt(icmpReplyPacket.getRtt())   # grab RTT for later calculating min, max, avg RTT
                        return True     # Echo reply is the end and therefore should return

                    else:
                        print("error")
            except timeout:
                print("  *        *        *        *        *    Request timed out (By Exception).")
            finally:
                mySocket.close()

        def sendTraceRouteEchoRequest(self):
            if len(self.__icmpTarget.strip()) <= 0 | len(self.__destinationIpAddress.strip()) <= 0:
                self.setIcmpTarget("127.0.0.1")

            RTT_list = [None,None,None]
            is_done = False
            is_error = True
            err_type = None
            err_code = None
            error_desc = None
            address = None
            for i in range(3):

                mySocket = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP)
                mySocket.settimeout(self.__ipTimeout)
                mySocket.bind(("", 0))
                mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', self.getTtl()))  # Unsigned int - 4 bytes
                try:
                    mySocket.sendto(b''.join([self.__header, self.__data]), (self.__destinationIpAddress, 0))
                    timeLeft = 30
                    pingStartTime = time.time()
                    startedSelect = time.time()
                    whatReady = select.select([mySocket], [], [], timeLeft)
                    endSelect = time.time()
                    howLongInSelect = (endSelect - startedSelect)
                    if whatReady[0] == []:  # Timeout
                        RTT_list[i] = "*\t"
                    recvPacket, addr = mySocket.recvfrom(1024)  # recvPacket - bytes object representing data received
                    # addr  - address of socket sending data
                    timeReceived = time.time()
                    timeLeft = timeLeft - howLongInSelect
                    if timeLeft <= 0:
                        RTT_list[i] = "*\t"

                    else:
                        # Fetch the ICMP type and code from the received packet
                        icmpType, icmpCode = recvPacket[20:22]

                        if icmpType == 12:                          # Parameter Problem
                            RTT_list[i] = "*\t"
                            code_desc = ["Pointer indicates the error","Missing a Required Option","Bad Length"]
                            if is_error:
                                err_type = icmpType
                                err_code = icmpCode
                                error_desc = "Type: "+icmpType+" Code: "+icmpCode+"  "+code_desc[icmpCode]
                                try:
                                    address = gethostbyaddr(addr[0])[0] + " [" + addr[0] + "]"
                                except:
                                    address = addr[0]

                        elif icmpType == 11:                          # Time Exceeded
                            is_error = False
                            RTT_list[i] = str(round((timeReceived - pingStartTime) * 1000)) + " ms"
                            try:
                                address = gethostbyaddr(addr[0])[0] + " [" + addr[0] + "]"
                            except:
                                address = addr[0]

                        elif icmpType == 9:                           # Router Advertisement
                            RTT_list[i] = "*\t"
                            code_desc = {0:"Normal router advertisement", 16:"Does not route common traffic"}
                            if is_error:
                                err_type = icmpType
                                err_code = icmpCode
                                error_desc = "Type: "+icmpType+" Code: "+icmpCode+"  "+code_desc[icmpCode]
                                try:
                                    address = gethostbyaddr(addr[0])[0] + " [" + addr[0] + "]"
                                except:
                                    address = addr[0]

                        elif icmpType == 5:                         # Redirect
                            RTT_list[i] = "*\t"
                            code_desc = ["Redirect Datagram for the Network (or subnet)",
                                         "Redirect Datagram for the Host",
                                         "Redirect Datagram for the Type of Service and Network",
                                         "Redirect Datagram for the Type of Service and Host"]
                            if is_error:
                                err_type = icmpType
                                err_code = icmpCode
                                error_desc = "Type: "+icmpType+" Code: "+icmpCode+"  "+code_desc[icmpCode]
                                try:
                                    address = gethostbyaddr(addr[0])[0] + " [" + addr[0] + "]"
                                except:
                                    address = addr[0]

                        elif icmpType == 3:                         # Destination Unreachable
                            RTT_list[i] = "*\t"
                            code_desc = ["Net Unreachable",
                                         "Host Unreachable",
                                         "Protocol Unreachable",
                                         "Port Unreachable",
                                         "Fragmentation Needed and Don't Fragment was Set",
                                         "Source Route Failed",
                                         "Destination Network Unknown",
                                         "Destination Host Unknown",
                                         "Source Host Isolated",
                                         "Communication with Destination Network is Administratively Prohibited",
                                         "Communication with Destination Host is Administratively Prohibited",
                                         "Destination Network Unreachable for Type of Service",
                                         "Destination Host Unreachable for Type of Service",
                                         "Communication Administratively Prohibited",
                                         "Host Precedence Violation",
                                         "Precedence cutoff in effect"]
                            if is_error:
                                err_type = icmpType
                                err_code = icmpCode
                                error_desc = "Type: "+icmpType+" Code: "+icmpCode+"  "+code_desc[icmpCode]
                                try:
                                    address = gethostbyaddr(addr[0])[0] + " [" + addr[0] + "]"
                                except:
                                    address = addr[0]

                        elif icmpType == 0:                         # Echo Reply
                            is_done = True
                            is_error = False
                            RTT_list[i] = str(round((timeReceived - pingStartTime) * 1000)) + " ms"
                            try:
                                address = gethostbyaddr(addr[0])[0] + " [" + addr[0] + "]"
                            except:
                                address = addr[0]

                        else:
                            RTT_list[i] = "*\t"
                            if is_error:
                                try:
                                    address = gethostbyaddr(addr[0])[0] + " [" + addr[0] + "]"
                                except:
                                    address = addr[0]
                                error_desc = "error"
                except timeout:
                    RTT_list[i] = "*\t"
                    if is_error:
                        error_desc = "Request timed out (By Exception)."
                finally:
                    mySocket.close()
            print("Hop %d\t%s\t%s\t%s\t %s" %
                  (
                      self.getTtl(),
                      RTT_list[0],
                      RTT_list[1],
                      RTT_list[2],
                      address
                  ))
            if is_error:
                print("Error: Type=%s\tCode=%s\tDesc=%s" %
                      (
                          err_type,
                          err_code,
                          error_desc
                      ))

            return is_done

        def printIcmpPacketHeader_hex(self):
            print("Header Size: ", len(self.__header))
            for i in range(len(self.__header)):
                print("i=", i, " --> ", self.__header[i:i+1].hex())

        def printIcmpPacketData_hex(self):
            print("Data Size: ", len(self.__data))
            for i in range(len(self.__data)):
                print("i=", i, " --> ", self.__data[i:i + 1].hex())

        def printIcmpPacket_hex(self):
            print("Printing packet in hex...")
            self.printIcmpPacketHeader_hex()
            self.printIcmpPacketData_hex()

    # ################################################################################################################ #
    # Class IcmpPacket_EchoReply                                                                                       #
    #                                                                                                                  #
    # References:                                                                                                      #
    # http://www.networksorcery.com/enp/protocol/icmp/msg0.htm                                                         #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    class IcmpPacket_EchoReply:
        # ############################################################################################################ #
        # IcmpPacket_EchoReply Class Scope Variables                                                                   #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        __recvPacket = b''
        __IcmpSequenceNumber_isValid = False
        __IcmpIdentifier_isValid = False
        __IcmpData_isValid = False
        __isValidResponse = False
        __rtt = f''

        # ############################################################################################################ #
        # IcmpPacket_EchoReply Constructors                                                                            #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        def __init__(self, recvPacket):
            self.__recvPacket = recvPacket

        # ############################################################################################################ #
        # IcmpPacket_EchoReply Getters                                                                                 #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        def getIcmpType(self):
            # Method 1
            # bytes = struct.calcsize("B")        # Format code B is 1 byte
            # return struct.unpack("!B", self.__recvPacket[20:20 + bytes])[0]

            # Method 2
            return self.__unpackByFormatAndPosition("B", 20)

        def getIcmpCode(self):
            # Method 1
            # bytes = struct.calcsize("B")        # Format code B is 1 byte
            # return struct.unpack("!B", self.__recvPacket[21:21 + bytes])[0]

            # Method 2
            return self.__unpackByFormatAndPosition("B", 21)

        def getIcmpHeaderChecksum(self):
            # Method 1
            # bytes = struct.calcsize("H")        # Format code H is 2 bytes
            # return struct.unpack("!H", self.__recvPacket[22:22 + bytes])[0]

            # Method 2
            return self.__unpackByFormatAndPosition("H", 22)

        def getIcmpIdentifier(self):
            # Method 1
            # bytes = struct.calcsize("H")        # Format code H is 2 bytes
            # return struct.unpack("!H", self.__recvPacket[24:24 + bytes])[0]

            # Method 2
            return self.__unpackByFormatAndPosition("H", 24)

        def getIcmpIdentifier_isValid(self):
            return self.__IcmpIdentifier_isValid

        def getIcmpSequenceNumber(self):
            # Method 1
            # bytes = struct.calcsize("H")        # Format code H is 2 bytes
            # return struct.unpack("!H", self.__recvPacket[26:26 + bytes])[0]

            # Method 2
            return self.__unpackByFormatAndPosition("H", 26)

        def getIcmpSequenceNumber_isValid(self):
            return self.__IcmpSequenceNumber_isValid

        def getDateTimeSent(self):
            # This accounts for bytes 28 through 35 = 64 bits
            return self.__unpackByFormatAndPosition("d", 28)   # Used to track overall round trip time
                                                               # time.time() creates a 64 bit value of 8 bytes

        def getIcmpData(self):
            # This accounts for bytes 36 to the end of the packet.
            return self.__recvPacket[36:].decode('utf-8')

        def getIcmpData_isValid(self):
            return self.__IcmpData_isValid

        def getRtt(self):
            return self.__rtt

        def isValidResponse(self):
            return self.__isValidResponse

        # ############################################################################################################ #
        # IcmpPacket_EchoReply Setters                                                                                 #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        def setIsValidResponse(self, booleanValue):
            self.__isValidResponse = booleanValue

        def setIcmpSequenceNumber_isValid(self, booleanValue):
            self.__IcmpSequenceNumber_isValid = booleanValue

        def setIcmpData_isValid(self, booleanValue):
            self.__IcmpData_isValid = booleanValue

        def setIcmpIdentifier_isValid(self, booleanValue):
            self.__IcmpIdentifier_isValid = booleanValue

        def setRtt(self, rtt):
            self.__rtt = rtt

        # ############################################################################################################ #
        # IcmpPacket_EchoReply Private Functions                                                                       #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        def __unpackByFormatAndPosition(self, formatCode, basePosition):
            numberOfbytes = struct.calcsize(formatCode)
            return struct.unpack("!" + formatCode, self.__recvPacket[basePosition:basePosition + numberOfbytes])[0]

        # ############################################################################################################ #
        # IcmpPacket_EchoReply Public Functions                                                                        #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        #                                                                                                              #
        # ############################################################################################################ #
        def printResultToConsole(self, ttl, timeReceived, addr, seqNumber, identifier, data):
            bytes = struct.calcsize("d")
            timeSent = struct.unpack("d", self.__recvPacket[28:28 + bytes])[0]
            rtt = (timeReceived - timeSent) * 1000
            self.setRtt(rtt)
            print("  TTL=%d    RTT=%.0f ms    Type=%d    Code=%d        Identifier=%d    Sequence Number=%d    %s \n"
                  "  Valid Reply=%s                           Sent Identifier=%d    Sent Seq Number=%d \n"
                  "  Sent Data=%s      Reply Data=%s" %
                  (
                      ttl,
                      rtt,
                      self.getIcmpType(),
                      self.getIcmpCode(),
                      self.getIcmpIdentifier(),
                      self.getIcmpSequenceNumber(),
                      addr[0],
                      self.isValidResponse(),
                      identifier,
                      seqNumber,
                      data,
                      self.getIcmpData()
                  )
                 )

            # if the echo reply is invalid, inform where the inconsistency is
            if not self.getIcmpIdentifier_isValid():
                print("ERROR: Echo reply identifier number does not match sent identifier")
            if not self.getIcmpSequenceNumber_isValid():
                print("ERROR: Echo reply sequence number does not match sent sequence number")
            if not self.getIcmpData_isValid():
                print("ERROR: Echo reply data does not match sent data")

    # ################################################################################################################ #
    # Class IcmpHelperLibrary                                                                                          #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #

    # ################################################################################################################ #
    # IcmpHelperLibrary Class Scope Variables                                                                          #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    __DEBUG_IcmpHelperLibrary = False                  # Allows for debug output

    # ################################################################################################################ #
    # IcmpHelperLibrary Private Functions                                                                              #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def __sendIcmpEchoRequest(self, host):
        print("sendIcmpEchoRequest Started...") if self.__DEBUG_IcmpHelperLibrary else 0

        minRTT = None
        maxRTT = None
        avgRTT = None
        requestsSent = 4
        echoReceived = 0                # keep count of replies received to calculate packet loss rate
        RTTsum = 0                      # keep track of sum of RTT to calculate avg RTT
        for i in range(requestsSent):
            # Build packet
            icmpPacket = IcmpHelperLibrary.IcmpPacket()

            randomIdentifier = (os.getpid() & 0xffff)      # Get as 16 bit number - Limit based on ICMP header standards
                                                           # Some PIDs are larger than 16 bit

            packetIdentifier = randomIdentifier
            packetSequenceNumber = i

            icmpPacket.buildPacket_echoRequest(packetIdentifier, packetSequenceNumber)  # Build ICMP for IP payload
            icmpPacket.setIcmpTarget(host)
            if icmpPacket.sendEchoRequest():                                            # Build IP
                echoReceived += 1

            icmpPacket.printIcmpPacketHeader_hex() if self.__DEBUG_IcmpHelperLibrary else 0
            icmpPacket.printIcmpPacket_hex() if self.__DEBUG_IcmpHelperLibrary else 0
            # we should be confirming values are correct, such as identifier and sequence number and data

            # update min, max, and avg RTTs
            rtt = icmpPacket.getRtt()
            if minRTT is None or rtt < minRTT:
                minRTT = rtt
            if maxRTT is None or rtt > maxRTT:
                maxRTT = rtt
            if echoReceived > 0 and rtt:
                RTTsum += rtt
                avgRTT = RTTsum / echoReceived

        # Display min, max, and avg RTT, as well as packet loss rate %
        print()
        print("Min RTT=%.0f ms    Max RTT=%.0f ms    Avg RTT=%.1f ms    Packet Loss Rate=%.1f %%" %
              (minRTT,
               maxRTT,
               avgRTT,
               (requestsSent - echoReceived)/requestsSent))
        print()
        print()

    def __sendIcmpTraceRoute(self, host):
        print("sendIcmpTraceRoute Started...") if self.__DEBUG_IcmpHelperLibrary else 0
        # Build code for trace route here
        max_hops = 30
        ttl = 1
        host_ip = gethostbyname(host)
        print("Tracing route to (" + host + ") " + host_ip + "\nover a max of " + str(max_hops) + " hops:\n")
        while ttl < max_hops+1:
            # Build packet
            icmpPacket = IcmpHelperLibrary.IcmpPacket()
            randomIdentifier = (os.getpid() & 0xffff)  # Get as 16 bit number - Limit based on ICMP header standards
            # Some PIDs are larger than 16 bit
            packetIdentifier = randomIdentifier
            packetSequenceNumber = ttl
            icmpPacket.buildPacket_echoRequest(packetIdentifier, packetSequenceNumber)  # Build ICMP for IP payload
            icmpPacket.setIcmpTarget(host)
            icmpPacket.setTtl(ttl)
            if icmpPacket.sendTraceRouteEchoRequest():
                break

            ttl += 1

        print("Trace complete.")


    # ################################################################################################################ #
    # IcmpHelperLibrary Public Functions                                                                               #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def sendPing(self, targetHost):
        print("ping Started...") if self.__DEBUG_IcmpHelperLibrary else 0
        self.__sendIcmpEchoRequest(targetHost)

    def traceRoute(self, targetHost):
        print("traceRoute Started...") if self.__DEBUG_IcmpHelperLibrary else 0
        self.__sendIcmpTraceRoute(targetHost)


# #################################################################################################################### #
# main()                                                                                                               #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
#                                                                                                                      #
# #################################################################################################################### #
def main():
    icmpHelperPing = IcmpHelperLibrary()


    # Choose one of the following by uncommenting out the line
    # icmpHelperPing.sendPing("209.233.126.254")
    # icmpHelperPing.sendPing("www.google.com")
    # icmpHelperPing.sendPing("oregonstate.edu")
    # icmpHelperPing.sendPing("gaia.cs.umass.edu")
    # icmpHelperPing.traceRoute("oregonstate.edu")
    # icmpHelperPing.traceRoute("google.com")
    # icmpHelperPing.traceRoute("nintendo.com")
    # icmpHelperPing.traceRoute("nintendo.co.jp")
    # icmpHelperPing.traceRoute("nintendo.fr")
    # icmpHelperPing.traceRoute("nintendo.co.uk")


if __name__ == "__main__":
    main()

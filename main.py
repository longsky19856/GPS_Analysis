#!/usr/bin/python
# -*- coding: UTF-8 -*
import threading,time
import serial
import string
import re
class DATA_TIME:
    #def __init__(self,time,date):
    def __init__(self):
        self.time=''
        self.date=''
        self.year=''
        self.month=''
        self.day=''
        self.hour=''
        self.minute=''
        self.second=''

    def update_time(self):
        self.hour = self.time[0:2]
        self.minute = self.time[2:4]
        self.second = self.time[4:6]
        self.year = self.date[4:]
        self.month = self.date[2:4]
        self.day = self.date[0:2]

    def show_time(self):
        print "the data time is: ",self.year,self.month,self.day,self.hour,self.minute,self.second
class POSI_TION:
    def __init__(self):
        self.latitude=0
        self.longitude=0
        self.latitude_Degree=0
        self.latitude_Cent=0
        self.latitude_Second=0
        self.longitude_Degree=0
        self.longitude_Cent=0
        self.longitude_Second=0
    def position_get(self):

        self.latitude=self.latitude_Degree+self.latitude_Cent/60.0+self.latitude_Second/3600.0
        self.longitude=self.longitude_Degree+self.longitude_Cent/60.0+self.longitude_Second/3600.0
    def show_position(self):
        print "the position is: ", self.latitude, self.longitude


class GPS_INFO:
    def __init__(self):
        self.start=0
        self.end=0
        self.start_byte='GPRMC'
        self.end_byte='GPVTG'
        self.data=''
        self.positon=POSI_TION()
        self.gps_data_time=DATA_TIME()
class gps:
    gps_mess=GPS_INFO()

    def __init__(self,Port,rate):
        self.my_serial = serial.Serial()
        self.my_serial.port = Port
        self.my_serial.baudrate = rate
        self.my_serial.timeout = 1
        self.alive = False
        self.waitEnd = None
        self.thread_read = None

    def waiting(self):
        # 等待event停止标志
        if not self.waitEnd is None:
            self.waitEnd.wait()
    def start(self):
        self.my_serial.open()
        if self.my_serial.isOpen():
            self.waitEnd = threading.Event()
            self.alive = True
            self.thread_read = threading.Thread(target=self.Reader)
            self.thread_read.setDaemon(True)
            self.thread_read.start()
            return True
        else:
            return False

    def process(self,data):
        #print 'get :'+data
        if self.gps_mess.start==1:
            self.gps_mess.data += data
            if re.search(self.gps_mess.start_byte, self.gps_mess.data) == None:
                pass
            else:
                a= int(re.search(self.gps_mess.start_byte, self.gps_mess.data).span()[0])
                self.gps_mess.data=self.gps_mess.data[a:]
                if re.search(self.gps_mess.end_byte, self.gps_mess.data) == None:
                    pass
                else:
                    b= int(re.search(self.gps_mess.end_byte, self.gps_mess.data).span()[0])
                    self.gps_mess.data = self.gps_mess.data[a:b-3]
                    self.gps_mess.start = 0
                    print  self.gps_mess.data
                    print  self.gps_mess.data.split(',')
                    #self.gps_mess.time=self.gps_mess.data.split(',')[1]
                    if self.gps_mess.data.split(',')[2]=='A':
                        #updata message
                        """
                        self.gps_mess.gps_data_time.hour=self.gps_mess.data.split(',')[1][0:2]
                        self.gps_mess.gps_data_time.minute = self.gps_mess.data.split(',')[1][2:4]
                        self.gps_mess.gps_data_time.second = self.gps_mess.data.split(',')[1][4:6]
                        self.gps_mess.gps_data_time.year = self.gps_mess.data.split(',')[9][4:]
                        self.gps_mess.gps_data_time.month = self.gps_mess.data.split(',')[9][2:4]
                        self.gps_mess.gps_data_time.day = self.gps_mess.data.split(',')[9][0:2]
                        """
                        self.gps_mess.gps_data_time.time=self.gps_mess.data.split(',')[1]
                        self.gps_mess.gps_data_time.date=self.gps_mess.data.split(',')[9]

                        self.gps_mess.gps_data_time.update_time()
                        self.gps_mess.gps_data_time.show_time()
                        tmp=self.gps_mess.data.split(',')[3]
                        self.gps_mess.positon.latitude_Degree=int(float(tmp)/100)
                        self.gps_mess.positon.latitude_Cent=int(float(tmp))-self.gps_mess.positon.latitude_Degree*100
                        self.gps_mess.positon.latitude_Second=int((float(tmp)-int(float(tmp)))*60)
                        tmp = self.gps_mess.data.split(',')[5]
                        self.gps_mess.positon.longitude_Degree = int(float(tmp) / 100)
                        self.gps_mess.positon.longitude_Cent = int(float(tmp)) - self.gps_mess.positon.longitude_Degree * 100
                        self.gps_mess.positon.longitude_Second = int((float(tmp) - int(float(tmp))) * 60)
                        self.gps_mess.positon.position_get()
                        self.gps_mess.positon.show_position()









        else:
            if re.search('$',data)==None:
                #print data
                pass
            else:
                self.gps_mess.start = 1
                self.gps_mess.data=data
                #print data

    def Reader(self):
        while self.alive:
            try:
                n = self.my_serial.inWaiting()
                data = ''
                if n:
                    #data = self.my_serial.read(n).decode('utf-8')
                    data = self.my_serial.read(n)
                    #print ('recv' + ' ' + time.strftime("%Y-%m-%d %X") + ' ' + data.strip())
                    #print ( data.strip())
                    self.process(data)
            except Exception as ex:
                print (ex)

        self.waitEnd.set()
        self.alive = False


    def stop(self):
        self.alive = False
        # self.thread_read.join()
        # self.thread_send.join()
        if self.my_serial.isOpen():
            self.my_serial.close()

if __name__=='__main__':
    ser=gps('com18',9600)
    try:
        if ser.start():
            ser.waiting()
            ser.stop()
        else:
            pass;
    except Exception as ex:
        print (ex)

    if ser.alive:
        ser.stop()

    print ('End OK .')
    del ser




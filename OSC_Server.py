import liblo
import sys
import time
from BitalinoRun import bitalino_run
# from to_plot_pyqt import HelloWindow


class OSCreceive:
    def __init__(self, receiveport):

        self.server = liblo.Server(receiveport) #Create sever instance
        #add methods
        self.server.add_method("/connect", None, self.startendECG_msg)  # Adds function to handle messages
        self.server.add_method("/sonification", None, self.sonification_settings)  # Adds function to handle messages


        #Initialize variables
        self.sonificationType = "Blip"
        self.sonificationVolume = 0.3
        print("\nStarting OSCServer. Use ctrl-C to quit.")

        while True: #Run server
            self.server.recv(10)



    def startendECG_msg(self,path, args):
        if path == "/connect":
            i = args
            print("received message '%s' with arguments '%s'" % (path, i))
            if args[0] == '1':
                print ('starting ECG acquisition')

                self.bit_thr = bitalino_run(args[0], 1000.0, self.sonificationType, self.sonificationVolume)  # Initialize Bitalino thread
                self.bit_thr.start()

                # self.plot_thr = HelloWindow()  # Initialize GUI thread
                # self.plot_thr()

                # self.bitalino = Bitalino_signal(args[0], 1000.0)  # Initialize Bitalino

            if args[0] == '0':
                print ('stoping ECG acquisition')
                self.bit_thr.stop();
                # self.plot_thr.stop()

    def update_sonification_values(self):
        print ('Update called')
        print (('updated values are: %s and %s') % (self.sonificationType, self.sonificationVolume))
        return self.sonificationType, self.sonificationVolume


    def sonification_settings(self, path, args):
        print (args)
        if path == "/sonification":
            # print 'Sonification settings received'
            print (args)
            if args[0] == 'Blip':
                self.sonificationType = 'Blip'
                self.sonificationVolume = args[1]
                # self.update_sonification_values(self)
                self.sonificationType, self.sonificationVolume = self.update_sonification_values()
                print ('We are in A')
                self.bit_thr.set_sony(self.sonificationType)

            elif args[0] == 'Marimba':
                self.sonificationType = 'Marimba'
                self.sonificationVolume = args[1]
                # self.update_sonification_values(self)
                self.sonificationType, self.sonificationVolume = self.update_sonification_values()
                print ('We are in B')
                self.bit_thr.set_sony(self.sonificationType)

            if args[0] == 'Water':
                self.sonificationType = 'Water'
                self.sonificationVolume = args[1]
                # self.update_sonification_values(self)
                self.sonificationType, self.sonificationVolume = self.update_sonification_values()
                print ('We are in C')
                self.bit_thr.set_sony(self.sonificationType)

            elif args[0] == 'ECGgrains':
                self.sonificationType = 'ECGgrains'
                self.sonificationVolume = args[1]
                # self.update_sonification_values(self)
                self.sonificationType, self.sonificationVolume = self.update_sonification_values()
                print('We are in D')
                self.bit_thr.set_sony(self.sonificationType)

            elif args[0] == 'Morph':
                self.sonificationType = 'Morph'
                self.sonificationVolume = args[1]
                # self.update_sonification_values(self)
                self.sonificationType, self.sonificationVolume = self.update_sonification_values()
                print ('We are in C')
                self.bit_thr.set_sony(self.sonificationType)


#

receive_port  = 5001
#Start OSC server
oscserver= OSCreceive(receive_port)

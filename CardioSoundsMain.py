print ("This is CardioSounds")

#Import libraries

import liblo
from start_bitalino import bitalino_run


class OSCreceive:
    def __init__(self, receiveport):

        self.server = liblo.Server(receiveport) #Create sever instance
        #add OSC receiving methods
        self.server.add_method("/connect", None, self.startendECG_msg)  # connection on/off
        self.server.add_method("/sonification", None, self.sonification_settings)  # sonification settings


        #Initialize variables and sonification parameters
        self.sonificationType = "Blip"
        self.sonificationVolume = 0.3
        print("\nStarting OSCServer. Use ctrl-C to quit.")

        while True: #Run server
            self.server.recv(2)


    def startendECG_msg(self, path, args):
        if path == "/connect":
            i = args
            print("received message '%s' with arguments '%s'" % (path, i))

            if args[0] == 1:
                print ('starting ECG signal acquisition with BITalino')

                self.bit_thr = bitalino_run(args[0], 1000.0, self.sonificationType, self.sonificationVolume)  # Initialize Bitalino thread
                self.bit_thr.start()

            if args[0] == 0:
                print ('stoping ECG acquisition')
                self.bit_thr.stop();

    def update_sonification_values(self):
        print ('Update called')
        print (('updated values are: %s and %s') % (self.sonificationType, self.sonificationVolume))
        return self.sonificationType, self.sonificationVolume


    def sonification_settings(self, path, args):
        print (args)
        #select a sonification type
        if path == "/sonification":
            # print 'Sonification settings received'
            print (args)
            if args[0] == 'Blip':
                self.sonificationType = 'Blip'
                self.sonificationVolume = float(args[1])
                # self.update_sonification_values(self)
                self.sonificationType, self.sonificationVolume = self.update_sonification_values()
                print ('We are in A/Blip')
                self.bit_thr.set_sony(self.sonificationType, self.sonificationVolume)

            elif args[0] == 'Marimba':
                self.sonificationType = 'Marimba'
                self.sonificationVolume = args[1]
                # self.update_sonification_values(self)
                self.sonificationType, self.sonificationVolume = self.update_sonification_values()
                print ('We are in B')
                self.bit_thr.set_sony(self.sonificationType, self.sonificationVolume)


            elif args[0] == 'ECGgrains':
                self.sonificationType = 'ECGgrains'
                self.sonificationVolume = args[1]
                # self.update_sonification_values(self)
                self.sonificationType, self.sonificationVolume = self.update_sonification_values()
                print('We are in D')
                self.bit_thr.set_sony(self.sonificationType, self.sonificationVolume)

            if args[0] == 'Water':
                self.sonificationType = 'Water'
                self.sonificationVolume = args[1]
                # self.update_sonification_values(self)
                self.sonificationType, self.sonificationVolume = self.update_sonification_values()
                print('We are in C')
                self.bit_thr.set_sony(self.sonificationType, self.sonificationVolume)


receive_port  = 5001
#Start OSC server:
oscserver= OSCreceive(receive_port)

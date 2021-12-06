import bitalino
import time, signal, sys, os
import ecgprocpy3
from scipy import signal as scsi
import pyson
import pandas as pd
import forecast
from supercollidersc import SuperColliderClient, OSCsend_receive

# import matplotlib.pylab as plt
# import matplotlib.pyplot as plt

#Plot backend:
import matplotlib
# matplotlib.use('TkAgg')
# matplotlib.use('Qt5Agg')
from pylab import *



class bitalino_run(threading.Thread):
    def __init__(self, activation, samplingrate, sonificationType, sonificationVolume):

        self.lock = threading.RLock()

        super(bitalino_run, self).__init__()
        self._stop_event = threading.Event()
        self.activation = activation
        self.SamplingRate = samplingrate
        self.sonificationType = sonificationType
        self.sonificationVolume = sonificationVolume
        self.runFlag = False
        self.toplot = False
        self.runSon = False
        self.sonFrom = 'file'
        print ('init completed')
        # signal.signal(signal.SIGINT, self.signal_handler)  # To close connection to BITalino

    def set_sony(self, sony, volume):
        with self.lock:
            self.sony = sony
            self.volume = volume
            self.sonificationType = self.sony #Updates sonification type
            self.sonificationVolume = self.volume


    # def plot_ecg(self, data, winwid, ax1):
    def plot_ecg(self, data):

        # while toploti < (lenfileinsamp / nSamples) - 1:
        while self.toplot == False:
            # print toploti
            clf()
            fig = plt.figure(1);
            ax1 = fig.add_subplot(111)
            # ion();
            winwid = 1000
            axis([0, winwid , -0.7, 0.8]);
            ax1.plotECG, = plot([], "r", lw=1, label='')
            title('ECG signal')
            ylabel('Amplitude [mV]')
            # xlabel('Samples')
            
            # print ('Run plotting function')
            if len(data) <= winwid:
                ax1.plotECG.set_data(range(len(data)), data)
            else:
                ax1.plotECG.set_data(range(winwid), data[len(data) - winwid:len(data)])

            draw()
            pause(0.005)
            plt.title('ECG signal')
            # time.sleep(0.05)

    def sonification_run_withOSCmesages(self, sonificationType, sonificationVolume):
        while self.runSon == True:
            # print 'a sonification is running'
            # print ('Sonification type is: %s') % (sonificationType)
            print ('Sonification type is: %s') % (self.sonificationType)
            time.sleep(1.0)

    def run(self):
        print ('run called, starting ECG acquisition')
        self.runFlag = True
        self.toplot = True
        self.runSon = True
        #directory in which data is written to
        fname = datetime.datetime.now().strftime("ecgdata-%Y%m%d-%H%M%S" + ".csv")  # File Name
        self.writedatatodisk = open(os.getcwd() + "/recorded_data/" + fname, "w")  # Open CSV file


        if self.sonFrom == 'file':

            SamplingRate = 1000.0
            #open an ecg data file:
            inputfile = os.getcwd() + "/baseline_data/healthy01.csv"
            filedata = (pd.read_csv(inputfile, header=0, delimiter=' ')).to_numpy()
            lenfileinsamp = len(filedata)

        elif self.sonFrom == 'bitalino':

            print ('Connecting to bitalino...please wait')
            #Devices's macAdress
            macAddress = "/dev/tty.BITalino-99-36-DevB"
            macAddress.encode()
            #if in use with a RaspberryPi:
            # macAddress = "20:xx:xx:xx:xx:xx" #RaspberryPi
            b = bytes(macAddress, 'utf-8')
            print (type(macAddress))
            print(type(b))

            self.device = bitalino.BITalino(macAddress, 10)  # timeout
            # Start Acquisition in Analog Channels 0 and 3 #ch2 = A3
            self.device.start(self.SamplingRate, [0, 1, 2, 3, 4])
            print ('BITalino connected')

        # Create OSC clients
        scserver = SuperColliderClient()
        oscother = OSCsend_receive("127.0.0.1", 57120)  # osc messages to the language
        # Send the messages according to their respective time tag

        sonification = self.sonificationType
        self.nodeid = 10


        dataAcquired = []  # List for storing acquired data
        dtsamples = (1 / self.SamplingRate)  # Time between samples
        buf_size = 200  # Buffer size
        nSamples = 100  # Number fo samples to read in each iteration
        amp_buffer = []  # Amplitudes buffer
        time_buffer = []  # time_buffer= zeros((30000, 2))
        tlist = [];
        tref = 0;  # Values for calculating time between samples in each iteration
        frbufflag = 0  # Variable to determine if the buffer is getting full for the first time (more time needed)

        self.all_amp_data = []  # List that stores all the acquired amplitude data, not only the buffered
        all_times_data = []  # List that stores all the acquired times data, not only the buffered
        toploti = 0
        omax = 0.001;
        omin = -0.001;
        thld = 0.3  # Values used in adaptative threshold for R peaks detection
        # Number of R peaks
        peaksct = 0
        Rpeaks = []
        RRdeltas = []
        Rpksinxsec = []
        HR = 0
        self.i = 0

        # For RRdelta forecast
        self.act_onset = 0
        self.old_act_onset= 0
        self.exp_onset = 0
        #Number of peaks to store to make the forecast:
        self.ntoforecast = 10

        # nSamples = 1
        timecompressionfactor = 1
        tsleepvalue = dtsamples * nSamples / timecompressionfactor

        #For st calculation
        st_average = []  # List for storing 3 st segment values and calculating amplitude
        stvalue = 0  # starting st value
        sec_counter = 0
        # starting Rdt value:
        Rdt = 1.0

        thread_plot = threading.Thread(target=self.plot_ecg, args=(self.all_amp_data, ))
        thread_plot.start()


        topi = lenfileinsamp / nSamples

        while self.runFlag:
            #Read data:

            self.nodeid +=1

            if self.sonFrom == 'file':

                spl_ct = self.i * nSamples
                # dataAcquired.extend(filedata[spl_ct:spl_ct + nSamples, 0])  # Reads lead I #Physionet long files
                dataAcquired.extend(filedata[spl_ct:spl_ct + nSamples, 1])  # Reads lead I #BItalino

                time.sleep(tsleepvalue)  # Simulate Sampling Rate from Bitalino
                scaleddata = dataAcquired[:] * 1
                self.i += 1

                if self.i == topi - nSamples:
                    self.i = 0
                    print ('Restarting i')

            if self.sonFrom == 'bitalino':
                # Process
                dataAcquired = self.device.read(nSamples)
                # Scaling BITalino ECG data according to documentation:
                scaleddata = ((dataAcquired[:, 5] * 3.3 / 2 ** 10 - 3.3 / 2) / 1100) * 1000

            for x in range(nSamples):  # Append times from 1 to 50 samples (nSamples)
                tlist.append(tref)
                tref = tref + dtsamples
            # Buffer update according to nSamples
            if (len(amp_buffer) <= buf_size - 1):  # if the amp buffer has not been filled
                amp_buffer.extend(scaleddata)  # add nSamples of ECG data to amplitudes buffer
                time_buffer.extend(tlist)  # Add times of the first nSamples to the times buffer
            else:  # When the amp buffer has been filled
                amp_buffer.extend(scaleddata)  # add nSamples of ECG data to amplitudes buffer
                time_buffer.extend(tlist)  # add times of the last nSamples
                del amp_buffer[
                    0:nSamples]  # Push, Pop #amp buffer always has buf_size samples, the final (200) buf_size samples
                del time_buffer[0:nSamples]  # Push, Pop
            tlist = []  # Empty times list (length nSamples)
            dataAcquired = []  # Empty starting acquire data buffer (length nSamples)

            if len(amp_buffer) >= buf_size:  # After filling, amp_buffer always has buf_size number of samples
                data_mean_dc = np.mean(amp_buffer)
                shifted_data = amp_buffer - data_mean_dc
                if frbufflag == 0:  # Filtering and signal processing is done in nSamples buffer, also the writing.
                    f_buffer = shifted_data[0:]  # The first time, all 200 samples are added
                    print (self.SamplingRate)
                    filtereddata = ecgprocpy3.lpIIR_filter(f_buffer, 70.0,
                                                        self.SamplingRate)  # Low pass after notch filter
                    filterforpeaks = ecgprocpy3.bpIIR_filter(filtereddata, 8.0, 30.0, self.SamplingRate)
                    self.all_amp_data.extend(filtereddata)  # Only one time append all samples in the first buffer
                    all_times_data.extend(time_buffer)  # Only one time append all samples in the first buffer
                    # # Hilbert transform
                    ht = abs(scsi.hilbert(filterforpeaks))
                    nnma, nnmi, maxbuf, minbuf, updated_th_flag = ecgprocpy3.update_thr(np.max(ht), np.min(ht), omax,
                                                                                     omin)  # maxand min from ht
                    omax = nnma;
                    omin = nnmi;
                    updated_th = (maxbuf - minbuf) * 0.6  # update peaks threshold
                    frbufflag = 1  # From now on, only append nSamples to final buffer
                    data = np.array([time_buffer, filtereddata])  # The first time bif_size samples are added
                    data = data.T
                    np.savetxt(self.writedatatodisk, data, fmt=['%s', '%s'])

                elif frbufflag == 1:
                    f_buffer = shifted_data[-nSamples:]  # Filter only the last added set of samples
                    filtereddata = ecgprocpy3.lpIIR_filter(f_buffer, 70.0,
                                                        self.SamplingRate)  # Low pass after notch filter
                    filterforpeaks = ecgprocpy3.bpIIR_filter(filtereddata, 8.0, 30.0, self.SamplingRate)
                    self.all_amp_data.extend(filtereddata)
                    all_times_data.extend(time_buffer[-nSamples:])  # Only add the times for the last nSamples
                    # # Hilbert transform
                    ht = abs(scsi.hilbert(filterforpeaks))
                    nnma, nnmi, maxbuf, minbuf, updated_th_flag = ecgprocpy3.update_thr(np.max(ht), np.min(ht), omax,
                                                                                     omin)  # maxand min from ht
                    omax = nnma;
                    omin = nnmi;
                    updated_th = (maxbuf - minbuf) * 0.7  # 20 percent of range #or 0.3 for waveform

                    # Record to CSV all samples in current buffer
                    data = np.array(
                        [time_buffer[-nSamples:], filtereddata])  # The first time bif_size samples are added
                    data = data.T
                    np.savetxt(self.writedatatodisk, data, fmt=['%s', '%s'])


                # Peak detection
                if updated_th_flag == 1: thld = updated_th;  # update threshold value for R peaks detection
                # print thld
                if len(self.all_amp_data) % buf_size == 0:  # Looks for peaks every time 200 samples are added to final buffer
                    foundRpeak = ecgprocpy3.R_peaks_detection_02(self.all_amp_data[-buf_size:], all_times_data[-buf_size:],
                                                              thld)  # Find peaks with new implementation in time series
                    if foundRpeak is not None:  # If a peak was found
                        print ("R Peak detected")
                        peaksct += 1
                        Rpeaks.append(foundRpeak)  # Stores found R peaks (time, amp, and sample in buffer window)
                        Rpksinxsec.append(foundRpeak) #List of peaks in 2 seconds used in ST elevation calculation

                        if len(Rpeaks) >= 2:  # if we have at least two R peaks
                            RRdeltas.append(Rpeaks[-1][0] - Rpeaks[-2][0]) #Calculate time difference between the last peaks
                            # self.act_onset = Rpeaks[-1][0]
                            #CardioSounds Forecast Sonification
                            if len(RRdeltas) >= self.ntoforecast: #If we have n=5 peaks stored

                                print (('before last peak %s y last peak %s ')%(Rpeaks[-2][0], Rpeaks[-1][0]))
                                datadur = int((Rpeaks[-1][0]-Rpeaks[-self.ntoforecast][0])*self.SamplingRate) #Amplitude within the last n=5 peaks
                                f_av, f_lr, mav = forecast.forecast_peaks(self.all_amp_data[-datadur:], RRdeltas[:-1], self.ntoforecast)
                                #use linear regression prediction:
                                next_peak_forecast_ave = f_lr

                                #Actual and expected onset
                                self.exp_onset = Rpeaks[-2][0] + f_av
                                self.act_onset = Rpeaks[-1][0]
                                print (self.act_onset)
                                print (self.exp_onset)
                                ant_signal = np.abs(self.act_onset - self.exp_onset)

                                print ('sonification is: %s')
                                print (sonification)


                                #Calculate duration of the P wave
                                peakdur= int((Rpeaks[-1][0]-Rpeaks[-2][0])*self.SamplingRate) #Amplitude within the last n=5 peaks
                                length_p_wave, exp_len_pwave = forecast.p_wave_count(self.all_amp_data[-peakdur:], self.SamplingRate,f_av, mav)
                                lastRR_value = RRdeltas[-1]
                                print (('Length of P wave %s')%(length_p_wave))

                                if self.sonificationType == 'Blip':

                                    if self.exp_onset < self.act_onset:
                                        freq = 400
                                    else:
                                        freq = 800
                                    scserver.sc_msg("/s_new", ["basic_synth", 1001+self.nodeid, 1, 0, "freq",
                                                     freq, "pan", 0, "amp", float(self.sonificationVolume), "att", 0.001, "dur", ant_signal])

                                if self.sonificationType == 'ECGgrains':

                                    freq = pyson.midicps(pyson.linlin(length_p_wave, 0.0, exp_len_pwave, 82, 60))  # Log freq mapping
                                    numtrig = pyson.linlin(ant_signal, 0.0, lastRR_value, 0.0, 20)
                                    scserver.sc_msg("/s_new", ["grain_sin_test", 2001 + self.nodeid, 1, 0, "freq",
                                                               freq, "numtriggers", numtrig, "amp", float(self.sonificationVolume), "dur",
                                                               lastRR_value])

                                if self.sonificationType == 'Marimba':

                                    numtrig = pyson.linlin(ant_signal, 0.0, lastRR_value, 0.0, 20)
                                    scserver.sc_msg("/s_new", ["marimba", 3001 + self.nodeid, 1, 0, "buf", np.random.randint(5,7) ,"numtriggers", numtrig, "amp", float(self.sonificationVolume), "envdur,", lastRR_value])

                                #Heart rate caluclation:
                                HR = int(60 / next_peak_forecast_ave)  # HR = int(60 / (Rpeaks[-1][0] - Rpeaks[-2][0]))
                                print(("Heart rate is: %s") % (HR))
                                RRdeltas.pop(0)  # delete one value from hrmean list
                                Rdt = next_peak_forecast_ave # This is used in the ST segment elevation calculation


                #ST segment calculation
                if len(self.all_amp_data) % (SamplingRate * 2) == 0:
                    sec_counter = sec_counter + 2
                    qrs, qst, iso, pr = ecgprocpy3.seg_dur_for_analysis(np.mean(Rdt),
                                                                     SamplingRate)  # calculate segments duration based on dt
                    rpks = [x[0] for x in Rpksinxsec]  # Take all peaks stored in x second of data
                    for item in rpks:
                        current_peak_insamp = item * SamplingRate  # Peak occurrence [within x second] expressed in samples
                        if current_peak_insamp + (
                            Rdt * SamplingRate) < sec_counter * SamplingRate:  # If there is enough data to calculate ST
                            # print 'Time to calculate ST'
                            isomean, st_ampinmv, ststats, _ = ecgprocpy3.st_elevation_detection_02(self.all_amp_data[int(-SamplingRate * 2):], int(current_peak_insamp),
                                sec_counter * SamplingRate, SamplingRate * 2)
                            st_average.append(st_ampinmv)
                        else:
                            pass
                    Rpksinxsec = []  # clean peaks stored each second


                    # updating ST value
                if len(st_average) > 3:
                    stvalue = np.mean(st_average)  # average st value for the sonification
                    print (('st value is: %f') % (stvalue))
                    st_average.pop(0)  # Calculate ST based on last 3 values

    def stop(self):
        self.runFlag = False
        if self.sonFrom == 'bitalino':
            self.device.stop()  # Stop acquisition
            self.device.close()
        print ("Stop it called. ")
        self.toplot = False
        self.runSon = False
        self.i = 0
        print ('all close statements executed')

    def stopped(self):
        print ('Stopped function called')
        return self._stop_event.is_set()

    def signal_handler(self):
        print('You pressed Ctrl+C!')
        self.device.stop()  # Stop acquisition
        self.device.close()
        sys.exit(0)

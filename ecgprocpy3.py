from scipy import signal
import numpy as np


# import matplotlib.pyplot as plt

def set_gui(_gui):
    global gui
    gui = _gui

def bpIIR_filter(data, fc1, fc2, SR):
    # Band pass filter design
    cutoffpass = fc1 / (SR / 2.0);
    cutoffstop = fc2 / (SR / 2.0)  # 5.0 inferior cf, 70.0
    b, a = signal.iirfilter(4, [cutoffpass, cutoffstop], btype='bandpass', analog=False, ftype='butter')
    # Apply High pass filter
    signalfilt = signal.filtfilt(b, a, data)
    return signalfilt


def hpIIR_filter(data, fc1, SR):
    cutoffpass = fc1 / (SR / 2.0);
    b, a = signal.iirfilter(2, cutoffpass, btype='high', analog=False, ftype='butter')
    signalfilt = signal.filtfilt(b, a, data)
    return signalfilt


def lpIIR_filter(data, fc1, SR):
    cutoffpass = fc1 / (SR / 2.0);
    b, a = signal.iirfilter(4, cutoffpass, btype='low', analog=False, ftype='butter')
    signalfilt = signal.filtfilt(b, a, data, method='gust')
    return signalfilt


def bpFIR_filter(data, fil_len, fc1, fc2, SR):
    cutoffpass = fc1 / (SR / 2.0);
    cutoffstop = fc2 / (SR / 2.0)
    b = signal.firwin(fil_len, [cutoffpass, cutoffstop], pass_zero=False, window='hamming')
    signalfilt = signal.lfilter(b, [1.0], data)
    return signalfilt


def notch_filter(data, fc1, SR, Q):
    notchfreq = fc1 / (SR / 2.0);
    b, a = signal.iirnotch(notchfreq, Q)
    signalfilt = signal.filtfilt(b, a, data)
    return signalfilt


def notch_filter_02(data, fc1, fc2, SR):
    cutoffpass = fc1 / (SR / 2.0);
    cutoffstop = fc2 / (SR / 2.0)  # 5.0 inferior cf, 70.0
    b, a = signal.iirfilter(2, [cutoffpass, cutoffstop], btype='bandstop', analog=False, ftype='butter')
    # Apply bandstop
    signalfilt = signal.filtfilt(b, a, data)
    return signalfilt


def running_mean(data, winlen):
    cumsum = np.cumsum(np.insert(data, 0, 0))
    return (cumsum[winlen:] - cumsum[:-winlen]) / winlen


def R_peaks_detection_02(ampdata, timedata, thld):
    detected_peaks = []
    lastPeak = []
    aboveThreshold = False
    # lastAboveThreshold = False
    for x in range(len(ampdata)):
        lastAboveThreshold = aboveThreshold
        curValue = ampdata[x]
        if curValue > thld:
            aboveThreshold = True
        else:
            aboveThreshold = False

        if aboveThreshold == True:
            if len(lastPeak) == 0 or curValue > lastPeak[1]:
                lastPeak = [timedata[x], ampdata[x], x]
        if lastAboveThreshold == True and aboveThreshold == False:
            detected_peaks.append(lastPeak)
            lastPeak = []

        lastAboveThreshold = aboveThreshold

    if len(detected_peaks) > 0:  # select max peak among peaks found
        peakamp, loc = max([(x[1], i) for i, x in enumerate(detected_peaks)])
        selectedpeak = detected_peaks[loc]
        return selectedpeak


def R_peaks_detection_simplified(ampdata, timedata, thld):
    detected_peaks = []
    lastPeak = []
    aboveThreshold = False
    # lastAboveThreshold = False
    for x in range(len(ampdata)):
        lastAboveThreshold = aboveThreshold
        curValue = ampdata[x]
        if curValue > thld:
            aboveThreshold = True
        else:
            aboveThreshold = False

        if aboveThreshold == True:
            if len(lastPeak) == 0 or curValue > lastPeak[1]:
                lastPeak = [timedata[x], ampdata[x]]
        if lastAboveThreshold == True and aboveThreshold == False:
            detected_peaks.append(lastPeak)
            lastPeak = []

        lastAboveThreshold = aboveThreshold

    if len(detected_peaks) > 0:  # select max peak among peaks found
        peakamp, loc = max([(x[1], i) for i, x in enumerate(detected_peaks)])
        selectedpeak = detected_peaks[loc]
        return selectedpeak


maxbuf = []
minbuf = []
buf_ct = []


def update_thr(nmax, nmin, omax, omin):
    if nmax > omax:
        omax = nmax
    if nmin < omin:
        omin = nmin
    maxbuf.append(omax)
    minbuf.append(omin)
    buf_ct.append([omax, omin])
    if len(maxbuf) > 5:  # 200 ms
        maxbuf.pop(0)
        minbuf.pop(0)
    mean_max_buf = np.mean(maxbuf)
    mean_min_buf = np.mean(minbuf)
    nnmax = omax
    nnmin = omin
    if len(buf_ct) > 5:
        up_flag = 1  # update threshold every 5 cycles of nSamples
    else:
        up_flag = 0
    return nnmax, nnmin, mean_max_buf, mean_min_buf, up_flag


def seg_dur_for_analysis(dt, SampleRate):
    dtinms = dt * 1000  # calculated dt in seconds to milisconds
    calc_qrs_width = 1 / 10.0 * (dtinms)  # ms #QRS is aprox 1/10 of the RR
    QRSdur = ((
                          calc_qrs_width / 2) * SampleRate) / 1000.0  # Half of the QRS width in samples according to calculated QRS width
    calc_qt_interval = (dtinms) / 2.5  # ms #QT is aprox 2.5 of the RR according to pdf
    qtc = (calc_qt_interval / 1000) / np.sqrt(dt)  # In seconds
    qtcinms = qtc * 1000
    calc_qt_interval = qtcinms  # Corrected QTC
    qstintdur = ((calc_qt_interval * SampleRate) / 1000.0)  # +QRSdur #ST duration in samples is qt
    pr_int_dur = (dtinms) / 6.25  # ms #PR is aprox 6.25 of the RR according to pdf
    iso_dur = ((dtinms - calc_qt_interval - pr_int_dur) * SampleRate) / 1000.0  # iso_dur in samples
    return int(QRSdur), int(qstintdur), int(iso_dur), int(pr_int_dur)


def st_elevation_detection_02(data, peak, sec_counter, timeanywin, QRSdur=40, qstintdur=270,
                              iso_dur=150):  # new_st_elevation_detection_02
    # Peaks should be in samples
    st_extracted_vec = []
    ststats = []

    peak = int(peak - sec_counter + timeanywin)

    datasel = data[
              peak - QRSdur + qstintdur:peak - QRSdur + qstintdur + iso_dur]  # estimation as explained in the paper
    isomeans = (np.mean(datasel))  # Calculate mean of isoelectric part
    # ST-Segment STATS
    stsel = data[peak + QRSdur:peak + QRSdur + qstintdur]  #
    ststats.append([np.max(stsel), np.var(stsel)])  # Max value (T wave amp) and variance
    # Extract the vector of the ST segment
    st_extracted_vec.append(stsel)  # Max value (T wave amp) and variance
    # Calculate amplitude in mV in st segment
    stselection = QRSdur

    # for p in range(len(peak)):
    calc_range = data[peak + QRSdur:peak + QRSdur + stselection]  # Calculate amp in defined range
    st_ampinmv = abs(np.mean(calc_range) - isomeans)

    return isomeans, st_ampinmv, ststats, st_extracted_vec
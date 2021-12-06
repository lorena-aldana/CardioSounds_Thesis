
from sklearn import linear_model
from pylab import *

def forecast_peaks(data, rr_deltas, forecast_window):
    '''Based on incoming detected peaks and the rr deltas calculated, this function forecasts the next R peak'''

    mav = zeros(shape(data))
    # Forecast moving average
    m_average = mean(data) #Calculate moving average
    # mav = m_average  # It is stationary
    mav.fill(m_average) #Fill mav vector with value of last n peaks
    rpf_mav = average(rr_deltas) #This is the forecasted value

    # Linear regression model
    model = linear_model.LinearRegression()
    #Forecast linear regression
    xdata = linspace(0, len(rr_deltas) - 1, len(rr_deltas))  # xdata [0, 1, 2, 3, 4]

    x = reshape(xdata, (-1, 1))  # Reshape to use scikit learn with 1d dataset
    y = reshape(rr_deltas, (-1, 1))  # Reshape to use scikit learn with 1d dataset
    #fit model
    model.fit(x, y)
    # rpf_lr = model.predict([x[-1], y[-1]])  # Forecast to n= 5
    #predict next rr delta:
    rpf_lr = model.intercept_ + forecast_window * model.coef_

    print (('Returning from forecast function, moving average forecast: %s, linear regression forecast: %s')%(rpf_mav, float(rpf_lr[0])))

    return rpf_mav, float(rpf_lr[0]), mav

#
def p_wave_count(data, sr, rr, mav):
    '''Estimates length of P wave based on previously calculated average int the signal'''
    pqint_refdur_s = int((0.2*rr) * sr)  # 160 ms
    h_qrs_width_s = int((0.05*rr) * sr)  # 50 ms
    qtinterval = int ((0.4*rr) *sr) #400 ms
    above_ct = 0
    p_exp_dur = int((rr * 0.11) * sr)  # In samples
    # print (('Len data: %s and Expected duration of the P wave is: %s, RR values is: %s')%(len(data), p_exp_dur, rr))

    pwavesearch_area= data[qtinterval-h_qrs_width_s-h_qrs_width_s:-pqint_refdur_s-h_qrs_width_s]
    # print (('pwave search are has %s samples ') %(len(pwavesearch_area)))

    if len(pwavesearch_area)> 0:
        for i in range(len(pwavesearch_area)):
            # number of P wave points above mean
            ocu_ab_p = [above_ct + 1 for ma, ecgs in zip(mav, pwavesearch_area) if ecgs > ma]
    else:
        # print (('Short snippet, P wave expected duration: %s ')%(p_exp_dur))
        ocu_ab_p = p_exp_dur

    return sum(ocu_ab_p), p_exp_dur


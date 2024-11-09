from backend.src.api import fetch_historical_data
import pandas as pd

def getData(ticker,period, interval):
    """
     The first three char of interval  are numbers => 00
     The fourth char of interval is unit of time =>  m:minute / h : hour
    """
    if(interval[3]=="m"):
        data_frame = fetch_historical_data(ticker, period, "1m")
        return data_frame

    elif(interval[3] == "h"):
        if(interval=="001h"):
            return fetch_historical_data(ticker, period, "1h")
        data_frame = fetch_historical_data(ticker, period, "1h")
        dt = pd.DataFrame()
        Ninterval =int(interval[0:3])
        for n in range(0,int((len(data_frame)+1)/Ninterval),Ninterval):
            timestr =data_frame.index[n].strftime('%Y-%m-%d %X')
            idx=[pd.Timestamp(year=int(timestr[0:4]), month=int(timestr[5:7]), day=int(timestr[8:10]), hour=int(timestr[11:13]),minute=int(timestr[14:16]),second=int(timestr[17:19]))]

            data = {
                "Open": [data_frame.Open.iloc[n]],
                "Close": [data_frame.Close.iloc[n+Ninterval-1]],
                "High": [data_frame.High.iloc[n:n+Ninterval].max()],
                "Low": [data_frame.Low.iloc[n:n+Ninterval].min()],
                "Dividends": [0]
            }
            dt=dt._append(pd.DataFrame(data,index=pd.Index(idx)))
        return dt

#d=getData("ADA-USD", '1mo', "002h")
#print(d)
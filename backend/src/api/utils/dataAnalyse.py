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
        data_frame = fetch_historical_data(ticker, period, "1h")
        #for n in range(1,len(data_frame)+1,3):
        timestr =data_frame.index[0].strftime('%Y-%m-%d %X')
        data = {

            "Datetime": [pd.Timestamp(year=int(timestr[0:4]), month=int(timestr[5:7]), day=int(timestr[8:10]), hour=int(timestr[11:13]),minute=int(timestr[14:16]),second=int(timestr[17:19]))],
            "Open": [0.042],
            "Close": [3.14],

        }
        dt=pd.DataFrame(data)
        return dt

d=getData("ADA-USD", '1d', "001h")
print(d)
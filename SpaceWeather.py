import datetime as dt, dateutil.relativedelta as du
import pytz, urllib2
from math import log10, floor
from calendar import monthrange

#________________________
#---- Params
_startWord = "data:"
_missingDataKey = 99999
_tzEu = pytz.timezone("Europe/Rome")
_tzUt = pytz.utc
_timeSlashFormat = "%Y/%m/%d %H:%M:%S"
_timeDashFormat = "%Y-%m-%d %H:%M:%S.%f"
_zeroTimeDiff = dt.timedelta(0)

#---- Loop over satellite and samples
#---- and generate the complete list of arguments
satellites = ["g13","g15"]
sample_keyword = {"_hepad_ap_":"_FLUX",
                  "_epead_p17ew_":"_COR_FLUX"}
_argList = [(sat,sam,key)
            for sat in satellites
            for sam,key in sample_keyword.iteritems()]

#________________________
def ConvertTime(x,isUTC=False,is_dst=None):
    #----
    if type(x) == str:
        try:
            x = dt.datetime.strptime(x.strip(),_timeSlashFormat)
        except ValueError:
            x = dt.datetime.strptime(x.strip(),_timeDashFormat)
    #----
    if isUTC:
        return _tzUt.localize(x,is_dst=is_dst).astimezone(_tzEu)
    else:
        return _tzEu.localize(x,is_dst=is_dst)

#________________________
#---- Calculate the division (x/y), with given precision, and convert to string
def Divide(x,y,sig=6):
    try:
        return str(round(float(x)/float(y), 
                         sig-int(floor(log10(x)))-1))
    except (ZeroDivisionError,ValueError):
        return "NaN"

#________________________
#---- Get the data for a given month, year, satellite and sample
def GetSpaceData(month,year,satellite,sample):
    #---- Reformat integers as strings
    lastDateInMonth = str(monthrange(year,month)[1]) #<--- Get the last date in the month
    month = str(month)
    year  = str(year)
    if len(month) == 1:
        month = "0"+month
    #---- Build the URL from string consts
    start  = "http://satdat.ngdc.noaa.gov/sem/goes/data/new_avg/"+year+"/"+month+"/"
    middle = "goes"+satellite[1:]+"/csv/"
    end    = satellite+sample+"5m_"+year+month+"01_"+year+month+lastDateInMonth+".csv"
    urlName = start+middle+end
    #---- Read the URL and extract the data
    print "\t\t--> Reading",urlName
    response = urllib2.urlopen(urlName)
    data     = response.read().split("\n")
    return data

#=====================
class SpaceData(dict):

    #_______________________
    def __init__(self,startTime,endTime):
        print "\nGetting flux data for time range",startTime,"-->",endTime
        self.startTime = ConvertTime(startTime,False)
        self.endTime   = ConvertTime(endTime,False)
        
        #---- Require less than one day between start and end times
        timeDiff  = self.endTime - self.startTime
        monthDiff = self.endTime.month - self.startTime.month
        if timeDiff <= _zeroTimeDiff:
            raise ValueError("The start time must occur before the end time")

        #---- Loop through dates
        while monthDiff >= 0 or timeDiff > _zeroTimeDiff:
            #---- Get the data
            self.ExtractData(self.startTime)
            #---- Increment
            self.startTime += du.relativedelta(months=+1)
            timeDiff  = self.endTime - self.startTime
            monthDiff = self.endTime.month - self.startTime.month

        #---- Sort the data, then format the header and data values
        sortedData = sorted(self.items())
        self.headerStr = ",".join([head for head,values in sortedData])
        self.dataStr   = ",".join([Divide(values[0],values[1]) for head,values in sortedData])

    #_______________________
    #----
    def ExtractData(self,daTime):        
        mn,yr = daTime.month,daTime.year
        print "\tExtracting data for month/year",mn,yr

        #----
        for sat,sam,keyword in _argList:
            #---- File outputs
            headerList = None
            foundStart = False
            #---- Loop over lines in data
            for line in GetSpaceData(mn,yr,sat,sam):
                #---- Skip the meta data
                if not foundStart:
                    if _startWord in line:
                        foundStart = True
                    continue

                #---- Remove "\r", then split by comma
                dataItems = line.replace('\r','').split(",")
                #---- The first line is the column names
                if not headerList:
                    headerList = dataItems
                    continue

                #---- Convert the raw datetime into the a time object
                rawDateTime = dataItems[0]
                theTime = ConvertTime(rawDateTime,True)
                #---- Check if the time is valid
                if theTime < self.startTime:
                    continue
                elif theTime > self.endTime:
                    continue

                #---- Add the data
                for i,header in enumerate(headerList):
                    #---- Only analyse headers containing the keyword
                    if not keyword in header:
                        continue
                    #---- Check if the data is missing
                    value = float(dataItems[i])
                    if abs(int(value)) == _missingDataKey:
                        continue
                    #---- Check if the column header has any data yet
                    if not header in self:
                        self[header] = [0.,0] #<--- Sum of values, num values
                    self[header][0] += value
                    self[header][1] += 1

#________________________
if __name__ == "__main__":
    #---- Input/output file names
    inName,outName  = "runTimes.csv","out.csv"
    with open(inName) as inFile, open(outName,"w") as outFile:
        #---- Loop over lines in input file
        for i,line in enumerate(inFile):
            startTime,endTime = line.strip("\n").split(",")
            #---- Get the data
            spaceData = SpaceData(startTime,endTime)
            #---- Write the output
            if i == 0:
                outFile.write(spaceData.headerStr+"\n")
            outFile.write(spaceData.dataStr+"\n")

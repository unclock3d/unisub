#!/usr/bin/env python

#Copyright (c) 2015 Dan Slov
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.


""" Module for parsing SubRip test files (.srt extension)  """
# imports section
# first add the directory to the search path
import os
import sys
import pinyin
import pprint
bindir = os.path.abspath(os.path.dirname(sys.argv[0]))
sys.path.append(bindir)
import re
# End of imports


##### CONSTANTS ######
class _CONST(object):
    FOO = 1234
    # pattern to match time of the sub line
    # Example: 00:00:03,748 --> 00:00:06,901
    timeFramePattern = "\t*(\d+:\d+:[\d,\,]+).*--\>.*(\d.*)"
    # pattern to match ordinal number of the subtitle
    currentSubNumberPattern = "^\d+$"
    subSeparator = "^\t*$"
    secondsInMinute = 60
    secondsInHour = 3600
    def __setattr__(self, *_):
        pass

CONST = _CONST()

class _SrtEntry(object):
    subNumber  = 0
    timeFrame = ""
    subText   = ""
    startTime = 0
    endTime = 1
    def __init__(self, subNumber = 0, timeFrame = "", subText = ""):
        self.subNumber = subNumber
        self.timeFrame = timeFrame
        self.subText = subText
    def extractTimeFromTimeFrame (self):
        if not self.timeFrame:
            self.startTime = 0
            self.endTime = 0
        else:
            match = re.match(CONST.timeFramePattern,self.timeFrame)
            # Example: 00:00:03,748 --> 00:00:06,901
            if (match):
                self.startTime = self._convertSrtFormatTime(match.group(1))
                self.endTime = self._convertSrtFormatTime(match.group(2))

    def _convertSrtFormatTime (self, srtTime):
        times = srtTime.split(':')
        if(len(times) == 3):
            #lastKey = match.group(1)
            mils = float(times[2].replace(',','.'))
            return mils + CONST.secondsInMinute*int(times[1]) + CONST.secondsInHour * int(times[0])
        else:
            # smth is wrong, TODO:: raise EXCEPTION
            # or maybe just do nothing
            return 0

    def toString (self):
        return self.subNumber + self.timeFrame + self.subText

class SrtObject(object):
    srtDB = {}
    filename = ""
    def __init__(self, **srtDB):
        #  init class members ######
        self.srtDB = srtDB
        self.filename = ""

    @classmethod
    def fromFilename(cls, filename):
        srtDB = cls()
        srtDB.buildSrtDB(filename)
        return srtDB

    def buildSrtDB(self,filename = ""):
        if not filename:
            filename = self.filename
        """ buildSrtDB takes .srt file name as an argument.
            The starting time of each entry is used as a dictionary key
            The value of the dictionary is the list (number, time, text)    
        """
        srtfile = open(filename,"r")
##### temp variables ######
        saveOn = False  # saveOn is True when a line containing time to show subs is matched
        # saveOn is False when empty line is matched
        lastKey = "NONE"
        subNumber = 0
#####  variables ######
        for line in srtfile: 
            #print(line)
            #line = line.rstrip()
            if(re.match(CONST.currentSubNumberPattern, line) and not saveOn): # means we start a new sub
                #subNumber = int(line)
                subNumber = line
            match = re.match(CONST.timeFramePattern,line)
            # Example: 00:00:03,748 --> 00:00:06,901
            if (match):
                srtEntry = _SrtEntry(subNumber, line)
                startTimes = match.group(1).split(':')
                if(len(startTimes) == 3):
                    saveOn = True
                    lastKey = match.group(1)
                    self.srtDB[lastKey] = srtEntry
                else:
                    # smth is wrong, TODO:: raise EXCEPTIONS
                    # or maybe just do nothing
                    continue
                #print(match.group(1))
            else:
                if (re.match(CONST.subSeparator, line)):
                    saveOn = False    #saveOn is false, move on to the next sub
                if (saveOn):
                    #assuming multiline sub
                    self.srtDB[lastKey].subText = self.srtDB[lastKey].subText + line 
        #pprint.pprint(self.srtDB)            
        srtfile.close()
# mergeSrtDB appends subs2 to subs11
    def mergeSrtDB(self, subs2):
        """ 
        mergeSrtDB assumes that both dictionaries contain exactly the same set of keys
        """
        subs_merged = {}
        for key1 in self.srtDB:
            if (subs2.srtDB[key1]):
                record1 = self.srtDB[key1]
                record2 = subs2.srtDB[key1]
                record = _SrtEntry (record1.subNumber, record1.timeFrame, record1.subText + record2.subText)
                subs_merged[key1] = record
        return SrtObject(**subs_merged)        

    def printSrt(self, filename):
        srtfile = open(filename,"w")
        for key in sorted(self.srtDB):
            srtfile.write(self.srtDB[key].toString())
            srtfile.write("\n")
        srtfile.close()

    def addPinyinToEnglishSrt(self):
        """ 
        addPinyinToEnglishSrt takes dictionary and returns new dictionary 
        containing hanzi and pinyin
        """
        subs_merged = {}
        for key in self.srtDB:
            record1 = self.srtDB[key]
            pin = pinyin.get(record1.subText)
            record = _SrtEntry(record1.subNumber, record1.timeFrame, record1.subText + pin)
            subs_merged[key] = record
        return SrtObject(**subs_merged)
class Date(object):
    day = 0
    month = 0
    year = 0

    def __init__(self, day=0, month=0, year=0):
        self.day = day
        self.month = month
        self.year = year
    @classmethod
    def from_string(cls, date_as_string):
        day, month, year = map(int, date_as_string.split('-'))
        date1 = cls(day, month, year)
        return date1

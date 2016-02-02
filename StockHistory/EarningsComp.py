from EarningsReleaseDates import EAHTMLParser
from termcolor import colored
from yahoo_finance import Share
import urllib2
import re
import datetime
import sys

def earningsReleasePatternFromZacks():
	''' we are to extract the dates from a line that looks like this:  
 	"1/26/2016", "12/2015", "$0.98", "$1.00", "<div class=\"right pos positive pos_icon showinline up\">0.02 (2.04%)</div>", "After Close" ]
    	This line can change, we can either keep changing the regex to try and keep up with the change, but there has to be a better way.
	'''
	date = "\"[\d]+\/[\d]+\/[\d]+\""
	whitespace = "\s+"
	date2 = "\"[\d]+\/[\d]+\""
	dol = "\"\-*\$[\d]+\.[\d]+\""
	null = "\"--\""
	dolnn = dol+ "|" + null
	junk = "\"\<div.*?div\>\""
	jnn = junk + "|" + null
	words = "\"[\w\s]+\""
	wnn = words + "|" + null
	temp = "("+ date+")," + whitespace + "(" + date2 + "),"+ whitespace + "(" + dolnn + ")," + whitespace + "(" + dolnn + ")," + whitespace + "(" + jnn + ")," + whitespace + "(" + wnn +")"
	return temp

def getConseqWorkDays(earnings_date):
	dt = earnings_date[0]
	dt2 = datetime.datetime.strptime(dt, "%m/%d/%Y")
	if earnings_date[1] == "Before Open":
		if dt2.weekday() == 0:		#monday
			dt2 = dt2 - datetime.timedelta(days=3)		#prev day is friday
		else:
			dt2 = dt2 - datetime.timedelta(days=1)
		dt1 = datetime.datetime.strftime(dt2,'%Y-%m-%d')
		dt2 = datetime.datetime.strptime(dt,'%m/%d/%Y').strftime('%Y-%m-%d' )
	else:		
		if dt2.weekday() == 4:		#friday
			dt2 = dt2 + datetime.timedelta(days=3)		#so next day is monday
		else:
			dt2 = dt2 + datetime.timedelta(days=1)		
		dt1 = datetime.datetime.strptime(dt,'%m/%d/%Y').strftime('%Y-%m-%d' )
		dt2 = datetime.datetime.strftime(dt2,'%Y-%m-%d')
	return (dt1, dt2)	

def processDateEarningsList(date_earningsList):
	dateList =  date_earningsList[0]
	earningsTime = date_earningsList[1]
	if "After Close" in earningsTime and "Before Open" in earningsTime:
		if "--" in earningsTime[1:]:	
			print "Data provided is not workable for all cases "	 
			return []		
	elif "After Close" in earningsTime:
		if "--" in earningsTime[1:]:	
			print "Some data missing, assuming After Close earnings for all available earnings announcement dates"
		earningsTime = ["After Close"] * len(earningsTime)
	elif "Before Open" in earningsTime:
		if "--" in earningsTime[1:]:	
			print "Some data missing, assuming Before Open earnings for all available earnings announcement dates"
		earningsTime = ["Before Open"] * len(earningsTime)
	return zip(dateList, earningsTime)	

def processEarningsBlobNew(blob):
	ptrn = earningsReleasePatternFromZacks()
	mat = re.findall(ptrn, blob)
	dateList = [i[0][1:-1] for i in mat]
	earningsTime = [i[5][1:-1] for i in mat]
	assert len(dateList) == len(earningsTime)
	return (dateList, earningsTime)

def processEarningsBlob(blob):
	pattern = "\"data\"\s*:(.*)"
	mat = re.search(pattern, blob)
	if not mat:
		return []
	blob =  mat.group(1)
	dateListPattern = "\"Date\"[\s]*:[\s]+\"([\d\/]*)\""
	earningsTimePattern = "\"Time\"[\s]*:[\s]+\"([\w\- ]*)\""
	dateList = re.findall(dateListPattern, blob)
	earningsTime = re.findall(earningsTimePattern, blob)
	assert len(dateList) == len(earningsTime)
	return (dateList, earningsTime)
	

def getStockPriceForDate(dateTuple, stock):
	dt1= dateTuple[0]	
	dt2= dateTuple[1]	
	if datetime.datetime.today() > datetime.datetime.strptime(dt1, "%Y-%m-%d"):
		return stock.get_historical(dt1, dt2)

'''
	TODO 1
	As of now we cull out the earnings release dates from Zacks and the stock prices from yahoo's finance api.
	The problem with this is:
	1.  Zacks can change their website so our regexes to cull out the dates will have to keep changing with them
	2.  This is not fast at all.  If you run the program you can see how slow it is.
	
	So, Ideally we should store our results on a database and refer to zacks and yahoo only if the data is missing
	and promptly fill up the db after the info has been retrieved.
	
	
'''
def printStockHist(stocksymbol):
	zacksurl = "http://www.zacks.com/stock/research/" + stocksymbol +"/earnings-announcements"
	stock = Share(stocksymbol)
	try:
		uf = urllib2.urlopen(zacksurl)
		eapage = uf.read()
	except:
		print "Exception received" , sys.exc_info()[0]
		print colored("Earnings release history unavailable for " + stocksymbol + " with Zacks at this time", 'red')
		return
	parser = EAHTMLParser()
	parser.feed(eapage)
	date_earningsList= processEarningsBlobNew(parser.earningsdatablob)
	if len(date_earningsList) == 0:
		print ("Earnings release history unavailable for " + stocksymbol + " with Zacks at this time", 'red')
		return	
	print "Retrieving earnings release dates from Zacks"
	date_earningsList = processDateEarningsList(date_earningsList) 
	dateList2 = [getConseqWorkDays(i) for i in date_earningsList if datetime.date.today()>datetime.datetime.strptime(i[0], "%m/%d/%Y").date() ]
	stockpriceList = [getStockPriceForDate(i, stock) for i in dateList2 if datetime.datetime.today()>datetime.datetime.strptime(i[0], "%Y-%m-%d")]
	print  "Retrieved " , len(stockpriceList) , "earnings release dates"
	if len(stockpriceList) == 0:
		print colored("Earnings release history unavailable for " + stocksymbol + " with Zacks at this time", 'red')
		return
	sums = 0
	for lst in stockpriceList:
		if len(lst) == 0:
			continue
		relDate = lst[-1]
		print "Earnings release on " , relDate['Date'] , ": closing price :", relDate['Close']
		prevClose = float(relDate['Close'])
		lst = lst[:-1]
		for dct in reversed(lst):
			dayopen = float(dct['Open'])
			dayclose = float(dct['Close'])
			if dayopen > prevClose:
				highcolor = 'green'
			else:
				highcolor = 'red'
			if dayclose > prevClose:
				lowcolor = 'green'
			else:
				lowcolor = 'red'

			print  dct['Date'] , ": day Open ", colored (dct['Open'] , highcolor), " day Close ", colored (dct['Close'] , lowcolor),
			absh = abs(prevClose - dayopen)
			absl = abs(prevClose - dayclose)
			maxs = max (absh, absl)/prevClose*100
			sums = sums +maxs
			print "Max swing is %", round(maxs, 2)
	if len(stockpriceList):
		print "Average swing % over ", len(stockpriceList), " earnings is ", round(sums/len(stockpriceList),2)

def main():	
	stocksymbol = raw_input("Enter stock symbol ")
	printStockHist(stocksymbol)

if __name__ == "__main__":
	main();

from termcolor import colored, cprint
import urllib2
from EarningsComp import printStockHist 
import re
from datetime import * 
import sys

def nextWeekDays(dt, days):
	dow = dt.weekday()
	i = 0
	out=[]
	while days:
		if (i+dow)%7 <5:
			out.append(i)
			days = days -1
		i = i+1
			
	return out

def getUpcomingWeekDays(days):
	td = date.today()
	return [td+timedelta(i) for i in nextWeekDays(td, days)]

def getEarnCalYahooUrl(day):
	urlPrefix = "http://biz.yahoo.com/research/earncal/"
	return urlPrefix+datetime.strftime(day,"%Y%m%d")+".html" 
	
	
def getCompaniesReleasingEarnings(day):
	url = getEarnCalYahooUrl(day)
	response = urllib2.urlopen(url)
	stocksymbolpattern = "http://finance.yahoo.com/q\?s=([\S]*)\""
	companynamepattern = "<td>(.*)</td><td><a href=" 
	earningtimepattern = "<small>([\w\s\d:]*)</small>"
	out = []
	time = []
	for line in response:
		mat1 = re.search(stocksymbolpattern, line)
		if (mat1):
			symbol = mat1.group(1)
			mat2 = re.search(companynamepattern, line)
			if (mat2):
				compname = mat2.group(1)
			else:
				print "company name not found in " + line + " pattern " + companynamepattern
				exit()
			out.append((compname, symbol))
		mat2 = re.search(earningtimepattern, line)
		if (mat2):
			time.append(mat2.group(1))
	return out

def main():
	days = input("Enter number of days from today for which earnings data is needed:")
	wdays = getUpcomingWeekDays(days)
	for days in wdays:
		cprint ("\nOn " +  datetime.strftime(days, "%d-%b-%y") , 'blue' ,attrs=['underline'])
 
		comps = getCompaniesReleasingEarnings(days)
		print "Earnings release scheduled for "	
		for i in comps:
			print "Company name: " + i[0] + "(" + i[1] + ")"

		for i in comps:
			print "\n" + i[0] + "("+ i[1] + ")" 
			try:
				printStockHist(i[1])
			except:
				print "Exception received for stock", i[1] , sys.exc_info()[0]
				print "Possibly a temporary error"

if __name__ == "__main__":
	main()

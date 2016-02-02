I am starting my journey into python with this first serious python program I am writing.   I use the data here to trade options sometimes.  When I was looking around, I saw Quandl has an api that gives you the earnings release dates for each company but it comes at a price, literally.  So I decided to parse the data from sites, besides fetching from Quandl wouldnt have been the learning experience this has been.

What does this program do?
	Given a number of days n(say), prints out the companies that are expected to announce earnings on the next n weekdays starting from today(this is fetched from biz.yahoo.com/research/earncal/).  For each company, fetches prior earnings release dates from zacks.com/stock/research/<stocksymbol>/earnings-announcements.  For each earning date of a company, fetches stock price for the prior date and the same on the earnings day and prints out the change in stock price.  So in short, the effect of the earnings release on the stock price.
	EarningsCalender.py:  	takes in the number of days into which we need the data
	EarningsComp.py:	takes a the stock symbol and prints out prior earnings release dates and the data described above.

Moving this further:
1. 	As I note in one of the comments, I should ideally store all this data in a database and not fetch this everytime.  Fetching/parsing everytime is just wasteful and even there are there smarter ways to parse and cull out data.  Currently reading up books on python that is supposed to help me with this kind of stuff.
2.	Given a stock whose average swing is a certain value, purchase straddle options before earnings and see where it goes(ofcourse am talking about paper trades here, but if you want to put in your money feel free :) )


from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint
import urllib
import re

class EAHTMLParser(HTMLParser):
	#def handle_comment(self, data):
	#	print "Comment :", data
	#	pos = self.getpos()
	#	print "line ", pos[0], "position ", pos[1]
	def __init__(self):
	        HTMLParser.__init__(self)
		self.earningsdatablob = ""
		
	def handle_data(self, data):
		match = re.search("\"earnings_announcements_earnings_table\"(\s)*:", data)
		if match:
			self.earningsdatablob = data
	
def main():
	uf = urllib.urlopen('http://www.zacks.com/stock/research/VMW/earnings-announcements')
	eapage = uf.read()
	parser = EAHTMLParser()
	parser.feed(eapage)
	print parser.earningsdatablob
	
    
if __name__ == "__main__":
	main();

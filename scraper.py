#!/usr/bin/python

from urllib2 import urlopen
from bs4 import BeautifulSoup
import re

class Scraper:
    
    def __init__(self, webpage):
        self.webpage = urlopen(webpage).read() #Open the page and parse the HTML
    
    def scrape(self):
        soup = BeautifulSoup(self.webpage, 'lxml') #Pass the page to the BeautifulSoup module
        
        linkPattern = re.compile('<link rel.*href="(.*)" />') #I used regex here because of the strange format of where the page's links were stored
        
        findTitles = soup.find_all('title') #Find all of the titles and put them in a list
        findLinkPattern = re.findall(linkPattern, self.webpage) #Find all of the links and put them in a list
        
        self.titles = [] #Create lists for each that will be accessed by the main program
        self.links = []
        self.bodies = []
        
        for i in range(1, 16):
            self.titles.append(str(findTitles[i].get_text())) #Add all of the titles to the titles list
            self.links.append(str(findLinkPattern[i])) #Add all of the links to the links list
            articlePage = urlopen(findLinkPattern[i]).read() #Open each link and parse it
            findBody = BeautifulSoup(articlePage, 'lxml') #Pass it to BeautifulSoup
            
            x = 1
            q = findBody.find_all('p')[x].get_text()
            
            while q == '': #If the second paragraph has no text, check the next paragraph
                    q = findBody.find_all('p')[x+1].get_text()
            while not q.find('\n'): #If the paragraph is just newlines, check the next paragraph
                q = findBody.find_all('p')[x+1].get_text()
                
                
            self.bodies.append(str(q)) #Add all the paragraphs to the bodies list
            
 

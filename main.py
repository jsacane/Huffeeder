#!/usr/bin/python

#Change Log:
#v1.1 - (9/2/13) Added refresh functionality, Added exception handler for inability to connect to HuffPost servers
#v1.0 - (8/26/13) First release


#---------------------------------------#
# To add:                               #
# -Fix loading gauges w/ threading      #
# -Back button/forward button to        #
#  navigate previous articles           #
# -Handling of missing article previews #
# -Eventual support for other feeds     #
#---------------------------------------#

import wx
import wx.html2
import scraper #A module I wrote that scrapes article info from the HuffPost RSS feed
import threading #Eventually to be used for loading gauges
import urllib2


class MainFrame(wx.Frame): #The main frame that will display everything
    
    def __init__(self, *args, **kwargs):
        super(MainFrame, self).__init__(*args, **kwargs)
        
        self.webpage = scraper.Scraper('http://feeds.huffingtonpost.com/huffingtonpost/LatestNews')
        self.webpage.scrape() #Scrape the feed for titles, links, and paragraphs
        
        self.InitUI()
        self.Centre()
        self.Show()
        
    def InitUI(self):
        
        #-----------------------Menus---------------------------------
        
        menubar = wx.MenuBar()
        filemenu = wx.Menu()
        
        fileQuit = filemenu.Append(wx.ID_EXIT, '&Quit\tCtrl+Q')
        fileAbout = filemenu.Append(wx.ID_ABOUT, '&About\tCtrl+A', 'Information about this program')
        fileRefresh = filemenu.Append(wx.ID_ANY, '&Refresh\tCtrl+R', 'Refresh the feed')
        
        menubar.Append(filemenu, '&File')
        self.SetMenuBar(menubar)
        
        self.statusBar = self.CreateStatusBar()
        
        toolBar = self.CreateToolBar()
        refreshTool = toolBar.AddLabelTool(wx.ID_ANY, 'Refresh', wx.Bitmap('reload.png'))
        toolBar.Realize()
        
        #-----------------------Panels--------------------------------
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        vbox = wx.BoxSizer(wx.VERTICAL)
        htmlBox = wx.BoxSizer(wx.VERTICAL)
        
        listPanel = wx.Panel(self, -1, style=wx.SUNKEN_BORDER)
        htmlPanel = wx.Panel(self, -1,style=wx.SUNKEN_BORDER)
        
        #-----------------------Layout--------------------------------
        
        listPanel.SetBackgroundColour('WHITE')
        
        self.listCtrl = wx.ListCtrl(listPanel, -1, style=wx.LC_REPORT)
        self.listCtrl.InsertColumn(0, 'Article Title')
        self.listCtrl.SetColumnWidth(0, 500)
        
        for i in range(0, 15):
            self.listCtrl.InsertStringItem(i, self.webpage.titles[i])
            
        self.multiLine = wx.TextCtrl(listPanel, -1, style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.multiLine.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.SUNKEN_BORDER))
        
        vbox.Add(self.listCtrl, 1, wx.EXPAND)
        vbox.Add(self.multiLine, 1, wx.EXPAND)
        listPanel.SetSizer(vbox)
        
        self.browser = wx.html2.WebView.New(htmlPanel)
        self.browser.LoadURL(self.webpage.links[0])
        htmlBox.Add(self.browser, 1, wx.EXPAND)
        htmlPanel.SetSizer(htmlBox)
        
        hbox.Add(listPanel, 1, wx.EXPAND|wx.ALL)
        hbox.Add(htmlPanel, 2, wx.EXPAND)
        
        self.SetAutoLayout(True)
        self.SetSizer(hbox)
        self.Layout()
        
        #-----------------------Events--------------------------------
        
        self.Bind(wx.EVT_MENU, self.OnQuit, fileQuit)
        self.Bind(wx.EVT_MENU, self.OnAbout, fileAbout)
        self.Bind(wx.EVT_MENU, self.OnRefresh, fileRefresh)
        
        self.Bind(wx.EVT_TOOL, self.OnRefresh, refreshTool)
        
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelect)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnActivate)
        
        #-------------------------------------------------------------
        
    def OnQuit(self, e):
        self.Close()
        
    def OnAbout(self, e):
        dlg = wx.MessageDialog(self, 
"""Huffeeder v1.1 is an RSS feed aggregator client for the Huffington Post RSS syndicate. 
It was written by Jack Sacane in Python 2.7 and last updated 9/2/13.""", 'About Huffeeder', wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
        
    def OnRefresh(self, e): #Reloads the scraper module and mimics previous processes, replaces the old articles in the list with the new articles
        gauge = LoadingGauge(None, title='', size=(300,200)) #Create an instance of the loading screen
        threading.Thread(target=gauge.InitUI).start() #Show the loading screen while the main program is refreshing (But it doesn't...)
        reload(scraper)
        self.webpage = scraper.Scraper('http://feeds.huffingtonpost.com/huffingtonpost/LatestNews')
        self.statusBar.SetStatusText('Refreshing feed...')
        self.webpage.scrape()
        self.statusBar.SetStatusText('')
        self.listCtrl.DeleteAllItems()
        for i in range(0, 15):
            self.listCtrl.InsertStringItem(i, self.webpage.titles[i])
        self.browser.LoadURL(self.webpage.links[0])
        self.Layout()
    
    def OnSelect(self, e): #When the list item is selected, display its title, link, and body information in the TextCtrl (Note: Sometimes an article body may have no relevant text or no text at all. Going to fix this soon!)
        self.statusBar.SetStatusText('Double click to load article')
        self.list_index = self.listCtrl.GetFirstSelected()
        self.multiLine.ChangeValue(self.webpage.titles[self.list_index] + '\n\n' + 
                                   self.webpage.links[self.list_index] + '\n\n' + self.webpage.bodies[self.list_index])
    
    def OnActivate(self, e): #When the list item is activated, load its link in the web view
        self.browser.LoadURL(self.webpage.links[self.list_index])


        
class LoadingGauge(wx.Dialog): #The loading screen
    def __init__(self, *args, **kwargs):
        super(LoadingGauge, self).__init__(*args, **kwargs)
        
        self.InitUI()
        self.Centre()
        self.Show()
        
    def InitUI(self):
            
        self.timer = wx.Timer(self, 1)
        self.count = 0
            
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
            
        self.gauge = wx.Gauge(panel, range=50, pos=(22,60), size=(250,25))
        self.text = wx.StaticText(panel, -1, 'Loading feed...', pos=(100,30))
            
        self.timer.Start(100)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
            
    def OnTimer(self, e):
            
        self.count += 1
        self.gauge.SetValue(self.count)
            
        if self.count == 50: #Just a five second load until I can figure out how to load in real time
            self.timer.Stop()
            self.Destroy()        

def main():
    
    try:
        urllib2.urlopen('http://feeds.huffingtonpost.com/huffingtonpost/LatestNews', timeout=5) #Check to see if user can connect to the HuffPost feed server
    except urllib2.URLError:
        print 'Unable to connect to server. Check internet connection.' #If not, stop the program
        return
    
    app = wx.App()
    frame = MainFrame(None, title='Huffeeder', size=(1280,715))
    app.MainLoop()
    
if __name__ == '__main__':
    main()

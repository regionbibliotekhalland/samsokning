#!/usr/local/bin/python

# -*- coding: utf-8 -*-

class HTMLwriter:
    'A class to handle output of HTML'
    
    def startBasicPage(self):
        print "Content-type: text/html"
        print
        print "<HTML>"
        print "<HEAD>"
        print "<TITLE>" + "Sams&ouml;kning i Halland" + "</TITLE>"
        print "</BODY>"
    
    def closeBasicPage(self):
        print "</BODY>"
        print "</HTML>"
        
    def outputSearchbox(self):
        print '<form name="input" action="samsok-hall2.py" method="get">'
        print '<input type="text" name="search">'
        print '<input type="submit" value="S&ouml;k">'
        print '</form>'

    def outputResultsnumbers(self,numbers, location):
        #print "Inside outputResultnumbers"
        #print "Numbers innehaller:" #+ numbers
        import cgi

        form = cgi.FieldStorage()
        if "search" in form:
            #print '"Search" was in form - if statement filled'
            print "Din s&ouml;kning p&aring; " + form['search'].value + " gav " + numbers + " tr&auml;ffar i" + location + "<br>\n"
            
    def output2dList(self, storage):
        
        print "<table>"
        for row in storage:
            print "<tr>"
            for field in row: 
                print "<td>"
                print field
                print "</td>"
            print "</tr>"
        print "</table>"
        #print "<ol>"
        #for row in storage:
        #    print "<li>"
        #    for field in row: 
        #        print field 
        #    print "</li>"               
        #print "</ol>"

class connectorclass: 
    'Knows how to fetch the different library opacs'
    
    def __init__(self):
        import urllib
        
    def getpage(self, url):
        import urllib
        page = urllib.urlopen(url)
        content = page.read()
        page.close()     
        return content
        
class opacParser:
    'Knows how to parse the different library opacs'
    
    def parseLibra(self,content,location,storage,baseurl):
        # Extract the relevant metadata using some string magic
        
        #First get the total number of hits through slicing the code
        hitnumbers = content[content.find("<b>Resultat"):]
        hitnumbers = hitnumbers[:hitnumbers.find("</b>")]
        hitnumbers = hitnumbers[hitnumbers.find("av")+3:]
        #hitnumbers = hitnumbers.strip()
        #hitnumbers = int(hitnumbers)
        #print "Hitnumbers eftr slicing inuti parseLibra" + hitnumbers
        
        #Second - take apart the results list and put the parts into the storage
        
        # Slicing away the html surrounding the list with the info we want
        hitlist = content[content.find('<table class="list"'):]
        hitlist = hitlist[:hitlist.find('</table>')]
        
        #print "Closing in on the parsing of the hitlist<br>\n"
        line = hitlist
        # Strip the first row with headers
        hitlist = hitlist[hitlist.find('</tr>')+5:]
        hitlist = hitlist.replace('<td >','<td>')
        # The loop to parse the full table with info 
        while len(hitlist) > 0:
            #print "Inside the while loop for parsing the hitlist!<br>\n"
            temprow = [location]
            #print temprow
            thisrow = hitlist[:hitlist.find('</tr>')+5]
            #print thisrow
            thiscell = thisrow
            for i in range(0,4,1): 
                #print "Inside for loop<br>\n"
                cellvalue = thiscell[thiscell.find('<td>')+4:thiscell.find('</td>')]
                #print "Denna cell:" + cellvalue + "<br>\n"
                thiscell = thiscell[thiscell.find('</td>')+5:]
                temprow.append(cellvalue)
            #print "Outside the for loop now"
            storage.append(temprow)
            #print "Appeding temprow to storage was ok"
            hitlist = hitlist[hitlist.find('</tr>')+5:]
        #print storage
        
        # Cleaning up the contents a bit and removing remaining html
        for row in storage:
            # Stripping away relative links and changing from icons to text representations. 
            #mediatype = row.pop(5)
            #mediatype = mediatype[mediatype.find('alt="')+5:]
            #mediatype = mediatype[:mediatype.find('"')]
            #row.insert(4,mediatype)
            #print row[2]
            
            # Making the relative URLs from the source point at the right source. 
            urlfield = row.pop(2)
            urlfield = urlfield.replace('href="','href='+baseurl)
            row.insert(2,urlfield)
         
        
        #print hitlist
        return storage, hitnumbers
        
class metadatastorage:

    def __init__(self): 
        metalist = []
        
class metadataSortmachine: 
    
    def groupByTitle(self,list):
        for row in list: 
            title = row.pop(2)
            row.insert(0,title)
        list.sort()
        return list  
            
        
import cgi        
HTMLmachine = HTMLwriter()
HTMLmachine.startBasicPage()
HTMLmachine.outputSearchbox()
storage = [] # metadatastorage()
connector = connectorclass()
form = cgi.FieldStorage()

#totalhits = 0
if "search" in form:
    # Searching Laholm
    page = connector.getpage('http://laholmopac.kultur.halmstad.se/opac/search_result.aspx?TextFritext=' + form['search'].value) 
    parser = opacParser()
    storage, hitnumbers = parser.parseLibra(page,"laholm", storage,'http://laholmopac.kultur.halmstad.se/opac/')
    #print "Calculating number of total hits" 
    #totalhits = totalhits + hitnumbers
    print "<h1>Resultat</h1>"
    HTMLmachine.outputResultsnumbers(hitnumbers,"Laholm")
    
    # Searching Halmstad
    page = connector.getpage('http://halmstadopac.kultur.halmstad.se/opac/search_result.aspx?TextFritext=' + form['search'].value) 
    storage, hitnumbers = parser.parseLibra(page,"Halmstad", storage,'http://halmstadopac.kultur.halmstad.se/opac/')
    #print "Calculating number of total hits" 
    #totalhits = totalhits + hitnumbers
    HTMLmachine.outputResultsnumbers(hitnumbers,"Halmstad")
    
    # Searching Varberg
    page = connector.getpage('http://bib.varberg.se/opac/search_result.aspx?TextFritext=' + form['search'].value) 
    storage, hitnumbers = parser.parseLibra(page,"Varberg", storage,'http://bib.varberg.se/opac/')
    #print "Calculating number of total hits" 
    #totalhits = totalhits + hitnumbers
    HTMLmachine.outputResultsnumbers(hitnumbers,"Varberg")
    
    sorter = metadataSortmachine()
    storage = sorter.groupByTitle(storage)
    HTMLmachine.output2dList(storage)

HTMLmachine.closeBasicPage()

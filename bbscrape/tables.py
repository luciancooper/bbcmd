import sys,re
import urllib.request
from contextlib import closing
from html.parser import HTMLParser

class TableParser(HTMLParser):
    #Initializing lists
    def __init__(self,report_warnings=True):
        super().__init__()
        self.stack = []
        self.attrs = []
        self.cache = []
        self.parsing = []
        self.tables = {}
        self.report_warnings = report_warnings

    def __iter__(self):
        return iter(self.tables.items())

    def __getitem__(self,key):
        return self.tables[key]

    # Override feed to return self
    def feed(self, data):
        super().feed(data)
        return self

    # Check if tag should initiate parsing capture
    def should_parse(self,tag,attrs):
        return (tag == 'table') and ('id' in dict(attrs))

    # Handle start tag event
    def handle_starttag(self, tag, attrs):
        parsing = self.should_parse(tag,attrs)
        self.stack.append(tag)
        self.attrs.append(attrs)
        self.parsing.append(parsing)
        if any(self.parsing):
            self.cache.append('')

    # Handle end tag event
    def handle_endtag(self, tag):
        for i in reversed(range(len(self.stack))):
            if self.stack[i]==tag:
                break
        else:
            if self.report_warnings == True:
                print(f"Table Parse Warning: {tag} Tags Imbalanced",file=sys.stderr)
            return
        self.stack = self.stack[:i]
        if any(self.parsing[:i+1]):
            attrs = ''.join(' %s="%s"'%(k,v.replace('"',"'")) for k,v in self.attrs[i])
            j = i - self.parsing.index(True)
            ele = f"<{tag}{attrs}>{self.cache[j]}</{tag}>"
            if j == 0:
                try:
                    id = dict(self.attrs[i])['id']
                    self.tables[id] = ele
                except KeyError as e:
                    if self.report_warnings == True:
                        print(f"Warning: Table does not have ID and was not recorded",file=sys.stderr)
            else:
                self.cache[j-1] += ele
            self.cache = self.cache[:j]
        self.parsing = self.parsing[:i]
        self.attrs = self.attrs[:i]



    # -------- Tag Content -------- #

    # Handle tag contents
    def handle_data(self,data):
        text = data.strip()
        if len(text) == 0:return
        #tag = self.stack[-1]
        if any(self.parsing):
            self.cache[-1]+=text


    def handle_startendtag(self,startendTag, attrs):
        pass

    # Handle comments, in baseball reference files, comments may contain hidden tables
    def handle_comment(self,data):
        for k,t in self.__class__(self.report_warnings).feed(data):
            self.tables[k] = t

    def feed_url(self,url):
        with closing(urllib.request.urlopen(url)) as response:
            page = response.read().decode('utf-8')
        return self.feed(page)

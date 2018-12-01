import requests
import urllib.request
import sys
import re
from contextlib import closing
from html.parser import HTMLParser


class BBRTableParser(HTMLParser):
    #Initializing lists
    def __init__(self):
        super().__init__()
        self.stack = []
        self.attrs = []
        self.cache = []
        self.parsing = []
        self.tables = {}

    def __iter__(self):
        return iter(self.tables.items())

    @property
    def _indent_(self):
        n = len(self.parsing) - self.parsing.index(True) - 1
        return '\t'*n

    # Override feed to return self
    def feed(self, data):
        super().feed(data)
        return self

    # -------- Start Tag -------- #

    # Check if tag should initiate parsing capture
    def should_parse(self,tag,attrs):
        return tag == 'table'

    # Handle start tag event
    def handle_starttag(self, tag, attrs):
        parsing = self.should_parse(tag,attrs)
        self.stack.append(tag)
        self.attrs.append(attrs)
        self.parsing.append(parsing)
        if any(self.parsing):
            self.cache.append('')
            #print(f"{self._indent_}<{tag}>",file=sys.stderr)

    # -------- End Tag -------- #

    # Handle end tag event
    def handle_endtag(self, tag):
        for i in reversed(range(len(self.stack))):
            if self.stack[i]==tag:
                break
        else:
            print(f"Warning HTML End Tag Imbalance: {tag}",file=sys.stderr)
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
                    print(f"Warning: Baseball Reference table does not have ID and was not recorded")
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
        for k,t in self.__class__().feed(data):
            self.tables[k] = t

    def feed_url(self,url):
        with closing(urllib.request.urlopen(url)) as response:
            page = response.read().decode('utf-8')
        return self.feed(page)



def build_webpage(fn):
    def wrapper(*args):
        print("""<html>
        <head>
        <link rel="stylesheet" href="bbr.css">
        </head>
        <body>""")
        fn(*args)
        print("""</body>
        </html>""")
    return wrapper


@build_webpage
def run_url(url):
    for k,t in BBRTableParser().feed_url(url):
        print(f"<h1>{k}</h1>")
        print(t)

@build_webpage
def run_text(text):
    for k,t in BBRTableParser().feed(text):
        print(f"<h1>{k}</h1>")
        print(t)


def main():
    sample = """<main>
        <div>
            <table class="sortable stats_table now_sortable" id="player_value_batting" data-cols-to-freeze="1">
                <tr><td>T1[0,0]</td><td>T1[0,1]</td><td>T1[0,2]</td></tr>
                <tr><td>T1[1,0]</td><td>T1[1,1]</td><td>T1[1,2]</td></tr>
                <tr><td>T1[2,0]</td><td>T1[2,1]</td><td>T1[2,2]</td></tr>
            </table>
        </div>
        <div>
            <table>
                <tr><td>T2[0,0]</td><td>T2[0,1]</td><td>T2[0,2]</td></tr>
                <tr><td>T2[1,0]</td><td>T2[1,1]</td><td>T2[1,2]</td></tr>
                <tr><td>T2[2,0]</td><td>T2[2,1]</td><td>T2[2,2]</td></tr>
            </table>
        </div>
    </main>"""
    #run_text(sample)
    run_url("https://www.baseball-reference.com/teams/ARI/2015.shtml")


if __name__ == '__main__':
    main()

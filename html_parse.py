import requests
import urllib.request
import sys
import re
from contextlib import closing
from htmlparser.parser import HTMLParser

class MyHTMLParser(HTMLParser):
    #Initializing lists
    def __init__(self):
        super().__init__()
        self.stack = []
        self.parsing = []

    @property
    def _indent_(self):
        n = len(self.parsing) - self.parsing.index(True) - 1
        return '\t'*n


    # -------- Start Tag -------- #

    def should_parse(self,tag):
        #return True
        return tag == 'table'

    def handle_starttag(self, tag, attrs):
        parsing = self.should_parse(tag)
        #parsing = True
        self.stack.append(tag)
        self.parsing.append(parsing)
        if any(self.parsing):
            print(f"{self._indent_}<{tag}>")

    # -------- End Tag -------- #

    def handle_endtag(self, tag):
        if not tag in self.stack:
            print(f"Warning HTML End Tag Imbalance: {tag}",file=sys.stderr)
            return
        while len(self.stack)>0:
            if tag == self.stack.pop():
                break
            self.parsing.pop()
        else:
            raise Exception(f"Impossible HTML End Tag Imbalance: {tag}")
        if any(self.parsing):
            print(f"{self._indent_}</{tag}>")
        self.parsing.pop()


    # -------- Tag Content -------- #

    def handle_data(self,data):
        text = data.strip()
        if len(text) == 0:return
        #tag = self.stack[-1]
        if any(self.parsing):
            print(f"{self._indent_}{text}")


    def handle_startendtag(self,startendTag, attrs):
        pass

    def handle_comment(self,data):
        self.__class__().feed(data)


def get_file(url):
    with closing(urllib.request.urlopen(url)) as response:
        return response.read().decode('utf-8')

def get_file_chunks(url):
    try:
        with closing(requests.get(url, stream=True)) as r:
            for chunk in r.iter_content(chunk_size=1024):
                yield chunk.decode('utf-8')
    except requests.exceptions.RequestException as e:
        print('Error during requests to {0} : {1}'.format(url, str(e)))


def remove_comments(text):
    return re.sub(r'--\s*>','',re.sub(r'<!--','',text))


def main():
    parser = MyHTMLParser()
    #parser.feed('  div#fs_fs_footer   ')

    #creating an object of the overridden class
    #parser = MyHTMLParser()

    #url = "https://www.nytimes.com/"
    url = "https://www.baseball-reference.com/teams/ARI/2015.shtml"
    #for chunk in  get_file_chunks(url): parser.feed(chunk)
    webpage = get_file(url)
    #webpage = remove_comments(webpage)
    parser.feed(webpage)


    #parser.feed(urllib.request.urlopen(url).read().decode('utf-8'))

    #print(“Comments”, parser.lsComments)


    #url = "https://www.baseball-reference.com/teams/ARI/2015.shtml"
    #for chunk in  get_file_chunks(url):
    #    if 'id="players_value_batting"' in chunk:
    #        print('FOUND ID')
        #parser.feed(chunk)

    #


if __name__ == '__main__':
    main()

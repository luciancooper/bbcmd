import sys,re
from bbscrape.tables import TableParser

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
    for k,t in TableParser().feed_url(url):
        print(f"<h1>{k}</h1>")
        print(t)

@build_webpage
def run_text(text):
    for k,t in TableParser().feed(text):
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
    #run_url("https://www.fangraphs.com/statss.aspx?playerid=1000001&position=OF")
    run_url("https://www.spotrac.com/mlb/chicago-cubs/payroll/2016/")
    #run_url("https://www.fangraphs.com/statss.aspx?playerid=11579&position=OF")
    #run_url("https://www.baseball-reference.com/leagues/MLB/2018.shtml")


if __name__ == '__main__':
    main()

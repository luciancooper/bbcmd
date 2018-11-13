

def writeXML(years):
    year_xml = "\t<season year='{0:}'>\n\t\t<context>/Users/luciancooper/BBSRC/SIM/ctx/{0:}.txt</context>\n\t\t<events>/Users/luciancooper/BBSRC/SIM/eve/{0:}.txt</events>\n\t\t<games>/Users/luciancooper/BBSRC/SIM/gid/{0:}.txt</games>\n\t\t<rosters>/Users/luciancooper/BBSRC/SIM/ros/{0:}.txt</rosters>\n\t\t<teams>/Users/luciancooper/BBSRC/SIM/team/{0:}.txt</teams>\n\t</season>"
    with open('bbdata.xml','w') as f:
        print('<?xml version="1.0"?>',file=f)
        print('<bbdata>',file=f)
        for y in years:
            print(year_xml.format(y),file=f)
        print('</bbdata>',file=f)

#!/usr/bin/env python
import sys,os,requests,itertools
from contextlib import closing
from cmdtools import parse_years,verify_dir
import cmdtools.progress as progress

### download environment

def download_file(path,ftype,year,bar):
    url = f"https://raw.githubusercontent.com/luciancooper/bbsrc/master/files/{ftype}/{year}.txt"
    file = os.path.join(path,ftype,f'{year}.txt')
    try:
        with closing(requests.get(url, stream=True)) as r,open(file,'wb') as f:
            total_size = int(r.headers['content-length'])
            loops = total_size // 1024 + int(total_size % 1024 > 0)
            for chunk in bar.init(loops,f'{ftype} {year}').iter(r.iter_content(chunk_size=1024)):
                f.write(chunk)
    except requests.exceptions.RequestException as e:
        print('Error during requests to {0} : {1}'.format(url, str(e)))


def download_env(years,path):
    ftypes = ['ctx','eve','gid','ros','team']
    srcdir = os.path.join(path,'bbsrc')
    for ftype in ftypes:
        verify_dir(os.path.join(srcdir,ftype))
    bar = progress.MultiBar(2,len(years)*len(ftypes),'Downloading')
    for year,ftype in itertools.product(years,ftypes):
        download_file(srcdir,ftype,year,bar)


### WRITE XML

def bbdataXML(srcdir,years):
    season_xml = [
        '<context>{0:}/ctx/{1:}.txt</context>',
        '<events>{0:}/eve/{1:}.txt</events>',
        '<games>{0:}/gid/{1:}.txt</games>',
        '<rosters>{0:}/ros/{1:}.txt</rosters>',
        '<teams>{0:}/team/{1:}.txt</teams>',
    ]
    xml = '<?xml version="1.0"?>\n<bbdata>\n%s</bbdata>\n'%''.join("\t<season year='{0:}'>\n{1:}\t</season>\n".format(year,''.join(f'\t\t{x}\n' for x in season_xml).format(srcdir,year)) for year in years)
    return xml

# main

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Baseball Source Data Tool")
    parser.add_argument('years',type=parse_years,help='Target MLB seasons')
    parser.add_argument('outdir',nargs='?',default=os.getcwd(),help='Target MLB seasons')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--env',action='store_true',help='Download Compile Raw files')
    group.add_argument('--xml',action='store_true',help='Create XML Directory Lookup File')
    args = parser.parse_args()
    #print(args)
    if args.xml == True:
        srcdir = os.path.join(os.getcwd(),'bbsrc')
        verify_dir(args.outdir)
        with open(os.path.join(args.outdir,'bbdata.xml'),'w') as f:
            f.write(bbdataXML(srcdir,args.years))

    elif args.env == True:
        download_env(args.years,args.outdir)

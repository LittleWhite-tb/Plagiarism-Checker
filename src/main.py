# -*- coding: utf-8 -*-
# Master script for the plagiarism-checker
# Coded by: Shashank S Rao

#import other modules
from cosineSim import *
from htmlstrip import *

from scholarly import scholarly
from scholarly import ProxyGenerator
from fp.fp import FreeProxy
from bs4 import BeautifulSoup

#import required modules
import argparse
import codecs
import json as simplejson
import traceback
import sys
import random
import time
import operator
import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse

# Given a text string, remove all non-alphanumeric
# characters (using Unicode definition of alphanumeric).
def getQueries(text,n):
    import re
    sentenceEnders = re.compile('[.!?]')
    sentenceList = sentenceEnders.split(text)
    sentencesplits = []
    for sentence in sentenceList:
        x = re.compile(r'\W+', re.UNICODE).split(sentence)
        x = [ele for ele in x if ele != '']
        sentencesplits.append(x)
    finalq = []
    for sentence in sentencesplits:
        l = len(sentence)
        l=l/n
        index = 0
        for i in range(0,int(l)):
            finalq.append(sentence[index:index+n])
            index = index + n-1
        if index !=len(sentence):
            finalq.append(sentence[len(sentence)-index:len(sentence)])
    return finalq

# Search the web for the plagiarised text
# Calculate the cosineSimilarity of the given query vs matched content on google
# This is returned as 2 dictionaries
def searchWeb(text,output,c):
    try:
        text = text.encode('utf-8')
    except:
        text = text
    query = urllib.parse.quote_plus(text)
    if len(query)>60:
        return output,c
    #using googleapis for searching web
    base_url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q='
    url = base_url + '%22' + query + '%22'
    request = urllib.request.Request(url,None,{'Referer':'Google Chrome'})
    response = urllib.request.urlopen(request)
    results = simplejson.load(response)
    try:
        if ( len(results) and 'responseData' in results and 'results' in results['responseData'] and results['responseData']['results'] != []):
            for ele in	results['responseData']['results']:
                Match = results['responseData']['results'][0]
                content = Match['content']
                if Match['url'] in output:
                    #print text
                    #print strip_tags(content)
                    output[Match['url']] = output[Match['url']] + 1
                    c[Match['url']] = (c[Match['url']]*(output[Match['url']] - 1) + cosineSim(text,strip_tags(content)))/(output[Match['url']])
                else:
                    output[Match['url']] = 1
                    c[Match['url']] = cosineSim(text,strip_tags(content))
    except:
        return output,c
    return output,c

def searchScholar(text, output, c):
    if not text:
        return output,c
    print(text)

    search_res_limit = 6
    res_it = scholarly.search_pubs('"' + text + '"')
    try:
        for it in res_it:
            if search_res_limit == 0:
                break
            search_res_limit -= 1

            art_title = it['bib']['title']
            art_link = it['pub_url']
            if art_link in output:
                output[art_link] = output[art_link] + 1
                c[art_link] = (output[art_link], c[art_link][1] + [("", text)])
            else:
                output[art_link] = 1
                c[art_link] = (1, [("", text)])
    except:
        return output,c
    return output,c


def searchBing(text, output, c):
    time.sleep(random.uniform(1.2,2.5))

    try:
        text = text.encode('utf-8')
    except:
        text = text

    query = urllib.parse.quote_plus(text)

    base_url = 'https://www.bing.com/search?q='
    url = base_url + '"' + query + '"'
    request = urllib.request.Request(url,None,{'Referer':'Google Chrome'})
    response = urllib.request.urlopen(request)

    soup = BeautifulSoup(response.read(), 'html.parser')
    search_res = soup.find_all(class_="b_algo")

    search_res_limit = 4
    for res in search_res:
        if search_res_limit == 0:
            break
        search_res_limit -= 1

        art_title = ""
        art_link = ""
        art_brief = ""
        links = res.find_all('a')
        for link in links:
            art_link = link.get('href')
            art_title = link.text

        contents = res.find_all('p')
        for content  in contents:
            art_brief = content.text

        score = cosineSim(text.decode('utf-8'), art_brief)
        if art_link in output:
            output[art_link] = output[art_link] + 1

            revised_score = (c[art_title]*(output[art_link] - 1) + score)/(output[art_link])
            c[art_link] = (revised_score, c[art_link][1] + [(art_brief, text)])
        else:
            output[art_title] = 1
            c[art_link] = (score, [(art_brief, text)])

    return output,c


# Use the main function to scrutinize a file for
# plagiarism
def main():
    arg_parser = argparse.ArgumentParser(description="Scan a text document for plagiarism.")
    arg_parser.add_argument('--use_proxy', action='store_true', dest = 'use_proxy', default=False, help='Use an automatically found proxy')
    arg_parser.add_argument('-s', '--start', type=int, dest='seg_start', default=0, help='Start the scan from a specific segment (allows to resume a scan)')
    arg_parser.add_argument('-l', '--limit', type=int, dest='limit', default=0, help='Limits the number of segments scanned (by default there is no limit)')
    arg_parser.add_argument('-b', '--bing', action='store_true', dest = 'use_bing', default=False, help='Use Bing as search engine (default is Google Scholar)')
    arg_parser.add_argument('-n', type=int, dest='segment_size', default=9, help='Size of the segments to use when splitting the input text (default is 9)')
    arg_parser.add_argument(type=argparse.FileType('r'), dest='text', help='Text file to scan')
    arg_parser.add_argument(type=argparse.FileType('w'), dest='report', help='Text file where the report is written')

    try:
        args = arg_parser.parse_args()
    except:
        return -1


    if args.use_proxy:
        print("Looking for a proxy")
        proxy = ProxyGenerator()
        while True:
            proxy_url = FreeProxy(rand=True, timeout=1).get()
            if proxy_url == None:
                print("Fail to get a proxy")
                return -3
            print("... trying with " + str(proxy_url))
            success = proxy.SingleProxy(http=proxy_url)
            if success:
                try:
                    print("Setting proxy " + str(proxy_url))
                    scholarly.use_proxy(proxy, proxy)
                except:
                    continue
                print("Done")
                break

    t=args.text.read()
    queries = getQueries(t,args.segment_size)
    q = [' '.join(d) for d in queries]

    #using 2 dictionaries: c and output
    #output is used to store the url as key and number of occurrences of that url in different searches as value
    #c is used to store url as key and tuple (score, text/brief) leading to this match

    nb_segments = len(q)
    loop_end = args.seg_start + args.limit
    print("Found " + str(nb_segments) + " segments")
    if args.limit == 0 or loop_end > nb_segments:
        loop_end = nb_segments

    output = {}
    c = {}
    try:
        i=1
        print("Start processing from " + str(args.seg_start) + " to " + str(loop_end))
        for s in q[args.seg_start:loop_end]:
            if args.use_bing:
                output,c=searchBing(s, output, c)
            else:
                output,c=searchScholar(s,output,c)

            msg = "\r"+str(i+args.seg_start)+"/"+str(nb_segments)+"completed..."
            sys.stdout.write(msg)
            sys.stdout.flush()
            i=i+1
    except:
        print("Uh Oh! Plagiarism search had to stop")
        print(traceback.format_exc())
    finally:
        # In all cases, let's try to save the results
        for ele in sorted(iter(c.items()),key=operator.itemgetter(1),reverse=True):
            # f.write(str(ele[1][1]) + str(" - ") + str(ele[0]) + str("(") + str(ele[1][0]) + str(")"))
            args.report.write(str(ele[1][0]) + " - " + str(ele[0]) + '\n')
            for t in ele[1][1]:
                args.report.write("--> " + str(t[1]) + '\n')
                args.report.write('\t' + t[0] + '\n')

            # args.report.write(str(ele[1][1]) + str("(") + str(ele[1][0]) + str(")"))
            args.report.write("\n")

    print("\nDone!")


if __name__ == "__main__":
    try:
        main()
    except:
        #writing the error to stdout for better error detection
        error = traceback.format_exc()
        print(("\nUh Oh!\n"+"Plagiarism-Checker encountered an error!:\n" + error))


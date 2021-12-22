# -*- coding: utf-8 -*-
# Master script for the plagiarism-checker
# Coded by: Shashank S Rao

#import other modules
from cosineSim import *
from htmlstrip import *

from scholarly import scholarly
from scholarly import ProxyGenerator
from fp.fp import FreeProxy

#import required modules
import codecs
import traceback
import sys
import operator
import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse
import json as simplejson
import time

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
        text =  text
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
            if art_title in output:
                output[art_title] = output[art_title] + 1
                c[art_title] = (it['pub_url'] , text) # (c[art_title]*(output[art_title] - 1) + cosineSim(text,strip_tags(content)))/(output[art_title])
            else:
                output[art_title] = 1
                c[art_title] = (it['pub_url'] , text) # cosineSim(text,strip_tags(content))
    except:
        return output,c
    return output,c


# Use the main function to scrutinize a file for
# plagiarism
segment_limit = 0
start = 482
def main():
    # n-grams N VALUE SET HERE
    n=9
    if len(sys.argv) <3:
        print("Usage: python main.py <input-filename>.txt <output-filename>.txt")
        sys.exit()
    else:
        t=open(sys.argv[1],'r')
        if not t:
            print("Invalid Filename")
            print("Usage: python main.py <input-filename>.txt <output-filename>.txt")
            sys.exit()
        t=t.read()


    print("Looking for a proxy")
    proxy = ProxyGenerator()
    while True:
        proxy_url = FreeProxy(rand=True, timeout=1).get()
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
            #print("Fail to set the proxy (" + str(proxy_url) + str(")"))
            #return -2


    queries = getQueries(t,n)
    q = [' '.join(d) for d in queries]

    #using 2 dictionaries: c and output
    #output is used to store the url as key and number of occurences of that url in different searches as value
    #c is used to store url as key and tuple of URL and text leading to this match
    output = {}
    c = {}
    i=1
    count = len(q)
    print("Found " + str(count) + " segments")
    if segment_limit != 0 and count>segment_limit:
        count=segment_limit
        print("Limiting to " + str(segment_limit) + " segments")

    try:
        for s in q[start:count]:
            output,c=searchScholar(s,output,c)
            msg = "\r"+str(i+start)+"/"+str(count)+"completed..."
            sys.stdout.write(msg)
            sys.stdout.flush()
            i=i+1
    except:
        print("Uh Oh! Plagiarism search had to stop")
        print(traceback.format_exc())
    finally:
        # In all cases, let's try to save the results
        f = open(sys.argv[2],"w")
        for ele in sorted(iter(c.items()),key=operator.itemgetter(1),reverse=True):
            # f.write(str(ele[1][1]) + str(" - ") + str(ele[0]) + str("(") + str(ele[1][0]) + str(")"))
            f.write(str(ele[1][1]) + str("(") + str(ele[1][0]) + str(")"))
            f.write("\n")
        f.close()

    #print "\n"

    print("\nDone!")


if __name__ == "__main__":
    try:
        main()
    except:
        #writing the error to stdout for better error detection
        error = traceback.format_exc()
        print(("\nUh Oh!\n"+"Plagiarism-Checker encountered an error!:\n" + error))


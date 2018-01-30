#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
for the purpose of crawling http://jieshaowang.com/jobs/restaurant/ information
"""

from bs4 import BeautifulSoup
import requests
import os

def run(url):
    current_path = os.getcwd()
    review_path = os.path.join(current_path, 'review.csv')
    for i in range(1, page_num + 1):
        print('page: ', i)

        if i == 1:
            pageLink = url
        else:
            pageLink = url + '/' + str(i) + '.html'

        try:
            response = requests.get(pageLink)
            html = response.content
            break
        except Exception as e:
            print("The exception is: ", e)

            html = None
            for i in range(5):
            try:
                response = requests.get(pageLink, headers={ 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36', })
                html = response.content
                break
            except Exception as e:
                print("The exception is :", e)
        
        if not html:
            continue
        
        soup = BeautifulSoup(html.decode("ascii", "ignore"), "lxml")
        lists = soup.find("ul", {"class":"listing"}).findAll('a')

        with open(review_path, 'a+') as fw:
            for list in lists:
                head = getHead(list)
                phone = getPhone(list)
                address = getAddress(list)
                position = getPosition(list)
                fw.write(head + '\t' + phone + '\t' + address + '\t' + position + '\n')
        
        

def getHead(list):
    headChunk = list.find('a', {'class':'external'})
    if headChunk:
        return headChunk.text
    else:
        return "NA"
    
def getPhone(list):
    phoneChunk = list.find('em')
    if phoneChunk:
        return phoneChunk.text
    else:
        return "NA"

def getAddress(list):
    addressChunk = list.find('div', {'class':'state'}).find('a')
    if addressChunk:
        return addressChunk.text.split(' / ')[2]
    else:
        return "NA"


def getPosition(list):
    positionChunk = list.find("div", {'class':'position'}).find('a')
    if positionChunk:
        return positionChunk.text
    else:
        return "NA"

if __name__=='__main__':
    url='http://jieshaowang.com/jobs/restaurant/'
    run(url)
    
    
    
    
    
    
    
    
    
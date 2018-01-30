#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
for the purpose of crawling http://jieshaowang.com/jobs/restaurant/ information
"""


from bs4 import BeautifulSoup
import urllib2
import os

def run(url, page_num):
    Path = os.getcwd()
    csv_path = os.path.join(Path, 'result.csv')

    with open(csv_path, 'a+') as fw:
        line = 'Heading' + '\t' + 'phone' + '\t' + 'address' + '\t' + 'position' + '\n'
        fw.write(line.encode('utf-8'))

    for i in range(1, page_num + 1):
        print('page: ',i)
        if i == 1:
            pageLink = url
        else:
            pageLink = url + '/' + str(i) + '.html'

        try:
            response = urllib2.urlopen(pageLink)
            html = response.read().decode('utf-8', 'ignore')

        except Exception as e:
            print('The exception is: ', e)

        if not html:
            continue

        soup = BeautifulSoup(html, 'lxml')
        lists = soup.find('ul', {'class': 'listing'}).findAll('li')

        with open(csv_path, 'a+') as fw:
            for l in lists:
                head = getHead(l)
                phone = getPhone(l)
                address = getAddress(l)
                position = getPosition(l)
                line = head + '\t' + phone + '\t' + address + '\t' + position + '\n'
                fw.write(line.encode('utf-8'))

        print(pageLink + ' successfully crawled.')

def getHead(l):
    headChunk = l.find('h3').find('a')
    if headChunk:
        return headChunk.text
    else:
        return "NA"


def getPhone(l):
    phoneChunk = l.find('h3').find('em')
    if phoneChunk:
        return phoneChunk.text[3:]
    else:
        return "NA"


def getAddress(l):
    addressChunk = l.find('div', {'class': 'state'}).find('a')
    if addressChunk:
        return addressChunk.text.split(' / ')[2]
    else:
        return "NA"


def getPosition(l):
    positionChunk = l.find("div", {'class': 'position'}).find('a')
    if positionChunk:
        return positionChunk.text
    else:
        return "NA"


if __name__ == '__main__':
    url = 'http://jieshaowang.com/jobs/restaurant/'
    # specify the number of pages you want to crawl, 10 as an arbitrary example here
    run(url, 10)


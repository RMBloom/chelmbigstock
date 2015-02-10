#!/usr/bin/env python3

'''
Oct 23, 2014
@author Hideki Ikeda
'''

import argparse
import datetime
import os
import sys
from urllib import request as urlreq
from urllib import error as urlerr

url_header='http://ichart.finance.yahoo.com/table.csv?s={sym}'
url_from='&a={m}&b={d}&c={y}'
url_to='&d={m}&e={d}&f={y}&g=d'
url_trailer='&ignore=.csv'
iso_date_fmt = '%Y-%m-%d'

def download_stocks(symbols, from_date = None, to_date = None, f_result = 'stock.csv'):
    '''
    Download stock quotes from Yahoo finance web page and stores as a file
    Input:
        symbols   : iterable object of stock symbols
        from_date : date string in ISO format. ex) '2014-02-23' for Feb 23, 2014
                    If None, retrieve data from the beginning. Default is None.
        to_date   : date string in ISO format. If None, uses today's.
                    Default is None.
        f_result  : file name where the stock data is stored
                    Default is 'stock.csv'
    Return:
        None
    Exceptions:
        exceptions which datetime.datetime.strptime throws
        exceptions which the symbols iterable object throws
    '''

    # make part of the url which is common in all stocks
    url_list = []
    if from_date is not None:
        from_date = datetime.datetime.strptime(from_date, iso_date_fmt)
        url_list.append( url_from.format(
            m = from_date.month - 1, d = from_date.day, y = from_date.year
            ) )
    if to_date is not None:
        to_date = datetime.datetime.strptime(to_date, iso_date_fmt)
        url_list.append( url_to.format(
            m = to_date.month - 1, d = to_date.day, y = to_date.year
            ) )
    url_list.append(url_trailer)

    url_last = ''.join(url_list)

    with open(f_result, 'w') as dst:
        for symbol in symbols:
            url = url_header.format(sym = symbol) + url_last
            print('Downloading {} ...'.format(symbol))

            try:
                with urlreq.urlopen(url) as src:
                    for bline in src:
                        dst.write(symbol + ',' + bline.decode('utf-8'))
            except urlerr.URLError as e:
                print('Failed to download "{}", Reason:"{}"; Skip'.format(symbol, e.reason), file=sys.stderr)
                continue
            except IOError:
                print('Failed to write to "{}": continue'.format(file_name), file=sys.stderr)
                continue


def read_symbols(file_name, max_symbols = None):
    '''
    Read a stock symbol file in text and put stock symbols into a list.
    Input:
        filename: the file name of the stock symbol file
        max_symbols: max number of symbols we take. Default: all
    Return:
        The list of stock symbols
    Exceptions:
        Exceptions which open() throws
    '''
    with open(file_name,'r') as f_stocks:
        symbols = []
        if max_symbols is not None:
            cnt = 0
        for line in f_stocks:
            if max_symbols is not None:
                if cnt >= max_symbols:
                    break
                cnt += 1
            symbols.append( line.strip() )
    return symbols


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Get stock data from Yahoo finance')
    parser.add_argument('-s', '--symbol_file', default='stock_symbols.txt',
            metavar='stock_symbol_file', dest='symbol_file_name',
            help='A text file contains stock symbols. Default:stock_symbols.txt')
    parser.add_argument('-m', '--max_stocks', type=int, default = None,
            metavar='N', dest='max',
            help='the maxinum number of stocks to be processed. Default:All')
    parser.add_argument('-r', '--result_file', default='stock.csv',
            metavar='result_file_name', dest='f_result',
            help='A csv file name where the downloaded data is stored. Default:stock.csv')
    parser.add_argument('-f', '--from_date', default=None,
            metavar='from_date', dest='from_date',
            help='The first date of stock data. Default:Oldest possible')
    parser.add_argument('-t', '--to_date', default=None,
            metavar='to_date', dest='to_date',
            help='the last date of stock data. Default:Today')

    opt = parser.parse_args()

    symbols = read_symbols(opt.symbol_file_name, opt.max)
    download_stocks(symbols, from_date=opt.from_date, to_date=opt.to_date,
            f_result=opt.f_result)

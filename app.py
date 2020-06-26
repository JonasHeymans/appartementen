import logging
import sys
import pandas as pd
import time
from bs4 import BeautifulSoup
import re
import json

from Downloader.downloader import Downloader

logging.basicConfig(format='%(asctime) s %(levelname) -8s [%(filename) s:%(lineno) d] %(message) s',
                    datefmt='%d-%m-%Y:%H:%M:%S',
                    level=logging.INFO,
                    stream=sys.stdout)

logger = logging.getLogger('basic')

main = Downloader.read_pickle('file')
instances = Downloader.read_pickle('full')




urls = Downloader.get_url_list('full', range(1,143))
print(urls)

df = Downloader.get_df(urls, 'full')

print(df)





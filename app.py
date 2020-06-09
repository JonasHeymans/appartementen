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

df = main.merge(instances, on='id').reset_index(drop=True )
Downloader.save_pickle(df, 'all')
df.to_csv('all.csv')


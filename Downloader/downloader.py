import logging
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import json
import re
import pandas as pd
import time
from itertools import cycle



logger = logging.getLogger('basic_downloader')

class Downloader():
    session = HTMLSession()

    @classmethod
    def get_url_list(cls,url_type,ids):
        logger.info(f'Getting Urls')
        url_types = {
            'full' : 'https://www.immoweb.be/en/search/house-and-apartment/for-sale/antwerp/district?countries=BE&page=',
            'unique': 'https://www.immoweb.be/en/classified/house/for-sale/Berchem/2930/'
        }
        return [f'{url_types[url_type]}{id}' for id in ids]

    @classmethod
    def __get_page(self, url):
        logger.info(f"Getting page {url}")
        r =  self.session.get(url)
        return r

    @classmethod
    def __parse_overview_page(self, page):
        logger.info(f'Starting to parse overview page')
        page.html.render()
        page = page.text
        soup = BeautifulSoup(page, 'html.parser')

        alles = soup.body.main
        alles = str(alles).strip('\n')

        eerste, tweede = re.findall(':results=\\\'(.*)\\\' :results-storage=\'', alles)[0], \
                         re.findall(':results-storage=\'(.*)\' :unique-id=', alles)[0]

        logger.info(f'Parsing overview page done')
        return json.loads(eerste)

    @classmethod
    def __parse_unique_page(cls,page,id):
        logger.info(f'Starting to parse unique page')
        page.html.render()
        page = page.text
        soup = BeautifulSoup(page, 'html.parser')
        d = {}
        # d['id'] = next(idscycle)
        d['id'] = id

        grid = soup.body.main.findAll("strong", {"class": "overview__text"})
        for x in grid:
            string = x.text.replace("\n", "").replace("  ", "")
            title = re.findall('\D*', string)
            title = ",".join(string.strip(' ') for string in title if len(string) > 0)
            value = re.findall('([0-9]*)', string)
            value = ",".join(string.strip(' ') for string in value if len(string) > 0)
            d[title] = value

        text_block = soup.body.main.findAll("td", {"class": "classified-table__data"})
        title_block = soup.body.main.findAll("th", {"class": 'classified-table__header'})

        for x, y in zip(text_block, title_block):
            value = x.text.replace('\n', '').replace('  ', '')
            title = y.text.replace('\n', '').replace('  ', '')
            d[title] = value

        logger.info(f'Parsing unique page done')
        return pd.Series(d)

    @classmethod
    def get_df(cls,url_list, type, ids = 0, start_point = 0):
        # idscycle = cycle(ids)
        logger.info(f'Starting to get DF')
        df = pd.DataFrame()
        counter = start_point + 1
        start = time.time()
        urls = url_list[start_point:]
        for url in urls:
            page = cls.__get_page(url)
            local_start = time.time()
            logger.info(f'Starting on url {counter} of {len(url_list)} ({(counter/len(url_list))*100:.2f}%)')
            if type == 'full':
                eerste = cls.__parse_overview_page(page)
                for x in eerste:
                    line = pd.json_normalize(x).iloc[0]
                    df = df.append(line)
            else:
                logger.info(f'Id {ids[counter-1]} en Url: {url}')
                id = ids[counter-1]
                df = df.append(cls.__parse_unique_page(page,id), ignore_index=True)

            if counter % 25 == 0:
                logger.info(f'Temp saving the df')
                df.to_csv(f'files/tijdelijk/Immoweb_tijdelijk_{type}_{start_point}-{counter}.csv')
                logger.info(f"Time elapsed: {time.time() - start :.2f} seconds")

            logger.info(f'Finished url {counter} in {time.time() - local_start :.2f} seconds\n')

            counter += 1

        df = df.reset_index(drop=True)
        logger.info(f'Getting DF complete')
        logger.info(f'Total time: {time.time() - start :.2f} seconds')
        return df

    @classmethod
    def save_pickle(cls,df,filename='file'):
        save_location = f'files/{filename}.pkl'
        df.to_pickle(save_location)
        logger.info(f'Saved {filename} to {save_location}')

    @classmethod
    def read_pickle(cls,filename):
        load_location = f"files/{filename}.pkl"
        logger.info(f'Loading Pickle from {load_location}')
        return pd.read_pickle(load_location)

    @classmethod
    def combine_csvs(cls):
        import os
        import glob
        import pandas as pd

        logger.info(f"Combining CSV's")
        os.chdir("files/tijdelijk")
        extension = 'csv'
        filenames = [i for i in glob.glob('*.{}'.format(extension))]

        # combine all files in the list
        combined_csv = pd.concat([pd.read_csv(f) for f in filenames])
        # export to csv
        save_location = "../combined_csv"
        combined_csv.to_csv(save_location, index=False, encoding='utf-8-sig')
        logger.info(f'Combined filenames {filenames} and saved to {save_location}')



    @classmethod
    def get_ids(cls,file):
        logger.info("Getting ID's")
        return file['id'].astype(int).to_list()




















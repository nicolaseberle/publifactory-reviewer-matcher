from bs4 import BeautifulSoup
from article import Article

import requests
import constants


class Scholar(object):

    def __init__(self):
        self.num_results = 0
        self.csv_link = None

    @staticmethod
    def download(link, filename):
        h = requests.head(link, allow_redirects=True)
        header = h.headers
        content_type = header.get('content-type')
        if 'text' in content_type.lower() or 'html' in content_type.lower():
            return False
        r = requests.get(link, allow_redirects=True)
        print("Downloading: %s" % link)
        open(filename, 'wb').write(r.content)

    def search(self, discipline, query, show_all=False, page=1):
        req = requests.get('%s/search/page/%s?query=%s&facet-discipline=%s&showAll=%s' % (constants.BASE, page, query, discipline, show_all))
        soup = BeautifulSoup(req.content, 'html.parser')
        try:
            nr = soup.find('h1', {'class': 'number-of-search-results-and-search-terms'})
            self.num_results = nr.find('strong').text
            self.num_results = ''.join(c for c in self.num_results if c.isnumeric())
            print("Found %s results" % self.num_results)
            if not int(self.num_results) > 0:
                return False
        except Exception as e:
            print(e.message)
        self.csv_link = constants.BASE + soup.find('a', {'id': 'tool-download'})['href']
        article_list = soup.find('ol', {'id': 'results-list'})
        results = []
        [results.append(Article(a)) for a in article_list.find_all('li')]
        return results

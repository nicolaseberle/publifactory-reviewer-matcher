import constants


class Article:

    def __init__(self, article_data):
        self._article_data = article_data

    @property
    def title(self):
        try:
            return self._article_data.find('a', {'class': 'title'}).text.strip()
        except Exception as e:
            return

    @property
    def authors(self):
        try:
            authors = self._article_data.find('span', {'class': 'authors'})
            return [author.text.strip() for author in authors.find_all('a')] if authors is not None else ''
        except Exception as e:
            return

    @property
    def pdf_link(self):
        try:
            return constants.BASE + self._article_data.find('a', {'class': 'pdf-link'})['href']
        except Exception as e:
            return

    @property
    def view_link(self):
        try:
            return constants.BASE + self._article_data.find('a', {'class': 'fulltext'})['href']
        except Exception as e:
            return

    @property
    def publication_title(self):
        try:
            return self._article_data.find('a', {'class': 'publication-title'}).text.strip()
        except Exception as e:
            return

    @property
    def publication_title_link(self):
        try:
            return constants.BASE + self._article_data.find('a', {'class': 'publication-title'})['href']
        except Exception as e:
            return

    @property
    def snippet(self):
        try:
            return self._article_data.find('p', {'class': 'snippet'}).text.strip()
        except Exception as e:
            return

    @property
    def content_type(self):
        try:
            return self._article_data.find('p', {'class': 'content-type'}).text.strip()
        except Exception as e:
            return

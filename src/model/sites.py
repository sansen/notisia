import re
import time
import requests

from bs4 import Comment
from bs4 import BeautifulSoup


class Site:
    def __init__(self, site, scrapi_fields):
        self.site = site
        self.scrapi_fields = scrapi_fields
        self.noticias_id = []
        self.noticias = {}
        self.noticias_db = []

    def retrieve_site_data(self):
        pass

    def retrieve_home_news(self):
        self.site_fields = self.scrapi_fields.get_site(self.site)

        r = requests.get(self.site_fields['base_url'])
        portada = BeautifulSoup(r.text, 'html.parser')

        tmp_noticias_db = list(set(
            [n_id[0] for n_id in self.noticias_db]
        ))

        if self.site_fields['front_container']:
            links_noticias = portada.select(self.site_fields['front_container'])

            for n in links_noticias:
                t=''
                a=''
                l = n.select_one(self.site_fields['front_container_link'])
                if not l or l.get('href', '') == '':
                    continue
                else:
                    l = l.get('href')

                if n.select_one(self.site_fields['front_container_title']):
                    t = n.select_one(self.site_fields['front_container_title']).text.strip()
                if n.select_one(self.site_fields['front_container_author']):
                    a = n.select_one(self.site_fields['front_container_author']).text.strip()


                if not l.startswith('https://') and \
                   not l.startswith('http://'):
                    l = self.site_fields['base_url'] + l

                if l not in tmp_noticias_db:
                    self.noticias_db.append([l, t, a, time.time(), self.site])
                    self.noticias_id.append(l)


    def retrieve_news(self, noticia_url):
        if noticia_url in self.noticias.keys():
            pass
        r = requests.get(noticia_url)
        bs = BeautifulSoup(r.text, 'html.parser')

        notice = self.new_scrap_body(bs)
        category_raw = self.new_scrap_category(bs)
        title_raw = self.new_scrap_title(bs)
        author_raw = self.new_scrap_author(bs)
        date_raw = self.new_scrap_date(bs)

        if noticia_url not in self.noticias.keys():
            self.noticias[noticia_url] = {
                'date': date_raw,
                'category': category_raw,
                'title': title_raw,
                'author': author_raw,
                'body': notice,
                'uri': noticia_url
            }

    def get_new(self, noticia_url):
        return self.noticias[noticia_url]

    def retrieve_sections(self):
        pass

    def filter_links(self, link, links):
        links.append(link)

    def new_scrap_category(self, bs):
        # scrap category
        try:
            category_raw = bs.select(self.site_fields['new_category'])
            category_raw = category_raw[0].text.strip().upper() if len(category_raw) > 0 else ''
        except Exception:
            category_raw = ''
        return category_raw

    def new_scrap_title(self, bs):
        # scrap title
        title_raw = bs.select(self.site_fields['new_title'])
        title_raw = title_raw[0].text.upper() if len(title_raw) > 0 else ''
        return title_raw

    def new_scrap_author(self, bs):
        # scrap author
        author_raw = bs.select(self.site_fields['new_author'])
        author_raw = author_raw[0].text if len(author_raw) > 0 \
            else self.site_fields['pretty_name']
        return author_raw

    def new_scrap_date(self, bs):
        # scrap date
        date_raw = bs.select(self.site_fields['new_date'])
        date_raw = date_raw[0].text if len(date_raw) > 0 else ''
        return date_raw

    def new_scrap_body(self, bs):
        # scrap body
        notice = ''
        notice_raw = bs.select(self.site_fields['new_wrapper'])

        for container in notice_raw:
            for item in container.children:
                if item.name in ['p', 'h2', 'h3', 'h4', 'h6'] \
                   and len(item.text) > 0:
                    notice += item.text.strip().strip('\r\n') + '\n\n'
                elif item.name in ['strong'] and len(item.text) > 0:
                    notice += item.text.strip().strip('\r\n') + ' '
                elif item.name == 'div' \
                     and len(self.site_fields.get('noticia_element_class', [])) > 0:
                    item = item.select(self.site_fields.get('noticia_element_class'))
                    if len(item) > 0:
                        item = item[0]
                        notice += item.text.strip().strip('\r\n') + ' '
                elif item.name == None and \
                     len(item) > 0 and not isinstance(item, Comment):
                    notice += item.strip() + ' '

        return notice


class Clarin(Site):
    def filter_links(self, link, links):
        """Get news links from clarin.com portal."""
        if link.endswith('.html'):
            links.append(link)


class Pagina(Site):
    def filter_links(self, link, links):
        """Get news links from pagina12.com portal."""
        if link.startswith('https://www.pagina12.com.ar/') and 'suplementos' not in link \
           and 'opinion' not in link:
            links.append(link)

class Telam(Site):
    def filter_links(self, link, links):
        """Get news links from telam.com.ar portal."""
        if link.startswith('https://www.telam.com.ar/notas'):
            links.append(link)

class Cronica(Site):
    def filter_links(self, link, links):
        """Get news links from telam.com.ar portal."""
        if link.startswith('https://www.cronica.com.ar/'):
            links.append(link)


class SiteFactory:
    def getSiteInstance(site, scrapi_fields):
        if site == 'clarin':
            site_instance = Clarin(site, scrapi_fields)
        elif site == 'pagina12':
            site_instance = Pagina(site, scrapi_fields)
        elif site == 'telam':
            site_instance = Telam(site, scrapi_fields)
        elif site == 'cronica':
            site_instance = Cronica(site, scrapi_fields)
        else:
            site_instance = Site(site, scrapi_fields)
        return site_instance

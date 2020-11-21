# This file is part of Foobar.

# Foobar is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <https://www.gnu.org/licenses/>.


import requests
import threading

from datetime import date
from docopt import docopt

from src.model import sites
from src.model.stats import Stats
from src.model.database import Database


class ScrAPIFields:
    def __init__(self, url):
        self.api_url = url
        self.media = {
            'clarin': {
                'pretty_name': 'Clarín',
                'base_url': 'https://www.clarin.com/',
                'front_links': '.content-nota a',
                'site_image': '.content-nota a',
                'site_section': '.content-nota a',
                'noticias_id': [],
                'noticias_full': {},
                'new_wrapper': '.body-nota',
                'new_pretitle': 'h1#title',
                'new_title': 'h1#title',
                'new_subtitle': 'h1#title',
                'new_date': '.breadcrumb span',
                'new_category': '.section-name span',
                'new_author': '.entry-author a p',
                'new_body': '.entry-author a p',
                'new_image': '.entry-author a p',
                'new_source': '.entry-author a p',
                'author_name': '.entry-author a p',
                'author_email': '.entry-author a p',
                'author_site': '.entry-author a p',
                'author_image': '.entry-author a p',
            },
            'pagina12': {
                'pretty_name': 'Página 12',
                'base_url': 'https://www.pagina12.com.ar/',
                'front_links': '.article-title a',
                'site_image': '.content-nota a',
                'site_section': '.content-nota a',
                'noticias_id': [],
                'noticias_full': {},
                'new_wrapper': 'article .article-body .article-text',
                'new_pretitle': 'h1#title',
                'new_title': 'article .article-titles .article-title',
                'new_subtitle': 'h1#title',
                'new_date': '.article-info .time span',
                'new_category': '.article-info .suplement a',
                'new_author': 'article .article-main-media-header .article-author a',
                'new_body': '.entry-author a p',
                'new_image': '.entry-author a p',
                'new_source': '.entry-author a p',
                'author_name': '.entry-author a p',
                'author_email': '.entry-author a p',
                'author_site': '.entry-author a p',
                'author_image': '.entry-author a p',
            },
            'minutouno': {
                'pretty_name': 'Minuto Uno',
                'base_url': 'https://www.minutouno.com/',
                'front_links': 'article h2.title a',
                'site_image': '.content-nota a',
                'site_section': '.content-nota a',
                'noticias_id': [],
                'noticias_full': {},
                'new_wrapper': '.detail-body p',
                'new_pretitle': '',
                'new_title': 'h1.title',
                'new_subtitle': '',
                'new_date': 'section span.date',
                'new_category': '.media-wrapper h2',
                'new_author': 'section .author span.name',
                'new_body': '.detail-body p',
                'new_image': '.entry-author a p',
                'new_source': '.entry-author a p',
                'author_name': '.entry-author a p',
                'author_email': '.entry-author a p',
                'author_site': '.entry-author a p',
                'author_image': '.entry-author a p',
            },
            'cronica': {
                'pretty_name': 'Cronica',
                'base_url': 'https://www.cronica.com.ar',
                'front_links': 'article a.cover-link',
                'site_image': '.content-nota a',
                'site_section': '.content-nota a',
                'noticias_id': [],
                'noticias_full': {},
                'new_wrapper': 'article .inner-container .nota-body-container .main-content section .entry-body p',
                'new_pretitle': '',
                'new_title': 'article .title-top h1',
                'new_subtitle': 'article .inner-container .nota-body-container .title h2 p',
                'new_date': 'article .title-top span .entry-time',
                'new_category': 'article .title-top span.entry-label',
                'new_author': 'article .inner-container .nota-body-container .main-content .author-data-container span.author-name ',
                'new_body': 'article .inner-container .nota-body-container .main-content section .entry-body p',
                'new_image': '.entry-author a p',
                'new_source': '.entry-author a p',
                'author_name': '.entry-author a p',
                'author_email': '.entry-author a p',
                'author_site': '.entry-author a p',
                'author_image': '.entry-author a p',
            },
            'ambito': {
                'pretty_name': 'Ambito Financiero',
                'base_url': 'https://www.ambito.com/',
                'front_links': '.info-wrapper h2.title a',
                'site_image': '.content-nota a',
                'site_section': '.content-nota a',
                'noticias_id': [],
                'noticias_full': {},
                'new_wrapper': '.detail-body p',
                'new_pretitle': '',
                'new_title': '.detail-header-wrapper h1.title',
                'new_subtitle': '',
                'new_date': '.detail-header-wrapper .date',
                'new_category': '.detail-header-wrapper .article-theme',
                'new_author': '.person span.person-name',
                'new_body': '.detail-body p',
                'new_image': '.entry-author a p',
                'new_source': '.entry-author a p',
                'author_name': '.entry-author a p',
                'author_email': '.entry-author a p',
                'author_site': '.entry-author a p',
                'author_image': '.entry-author a p',
            },
            'eldesapeweb': {
                'pretty_name': 'El Destape Web',
                'base_url': 'https://www.eldestapeweb.com',
                'front_links': '.nota .titulo h2 a',
                'site_image': '.content-nota a',
                'site_section': '.content-nota a',
                'noticias_id': [],
                'noticias_full': {},
                'new_wrapper': '.container .nota_contenido .cuerpo p',
                'new_pretitle': '',
                'new_title': '.container h1.titulo',
                'new_subtitle': '.container h2.intro',
                'new_date': '.container .cont_autor .fecha',
                'new_category': '.container .breadcrumb a span',
                'new_author': '.container .cont_autor .autor .firmante',
                'new_body': '.container .nota_contenido .cuerpo p',
                'new_image': '.entry-author a p',
                'new_source': '.entry-author a p',
                'author_name': '.entry-author a p',
                'author_email': '.entry-author a p',
                'author_site': '.entry-author a p',
                'author_image': '.entry-author a p',
            },
            'telam': {
                'pretty_name': 'Agencia Telam',
                'base_url': 'https://www.telam.com.ar/',
                'front_links': 'div.main-content-block a',
                'site_image': '.content-nota a',
                'site_section': '.content-nota a',
                'noticias_id': [],
                'noticias_full': {},
                'new_wrapper': 'div.main-container div.main-content-block div.editable-content',
                'new_pretitle': 'h1#title',
                'new_title': 'div.main-container div.head-content h2',
                'new_subtitle': 'h1#title',
                'new_date': 'div.main-container div.head-content .data p',
                'new_category': 'div.main-container div.head-section h2',
                'new_author': 'div.main-container div.head-content .author',
                'new_body': '.entry-author a p',
                'new_image': '.entry-author a p',
                'new_source': '.entry-author a p',
                'author_name': '.entry-author a p',
                'author_email': '.entry-author a p',
                'author_site': '.entry-author a p',
                'author_image': '.entry-author a p',
            },
            'infobae': {
                'pretty_name': 'Infobae',
                'base_url': 'https://www.infobae.com/',
                'front_links': '.headline a',
                'site_image': '.content-nota a',
                'site_section': '.content-nota a',
                'noticias_id': [],
                'noticias_full': {},
                'noticia_element_class': '.element-paragraph',
                'new_wrapper': 'section.main article.article',
                'new_pretitle': 'h1#title',
                'new_title': 'h1',
                'new_subtitle': 'h1#title',
                'new_date': 'section.main .header .datetime',
                'new_category': '.header-label a',
                'new_author': 'section.main .header span.author a',
                'new_body': '.entry-author a p',
                'new_image': '.entry-author a p',
                'new_source': '.entry-author a p',
                'author_name': '.entry-author a p',
                'author_email': '.entry-author a p',
                'author_site': '.entry-author a p',
                'author_image': '.entry-author a p',
            },
            'cohete': {
                'pretty_name': 'Cohete a la luna',
                'base_url': 'https://www.elcohetealaluna.com/',
                'front_links': 'article h2.title a',
                'site_image': '.content-nota a',
                'site_section': '.content-nota a',
                'noticias_id': [],
                'noticias_full': {},
                'new_wrapper': 'article .single-post-content',
                'new_pretitle': 'h1#title',
                'new_title': 'article h1 .post-title',
                'new_subtitle': 'h1#title',
                'new_date': '.time time',
                'new_category': 'span.categoria.tag a',
                'new_author': 'article .post-author-name',
                'new_body': '.entry-author a p',
                'new_image': '.entry-author a p',
                'new_source': '.entry-author a p',
                'author_name': '.entry-author a p',
                'author_email': '.entry-author a p',
                'author_site': '.entry-author a p',
                'author_image': '.entry-author a p',
            },    
            'tiempoar': {
                'pretty_name': 'Tiempo Argentino',
                'base_url': 'https://www.tiempoar.com.ar/',
                'front_links': '.card-body a',
                'noticias_id': [],
                'noticias_full': {},
                'new_wrapper': 'article.art-complete div.body',
                'new_pretitle': 'h1#title',
                'new_title': 'h1.art-headline',
                'new_subtitle': 'h1#title',
                'new_date': '.author-box .release-date',
                'new_category': 'article .section-name',
                'new_author': '.author-string a',
                'new_body': '.entry-author a p',
                'new_image': '.entry-author a p',
                'new_source': '.entry-author a p',
                'author_name': '.entry-author a p',
                'author_email': '.entry-author a p',
                'author_site': '.entry-author a p',
                'author_image': '.entry-author a p',
            },
            'lanacion': {
                'pretty_name': 'La Nación',
                'base_url': 'https://www.lanacion.com.ar/',
                'front_links': 'article a',
                'site_image': '.content-nota a',
                'site_section': '.content-nota a',
                'noticias_id': [],
                'noticias_full': {},
                'new_wrapper': 'article #cuerpo',
                'new_pretitle': 'h1#title',
                'new_title': 'h1.titulo',
                'new_subtitle': 'h1#title',
                'new_date': 'section .fecha',
                'new_category': 'span.categoria.tag a',
                'new_author': 'div.datos a',
                'new_body': '.entry-author a p',
                'new_image': '.entry-author a p',
                'new_source': '.entry-author a p',
                'author_name': '.entry-author a p',
                'author_email': '.entry-author a p',
                'author_site': '.entry-author a p',
                'author_image': '.entry-author a p',
            },
        }

    def get_sites(self):
        try:
            r = requests.get(f"{self.api_url}/media/sites", timeout=0.5)
            sites = r.json()
        except requests.exceptions.RequestException as e:
            sites = {k:v['pretty_name'] for k,v in self.media.items()}
        except Exception as e:
            print('Sitio no encontrado.')
            raise Exception('Sitio no encontrado.!')
        return sites

    def get_site(self, site):
        try:
            r = requests.get(f"{self.api_url}/media/{site}", timeout=0.5)
            site = r.json()
        except requests.exceptions.RequestException as e:
            site = self.media[site]
        except Exception as e:
            print('Sitio no encontrado.')
            raise Exception('Sitio no encontrado.!')
        return site

    def get_authors(self, site):
        r = requests.get(f"{self.api_url}/media/{site}/author", timeout=0.5)
        return r.json()

    def get_news(self, site):
        r = requests.get(f"{self.api_url}/media/{site}/news", timeout=0.5)
        return r.json()


class Medium:
    def __init__(self, url):
        self.scrapi_fields = ScrAPIFields(url)
        self.MEDIUM = self.scrapi_fields.get_sites()
        self.database = Database()
        self.stats = Stats()

    def run(self, site_name):
        site = sites.SiteFactory.getSiteInstance(
            site_name, self.scrapi_fields
        )
        self.MEDIUM[site_name] = site

        for noticia in self.database.select_noticias_id(site_name):
            site.noticias_db.append([noticia[0], noticia[1], site_name])
        site.retrieve_home_news()
        self.database.save_site(site)
        return site

    def update_news(self, site, noticia_id ):
        noticia = self.MEDIUM[site].get_new(noticia_id)
        self.database.update_new(
            noticia_id,
            noticia.get('title'),
            noticia.get('body', ''),
            noticia.get('author', '')
        )

    def search(self, query):
        notices = []
        for site_id, site_name in self.MEDIUM.items():
            noticias = self.database.search(site_id, query)
            notices.extend(noticias)
        return notices

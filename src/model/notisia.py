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


import re
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
                'front_links': 'article a',
                'front_container': 'article',
                'front_container_title': 'h2',
                'front_container_section': 'p.name.name-section',
                'front_container_author': 'p.name.name-author',
                'front_container_link': 'a',
                'site_image': '.content-nota a',
                'site_section': 'nav ul li a',
                'noticias_id': [],
                'noticias_full': {},
                'new_wrapper': '#NewsContainer .StoryTextContainer p',
                'new_pretitle': '',
                'new_title': '.storyTitle',
                'new_subtitle': '.storySummary',
                'new_date': '.createDate',
                'new_category': 'a.SectionSeparator',
                'new_author': 'article#StoryBody div.author-info div',
                'new_body': '.StoryTextContainer p',
                'new_image': '.image-container img',
                'new_source': 'article#StoryBody',
                'author_name': 'article#StoryBody div.author-info div',
                'author_email': '',
                'author_site': '',
                'author_image': 'article#StoryBody div.author-info img',
            },
            'pagina12': {
                'pretty_name': 'Página 12',
                'base_url': 'https://www.pagina12.com.ar/',
                'front_links': '.article-title a',
                'front_container': '.block-content',
                'front_container_title': '.article-title a',
                'front_container_section': '',
                'front_container_author': '.article-author .no-link',
                'front_container_link': '.article-title a',
                'site_image': '.content-nota a',
                'site_section': '.content-nota a',
                'noticias_id': [],
                'noticias_full': {},
                'new_wrapper': 'article.article-full.section .article-main-content .article-text',
                'new_pretitle': 'article.article-full.section .article-header h2.h4',
                'new_title': 'article.article-full.section .article-header h1',
                'new_subtitle': 'article.article-full.section .article-header h2.h3',
                'new_date': '.article-info .date time',
                'new_category': 'article.article-full.section .article-header h5.current-tag a',
                'new_author': 'article.article-full.section .author-inner a',
                'new_body': 'article.article-full.section .article-main-content .article-text',
                'new_image': 'article.article-full.section .article-main-imag .image-wrapper img',
                'new_source': '',
                'author_name': '.entry-author a p',
                'author_email': '.entry-author a p',
                'author_site': '.entry-author a p',
                'author_image': '.entry-author a p',
            },
            'ambito': {
                'pretty_name': 'Ambito Financiero',
                'base_url': 'https://www.ambito.com/',
                'front_links': '.news-article__title a',
                'front_container': '.news-article__info-wrapper',
                'front_container_title': '.news-article__title a',
                'front_container_section': '',
                'front_container_author': '.news-article__journalist',
                'front_container_link': '.news-article__title a',
                'site_image': '',
                'site_section': '',
                'noticias_id': [],
                'noticias_full': {},
                'new_wrapper': '.main-container.container.note article.article-body',
                'new_pretitle': '',
                'new_title': 'header.news-headline h1.news-headline__title',
                'new_subtitle': 'header.news-headline h2.news-headline__article-summary p',
                'new_date': 'header.news-headline span.news-headline__publication-date',
                'new_category': 'header.news-headline .news-headline__topic li:last-child a',
                'new_author': '.news-headline__author-name',
                'new_body': '.main-container.container.note article p',
                'new_image': '.entry-author a p',
                'new_source': '.entry-author a p',
                'author_name': '.entry-author a p',
                'author_email': '.entry-author a p',
                'author_site': '.entry-author a p',
                'author_image': '.entry-author a p',
            },
            # 'telam': {
            #     'pretty_name': 'Telam',
            #     'base_url': 'https://www.telam.com.ar/',
            #     'front_links': '.wrapper-sections .nota .content a',
            #     'front_container': '.nota .content',
            #     'front_container_title': 'a',
            #     'front_container_section': '',
            #     'front_container_author': '.author',
            #     'front_container_link': 'a',
            #     'site_image': '',
            #     'site_section': '',
            #     'noticias_id': [],
            #     'noticias_full': {},
            #     'new_wrapper': 'article.note-content div.wrapper-editable-content .paragraph',
            #     'new_pretitle': '.volanta',
            #     'new_title': 'h1',
            #     'new_subtitle': '',
            #     'new_date': '.wrapper-info-note .time',
            #     'new_category': 'article.note-content h2.module-title ',
            #     'new_author': 'article.main-container ',
            #     'new_body': 'article.note-content div.wrapper-editable-content .paragraph',
            #     'new_image': '.entry-author a p',
            #     'new_source': '.entry-author a p',
            #     'author_name': '.entry-author a p',
            #     'author_email': '.entry-author a p',
            #     'author_site': '.entry-author a p',
            #     'author_image': '.entry-author a p',
            # },
            'infobae': {
                'pretty_name': 'Infobae',
                'base_url': 'https://www.infobae.com/',
                'front_links': 'a.story-card-ctn',
                'front_container': '.default-chain-ctn',
                'front_container_title': '.headline-link',
                'front_container_section': '',
                'front_container_author': '.story-card-author-name',
                'front_container_link': 'a.story-card-ctn',
                'site_image': '.logo-image',
                'site_section': '.content-nota a',
                'noticias_id': [],
                'noticias_full': {},
                'noticia_element_class': '.element-paragraph',
                'new_wrapper': 'article.article .body-article',
                'new_pretitle': 'h1#title',
                'new_title': 'h1.article-headline',
                'new_subtitle': 'h2.article-subheadline',
                'new_date': '.sharebar-article-date',
                'new_category': '.article-section-tag',
                'new_author': 'section.article-section .article-header a.author-name',
                'new_body': 'article.article .body-article',
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
                'front_links': 'article.ln-card .link.ln-link',
                'front_container': 'article.ln-card',
                'front_container_title': '.ln-text.title',
                'front_container_section': '',
                'front_container_author': '.text.ln-text.marquee',
                'front_container_link': '.link.ln-link',
                'site_image': '.content-nota a',
                'site_section': '.content-nota a',
                'noticias_id': [],
                'noticias_full': {},
                'new_wrapper': 'main#content .cuerpo__nota .com-paragraph',  # .com-paragraph',
                'new_pretitle': '',
                'new_title': 'h1.com-title',
                'new_subtitle': 'h2.com-subhead',
                'new_date': 'span.mod-date .com-date',
                'new_category': 'main#content nav a:last-child',
                'new_author': 'div.datos a',
                'new_body': 'main#content .cuerpo__nota .com-paragraph',
                'new_image': '.entry-author a p',
                'new_source': '.entry-author a p',
                'author_name': '.entry-author a p',
                'author_email': '.entry-author a p',
                'author_site': '.entry-author a p',
                'author_image': '.entry-author a p',
            },
        }
            # 'cronica': {
            #     'pretty_name': 'Cronica',
            #     'base_url': 'https://www.cronica.com.ar',
            #     'front_links': 'article a.cover-link',
            #     'site_image': '.content-nota a',
            #     'site_section': '.content-nota a',
            #     'noticias_id': [],
            #     'noticias_full': {},
            #     'new_wrapper': 'article .inner-container .nota-body-container .main-content section .entry-body p',
            #     'new_pretitle': '',
            #     'new_title': 'article .title-top h1',
            #     'new_subtitle': 'article .inner-container .nota-body-container .title h2 p',
            #     'new_date': 'article .title-top span .entry-time',
            #     'new_category': 'article .title-top span.entry-label',
            #     'new_author': 'article .inner-container .nota-body-container .main-content .author-data-container span.author-name ',
            #     'new_body': 'article .inner-container .nota-body-container .main-content section .entry-body p',
            #     'new_image': '.entry-author a p',
            #     'new_source': '.entry-author a p',
            #     'author_name': '.entry-author a p',
            #     'author_email': '.entry-author a p',
            #     'author_site': '.entry-author a p',
            #     'author_image': '.entry-author a p',
            # },
            # 'minutouno': {
            #     'pretty_name': 'Minuto Uno',
            #     'base_url': 'https://www.minutouno.com/',
            #     'front_links': 'article h2.title a',
            #     'site_image': '.content-nota a',
            #     'site_section': '.content-nota a',
            #     'noticias_id': [],
            #     'noticias_full': {},
            #     'new_wrapper': '.detail-body p',
            #     'new_pretitle': '',
            #     'new_title': 'h1.title',
            #     'new_subtitle': '',
            #     'new_date': 'section span.date',
            #     'new_category': '.media-wrapper h2',
            #     'new_author': 'section .author span.name',
            #     'new_body': '.detail-body p',
            #     'new_image': '.entry-author a p',
            #     'new_source': '.entry-author a p',
            #     'author_name': '.entry-author a p',
            #     'author_email': '.entry-author a p',
            #     'author_site': '.entry-author a p',
            #     'author_image': '.entry-author a p',
            # },
            # 'eldesapeweb': {
            #     'pretty_name': 'El Destape Web',
            #     'base_url': 'https://www.eldestapeweb.com',
            #     'front_links': '.nota .titulo h2 a',
            #     'site_image': '.content-nota a',
            #     'site_section': '.content-nota a',
            #     'noticias_id': [],
            #     'noticias_full': {},
            #     'new_wrapper': '.container .nota_contenido .cuerpo p',
            #     'new_pretitle': '',
            #     'new_title': '.container h1.titulo',
            #     'new_subtitle': '.container h2.intro',
            #     'new_date': '.container .cont_autor .fecha',
            #     'new_category': '.container .breadcrumb a span',
            #     'new_author': '.container .cont_autor .autor .firmante',
            #     'new_body': '.container .nota_contenido .cuerpo p',
            #     'new_image': '.entry-author a p',
            #     'new_source': '.entry-author a p',
            #     'author_name': '.entry-author a p',
            #     'author_email': '.entry-author a p',
            #     'author_site': '.entry-author a p',
            #     'author_image': '.entry-author a p',
            # },
            # 'cohete': {
            #     'pretty_name': 'Cohete a la luna',
            #     'base_url': 'https://www.elcohetealaluna.com/',
            #     'front_links': 'article h2.title a',
            #     'site_image': '.content-nota a',
            #     'site_section': '.content-nota a',
            #     'noticias_id': [],
            #     'noticias_full': {},
            #     'new_wrapper': 'article .single-post-content',
            #     'new_pretitle': 'h1#title',
            #     'new_title': 'article h1 .post-title',
            #     'new_subtitle': 'h1#title',
            #     'new_date': '.time time',
            #     'new_category': 'span.categoria.tag a',
            #     'new_author': 'article .post-author-name',
            #     'new_body': '.entry-author a p',
            #     'new_image': '.entry-author a p',
            #     'new_source': '.entry-author a p',
            #     'author_name': '.entry-author a p',
            #     'author_email': '.entry-author a p',
            #     'author_site': '.entry-author a p',
            #     'author_image': '.entry-author a p',
            # },
            # 'tiempoar': {
            #     'pretty_name': 'Tiempo Argentino',
            #     'base_url': 'https://www.tiempoar.com.ar/',
            #     'front_links': '.card-body a',
            #     'noticias_id': [],
            #     'noticias_full': {},
            #     'new_wrapper': 'article.art-complete div.body',
            #     'new_pretitle': 'h1#title',
            #     'new_title': 'h1.art-headline',
            #     'new_subtitle': 'h1#title',
            #     'new_date': '.author-box .release-date',
            #     'new_category': 'article .section-name',
            #     'new_author': '.author-string a',
            #     'new_body': '.entry-author a p',
            #     'new_image': '.entry-author a p',
            #     'new_source': '.entry-author a p',
            #     'author_name': '.entry-author a p',
            #     'author_email': '.entry-author a p',
            #     'author_site': '.entry-author a p',
            #     'author_image': '.entry-author a p',
            # },
        #}

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
            r = requests.get(f"{self.api_url}/media/site/{site}", timeout=0.5)
            site = r.json()
        except requests.exceptions.RequestException as e:
            site = self.media[site]
        except Exception as e:
            print('Sitio no encontrado.')
            raise Exception('Sitio no encontrado.!')
        return site

    def get_authors(self, site):
        r = requests.get(f"{self.api_url}/media/site/{site}/author", timeout=0.5)
        return r.json()

    def get_news(self, site):
        r = requests.get(f"{self.api_url}/media/site/{site}/news", timeout=0.5)
        return r.json()


class ScrAPIFieldsLocal(ScrAPIFields):
    def __init__(self):
        self.media = {
            'clarin': {
                'pretty_name': 'Clarín',
                'base_url': 'https://www.clarin.com/',
                'front_links': 'article a',
                'front_container': 'article',
                'front_container_title': 'h2',
                'front_container_section': 'p.name.name-section',
                'front_container_author': 'p.name.name-author',
                'front_container_link': 'a',
                'site_image': '.content-nota a',
                'site_section': 'nav ul li a',
                'noticias_id': [],
                'noticias_full': {},
                'new_wrapper': '#NewsContainer .StoryTextContainer p',
                'new_pretitle': '',
                'new_title': '.storyTitle',
                'new_subtitle': '.storySummary',
                'new_date': '.createDate',
                'new_category': 'a.SectionSeparator',
                'new_author': 'article#StoryBody div.author-info div',
                'new_body': '.StoryTextContainer p',
                'new_image': '.image-container img',
                'new_source': 'article#StoryBody',
                'author_name': 'article#StoryBody div.author-info div',
                'author_email': '',
                'author_site': '',
                'author_image': 'article#StoryBody div.author-info img',
            },
            'pagina12': {
                'pretty_name': 'Página 12',
                'base_url': 'https://www.pagina12.com.ar/',
                'front_links': '.article-title a',
                'front_container': '.block-content',
                'front_container_title': '.article-title a',
                'front_container_section': '',
                'front_container_author': '.article-author .no-link',
                'front_container_link': '.article-title a',
                'site_image': '.content-nota a',
                'site_section': '.content-nota a',
                'noticias_id': [],
                'noticias_full': {},
                'new_wrapper': 'article.article-full.section .article-main-content .article-text',
                'new_pretitle': 'article.article-full.section .article-header h2.h4',
                'new_title': 'article.article-full.section .article-header h1',
                'new_subtitle': 'article.article-full.section .article-header h2.h3',
                'new_date': '.article-info .date time',
                'new_category': 'article.article-full.section .article-header h5.current-tag a',
                'new_author': 'article.article-full.section .author-inner',
                'new_body': 'article.article-full.section .article-main-content .article-text',
                'new_image': 'article.article-full.section .article-main-imag .image-wrapper img',
                'new_source': '',
                'author_name': '.entry-author a p',
                'author_email': '.entry-author a p',
                'author_site': '.entry-author a p',
                'author_image': '.entry-author a p',
            },
            'ambito': {
                'pretty_name': 'Ambito Financiero',
                'base_url': 'https://www.ambito.com/',
                'front_links': '.news-article__title a',
                'front_container': '.news-article__info-wrapper',
                'front_container_title': '.news-article__title a',
                'front_container_section': '',
                'front_container_author': '.news-article__journalist a',
                'front_container_link': '.news-article__title a',
                'site_image': '',
                'site_section': '',
                'noticias_id': [],
                'noticias_full': {},
                'new_wrapper': '.main-container.container.note article.article-body',
                'new_pretitle': '',
                'new_title': 'header.news-headline h1.news-headline__title',
                'new_subtitle': 'header.news-headline h2.news-headline__article-summary p',
                'new_date': 'header.news-headline span.news-headline__publication-date',
                'new_category': 'header.news-headline .news-headline__topic li:last-child a',
                'new_author': '.news-headline__author-name',
                'new_body': '.main-container.container.note article p',
                'new_image': '.entry-author a p',
                'new_source': '.entry-author a p',
                'author_name': '.entry-author a p',
                'author_email': '.entry-author a p',
                'author_site': '.entry-author a p',
                'author_image': '.entry-author a p',
            },
            # 'telam': {
            #     'pretty_name': 'Telam',
            #     'base_url': 'https://www.telam.com.ar/',
            #     'front_links': '.wrapper-sections .nota .content a',
            #     'front_container': '.nota .content',
            #     'front_container_title': 'a',
            #     'front_container_section': '',
            #     'front_container_author': '.author',
            #     'front_container_link': 'a',
            #     'site_image': '',
            #     'site_section': '',
            #     'noticias_id': [],
            #     'noticias_full': {},
            #     'new_wrapper': 'article.note-content div.wrapper-editable-content .paragraph',
            #     'new_pretitle': '.volanta',
            #     'new_title': 'h1',
            #     'new_subtitle': '',
            #     'new_date': '.wrapper-info-note .time',
            #     'new_category': 'article.note-content h2.module-title ',
            #     'new_author': 'article.main-container ',
            #     'new_body': 'article.note-content div.wrapper-editable-content .paragraph',
            #     'new_image': '.entry-author a p',
            #     'new_source': '.entry-author a p',
            #     'author_name': '.entry-author a p',
            #     'author_email': '.entry-author a p',
            #     'author_site': '.entry-author a p',
            #     'author_image': '.entry-author a p',
            # },
            'infobae': {
                'pretty_name': 'Infobae',
                'base_url': 'https://www.infobae.com/',
                'front_links': 'a.story-card-ctn',
                'front_container': '.default-chain-ctn, .three-elements-chain-item',
                'front_container_title': '.headline-link',
                'front_container_section': '',
                'front_container_author': '.story-card-author-name',
                'front_container_link': 'a.story-card-ctn',
                'site_image': '.logo-image',
                'site_section': '.content-nota a',
                'noticias_id': [],
                'noticias_full': {},
                'noticia_element_class': '.element-paragraph',
                'new_wrapper': 'article.article .body-article',
                'new_pretitle': 'h1#title',
                'new_title': 'h1.article-headline',
                'new_subtitle': 'h2.article-subheadline',
                'new_date': '.sharebar-article-date',
                'new_category': '.article-section-tag',
                'new_author': 'section.article-section .article-header a.author-name',
                'new_body': 'article.article .body-article',
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
                'front_links': 'article.ln-card .link.ln-link',
                'front_container': 'article.ln-card',
                'front_container_title': '.ln-text.title',
                'front_container_section': '',
                'front_container_author': 'span.text.ln-text.marquee strong',
                'front_container_link': '.link.ln-link',
                'site_image': '.content-nota a',
                'site_section': '.content-nota a',
                'noticias_id': [],
                'noticias_full': {},
                'new_wrapper': 'main#content .cuerpo__nota .com-paragraph',  # .com-paragraph',
                'new_pretitle': '',
                'new_title': 'h1.com-title',
                'new_subtitle': 'h2.com-subhead',
                'new_date': 'span.mod-date .com-date',
                'new_category': 'main#content nav a:last-child',
                'new_author': 'div.datos a',
                'new_body': 'main#content .cuerpo__nota .com-paragraph',
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
                'front_links': '.article-preview .content .title a',
                'front_container': '.article-preview .content',
                'front_container_title': '.article-preview .content .title p',
                'front_container_section': '.article-preview .content .category-title h4',
                'front_container_author': '.article-preview .content .author',
                'front_container_link': '.article-preview .content .title a',
                'site_image': '.content-nota a',
                'site_section': '.content-nota a',
                'noticias_id': [],
                'noticias_full': {},
                'new_wrapper': 'article.articulo-simple .article-body',
                'new_pretitle': '',
                'new_title': '.title h1',
                'new_subtitle': '.subtitle h3',
                'new_date': 'time',
                'new_category': '.categories',
                'new_author': 'author-info p',
                'new_body': '.article-body div',
                'new_image': '.article-main-image',
                'new_source': '',
                'author_name': '.entry-author a p',
                'author_email': '.entry-author a p',
                'author_site': '.entry-author a p',
                'author_image': '.entry-author a p',
            }
        }

    def get_sites(self):
        return {k:v['pretty_name'] for k,v in self.media.items()}

    def get_site(self, site):
        return self.media[site]

    def get_authors(self, site):
        r = requests.get(f"{self.api_url}/media/{site}/author", timeout=0.5)
        return r.json()

    def get_news(self, site):
        r = requests.get(f"{self.api_url}/media/{site}/news", timeout=0.5)
        return r.json()


class Medium:
    def __init__(self, url=None):
        if not url:
            self.scrapi_fields = ScrAPIFieldsLocal()
        else:
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
            site.noticias_db.append([noticia[0], noticia[1], noticia[2], noticia[3], site_name])
        site.retrieve_home_news()
        self.database.save_site(site)

    def update_news(self, site, noticia_id ):
        noticia = self.MEDIUM[site].get_new(noticia_id)
        self.database.update_new(
            site,
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

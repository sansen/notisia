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


"""Notis IA.

Usage:
  notisia.py update [<medium>]
  notisia.py list
  notisia.py show (<medium>)
  notisia.py save (<medium>)
  notisia.py load (<medium>) [--date=<date>] 
  notisia.py clear 
  notisia.py (-h | --help)
  notisia.py --version

Options:
  -h --help  Show this screen.
  --version  Show version.
  <medium>   Choose a medium:
             pagina12, infobae, clarin, lanacion, tiempo, cohete
"""
import re
import time
import dill
import pprint
import os.path
import requests

from datetime import date
from docopt import docopt
from bs4 import BeautifulSoup
from colorama import init, Fore, Back, Style


def callback_clarin(link, links):
    """Get news links from clarin.com portal."""
    if re.search(r"\.html$", link):
        links.append(link)


def callback_pagina12(link, links):
    """Get news links from pagina12.com portal."""
    if link.startswith('https://www.pagina12.com.ar/') \
       and not re.search(r"suplementos",link) \
       and not re.search(r"opinion",link):
        links.append(link)
        
FILENAME = str(date.today())
MEDIUM = {
    'cohete': {
        'source': 'cohete',
        'pretty_name': 'Cohete a la luna',
        'base_url': 'https://www.elcohetealaluna.com/',
        'front_links': 'article h2.title a',
        'callback': (lambda link, links: links.append(link)),
        'noticias_id': [],
        'noticias_full': {},
        'noticia_wrapper': 'article .single-post-content',
        'noticia_element_class': '',
        'noticia_title_class': 'article h1 .post-title',
        'noticia_author_class': 'article .post-author-name',
    },    
    'tiempo': {
        'source': 'tiempo',
        'pretty_name': 'Tiempo Argentino',
        'base_url': 'https://www.tiempoar.com.ar/',
        'front_links': '.card-body a',
        'callback': (lambda link, links: links.append(link)),
        'noticias_id': [],
        'noticias_full': {},
        'noticia_wrapper': 'article.art-complete div.body',
        'noticia_element_class': '',
        'noticia_title_class': 'h1.art-headline',
        'noticia_author_class': '.author-string a',
    },    
    'pagina12': {
        'source': 'pagina12',
        'pretty_name': 'Página 12',
        'base_url': 'https://www.pagina12.com.ar/',
        'front_links': '.article-title a',
        'callback': callback_pagina12,
        'noticias_id': [],
        'noticias_full': {},
        'noticia_wrapper': 'article .article-body .article-text',
        'noticia_element_class': '',
        'noticia_title_class': 'article .article-titles .article-title',
        'noticia_author_class': 'article .article-main-media-header .article-author a',
    },    
    'clarin': {
        'source': 'clarin',
        'pretty_name': 'Clarín',
        'base_url': 'https://www.clarin.com/',
        'front_links': '.content-nota a',
        'callback': callback_clarin,
        'noticias_id': [],
        'noticias_full': {},
        'noticia_wrapper': '.body-nota',
        'noticia_element_class': '',
        'noticia_title_class': 'h1#title',
        'noticia_author_class': '.entry-author a p',
    },
    'infobae': {
        'source': 'infobae',
        'pretty_name': 'Infobae',
        'base_url': 'https://www.infobae.com/',
        'front_links': '.headline a',
        'callback': (lambda link, links: links.append(link)),
        'noticias_id': [],
        'noticias_full': {},
        'noticia_wrapper': '.wrapper #article-content',
        'noticia_element_class': '.element-paragraph',
        'noticia_title_class': 'h1',
        'noticia_author_class': '.byline-author',
    },
    'lanacion': {
        'source': 'lanacion',
        'pretty_name': 'La Nación',
        'base_url': 'https://www.lanacion.com.ar/',
        'front_links': 'article a',
        'callback': (lambda link, links: links.append(link)),
        'noticias_id': [],
        'noticias_full': {},
        'noticia_wrapper': 'article #cuerpo',
        'noticia_element_class': '',        
        'noticia_title_class': 'h1.titulo',
        'noticia_author_class': 'div.datos a',
    },    
}


def medium_list():
    """Print list of media."""
    init()
    print(f"Avilable Mediums")
    for key, medium in MEDIUM.items():
        print(f"{Fore.YELLOW}* {medium['pretty_name']}: {Fore.MAGENTA}{key}")
    print()


def update(medium):
    """Update news databases."""
    update_source(medium)
    update_content(medium)


def update_source(medium):
    """Update news sources links."""
    if medium is not None:
        mediums = [ MEDIUM[medium] ]
    else:
        mediums = MEDIUM

    for medium in mediums:
        r = requests.get(medium['base_url'])
        portada = BeautifulSoup(r.text, 'html.parser')
        links = []

        links_noticias = portada.select(medium['front_links'])
        for l in links_noticias:
            l = l.get('href')
            if not l.startswith('https://') and \
               not l.startswith('http://'):
                l = medium['base_url'] + l
            medium['callback'](l, links)

        links = list(set(links))
        medium['noticias_id'].extend(links)
        medium['noticias_id'] = list(set(medium['noticias_id']))
        # print(MEDIUM)


def update_content(medium=None):
    """Update content of news."""
    if medium is not None:
        mediums = [ MEDIUM[medium] ]
    else:
        mediums = MEDIUM

    for medium in mediums:
        if len(medium['noticias_id']) == 0:
            update_source(medium)

        for noticia_url in medium['noticias_id']:
            if noticia_url in medium['noticias_full'].keys():
                continue
            
            r = requests.get(noticia_url)
            bs = BeautifulSoup(r.text, 'html.parser')

            # scrap body
            notice = ''
            notice_raw = bs.select(medium['noticia_wrapper'])
            for container in notice_raw:
                for item in container.children:
                    if item.name in ['p', 'h2', 'h3', 'h4'] \
                       and len(item.text) > 0 :
                        notice = notice + item.text.strip().strip('\r\n') + '\n'
                    elif item.name == 'div' \
                         and len(medium['noticia_element_class']) > 0:
                        item = item.select(medium['noticia_element_class'])
                        if len(item) > 0:
                            item = item[0]
                            notice = notice + item.text.strip().strip('\r\n') + ' '

            # scrap title
            title_raw = bs.select(medium['noticia_title_class'])
            title_raw = title_raw[0].text.upper() if len(title_raw) > 0 else ''

            # scrap author
            author_raw = bs.select(medium['noticia_author_class'])
            author_raw = author_raw[0].text if len(author_raw) > 0 \
                else medium['pretty_name']
    
            if noticia_url not in medium['noticias_full'].keys():
                medium['noticias_full'][noticia_url] = {
                    'title': title_raw,
                    'author': author_raw,
                    'body': notice,
                    'uri': noticia_url
                }
        # print(MEIDUM)


def show(medium):
    """Print news menu for particular media."""
    option_quit = False
    medium = MEDIUM[medium]

    while not option_quit:
        output_noticias(medium)
        number = int(
            input(Fore.YELLOW + 'Ingrese la notica a escupir. (0 Para salir): ')
        )
        if number == 0:
            option_quit = True
            continue

        number -= 1
        news = list(medium['noticias_full'].values())
        view_notice(news[number])
        input(Fore.YELLOW + 'Tecla para Continuar')



def load_from_pickle(FILENAME):
    """Load current date media from a pickle file."""
    global MEDIUM

    if os.path.isfile(FILENAME) and \
       not os.stat(FILENAME).st_size==0:
        with open(FILENAME, 'rb') as handle:
            MEDIUM = dill.load(handle)
            return True
    return False


def save_to_pickle(FILENAME):
    """Save current date media to pickle file."""
    with open(FILENAME, 'wb') as handle:
        dill.dump(MEDIUM, handle)
        return True
    return False


def view_notice(notice):
    """Print content for selected new."""
    init()
    print('----')
    print(f"{Fore.GREEN}{notice['title']}{Back.BLACK}{Fore.WHITE}")
    if notice['author']:
        print(f"{Back.BLUE}{Fore.WHITE}{notice['author']}{Back.BLACK}{Fore.WHITE}")
    print()
    print(f"{Style.DIM}{Back.BLACK}{Fore.WHITE}{notice['body']}")
    print(f"{Style.NORMAL}{Back.BLACK}")
    print(f"{Back.RED}{Fore.WHITE}{notice['uri']}{Back.BLACK}{Fore.WHITE}")
    print()
    

def output_mediums():
    """Print output media."""
    init()
    for i, medium in enumerate(MEDIUM):
        print(f"{Fore.YELLOW}{str(i+1)}- {medium['pretty_name']}")
    print()


def output_noticias(medium):
    """Print output for news menu."""
    init()
    for i, noticia in enumerate(medium['noticias_full'].values()):
        print(f"{Fore.YELLOW}{i+1:03}- {noticia['author']} :: {Fore.GREEN}{noticia['title']}")
    print()


def metrics_word_freq(news_content):
    """Compute word Frequency of new."""
    word_freq = {}
    words = news_content.split(' ')

    for word in words:
        word = word.lower().strip().strip(',.\n\r')
        if word not in word_freq.keys():
            word_freq[word] = 1
        else:
            word_freq[word] += 1


def clear_mediums():
    """Clear media sources and content."""
    for medium in MEDIUM.values():
        medium['noticias_id'] = []
        medium['noticias_full'] = {}        

        
if __name__ == '__main__':
    arguments = docopt(__doc__, version='Notis pre-alpha 1.0')
    # print(arguments)

    if arguments['<medium>'] is not None:
        if arguments['<medium>'] not in MEDIUM.keys():
            exit()
        else:
            medium = arguments['<medium>']
    else:
        medium = None
            
    if arguments['list']:
        list_medium()
    elif arguments['clear']:
        load_from_pickle(FILENAME)
        clear_mediums()
        save_to_pickle(FILENAME)
    elif arguments['update']:
        load_from_pickle(FILENAME)
        update(medium)
        save_to_pickle(FILENAME)
    elif arguments['show']:
        if load_from_pickle(FILENAME): 
            show(medium)
        else:
            update(medium)
            show(medium)

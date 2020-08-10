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
  notisia.py url (<url>)
  notisia.py clear
  notisia.py (-h | --help)
  notisia.py --version

Options:
  -h --help  Show this screen.
  --version  Show version.
  <medium>   Choose a medium:
             pagina12, infobae, clarin, lanacion, tiempo, cohete
"""
import requests

from datetime import date
from docopt import docopt

from src import sites
from src.stats import Stats
from src.database import Database


class ScrAPIFields:
    def __init__(self, url):
        self.api_url = url

    def get_site(self, site):
        r = requests.get(f"{self.api_url}/media/{site}")
        return r.json()

    def get_authors(self, site):
        r = requests.get(f"{self.api_url}/media/{site}/author")
        return r.json()

    def get_news(self, site):
        r = requests.get(f"{self.api_url}/media/{site}/news")
        return r.json()


class Medium:
    def __init__(self, url):
        self.scrapi_fields = ScrAPIFields(url)
        self.MEDIUM = {
            'telam': 'Agencia Telam',
            'cohete': 'El Cohete a la Luna',
            'clarin': 'Clarin',
            'infobae': 'Infobae',
            'pagina12': 'Pagina 12',
            'tiempoar': 'Tiempo Argentino',
            'lanacion': 'La Nacion',
        }
        self.database = Database()
        self.stats = Stats()

    def run(self, site_name):
        # site = Site(site_name, self.scrapi_fields)
        site = sites.SiteFactory.getSiteInstance(
            site_name, self.scrapi_fields
        )
        self.MEDIUM[site_name] = site

        for noticia in self.database.select_noticias_id(site_name):
            site.noticias_db.append([noticia[0], noticia[1]])
        site.retrieve_home_news()
        self.database.save_site(site)
        return site


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Notis pre-alpha 1.0')

    SCRAPI_URL = arguments['<url>']
    m = Medium(SCRAPI_URL)

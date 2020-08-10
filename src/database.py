import time
import sqlite3

from datetime import date

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('example.db')
        self._create_tables()

    def _create_tables(self):
        # Create table
        self.conn.execute(
            'CREATE TABLE IF NOT EXISTS noticias ' +
            '(noticia_id text PRIMARY KEY, ' +
            'title text, body text, media text, fecha text)'
        )
        # Save (commit) the changes
        self.conn.commit()

    def save_site(self, site):
        inserts = []
        for noticia in site.noticias_id:
            inserts.append((noticia, site.site, time.time()))

        # Create table
        self.conn.executemany(
            'INSERT INTO noticias ' +
            '(noticia_id, media, fecha) ' +
            'VALUES (?, ?, ?)', inserts
        )
        # Save (commit) the changes
        self.conn.commit()

    def select_noticias_id(self, site):
        # Create table
        noticias = self.conn.execute(
            'SELECT noticia_id, fecha FROM noticias where media = ?', (site,)
        )
        return noticias

    def close_connection(self):
        # We can also close the connection if we are done with it.
        # Just be sure any changes have been committed or they will be lost.
        self.conn.close()

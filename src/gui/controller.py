# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2019-2020 Santiago Torres Batan

class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.init()

    def init(self):
        self.view.set_items(self.model.MEDIUM)
        self.view.section_selection_signal.connect(
            self.section_selection
        )
        self.view.action_signal.connect(self.action)
        self.view.search_signal.connect(self.search)
        self.download_thread = None

    def section_selection(self):
        sites = list(self.model.MEDIUM.keys())
        site_name = sites[self.view.cb.currentIndex()]
        site = self.model.run(site_name)
        self.view.build_tree(site.noticias_db, site_name, reset=True)

    def action(self):
        item, media, new_id = self.view.news_id
        # media = list(self.model.MEDIUM.keys())[media]

        self.model.run(media)
        self.model.MEDIUM[media].retrieve_news(new_id)
        self.model.update_news(media, new_id)
        self.model.stats.run(
            self.model.MEDIUM[media].noticias[new_id]
        )
        self.view.fill_news_pane(
            self.model.MEDIUM[media].noticias[new_id]
        )
        self.view.fill_stats_pane(
            self.model.MEDIUM[media].noticias[new_id]
        )

    def search(self):
        query = self.view.search.toPlainText()
        if len(query) < 3:
            return
        notices = self.model.search(query)
        self.view.build_tree(notices, reset=True)

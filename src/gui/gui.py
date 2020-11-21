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

import sys
from itertools import islice
from datetime import datetime

from PySide2 import QtWidgets, QtCore


class Window(QtWidgets.QMainWindow):
    search_signal = QtCore.Signal()
    action_signal = QtCore.Signal()
    section_selection_signal = QtCore.Signal()

    def __init__(self, parent=None):
        super(Window, self).__init__(parent=parent)

        width = 1024
        height = 680

        title = "NotisIA"
        self.setWindowTitle(title)

        self.setMinimumSize(QtCore.QSize(width, height))
        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QtWidgets.QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.cb = QtWidgets.QComboBox()
        self.cb.currentIndexChanged.connect(self.section_selection_signal)
        self.layout.addWidget(self.cb)

        self.widget1 = QtWidgets.QWidget()
        self.widget1.setFixedHeight(50)
        self.bar = QtWidgets.QHBoxLayout()
        self.widget1.setLayout(self.bar)

        self.layout.addWidget(self.widget1)

        self.bar.addWidget(QtWidgets.QLabel("Buscar:"))
        self.search = QtWidgets.QTextEdit()
        #self.search = QtWidgets.QLineEdit()
        self.bar.addWidget(self.search)
        self.search.textChanged.connect(self.search_signal)
        # self.ok_button.clicked.connect


        self.treewidget = QtWidgets.QTreeWidget()
        self.treewidget.setColumnCount(2)
        self.treewidget.setHeaderLabels(
            ['Noticia', 'Fecha', 'Sitio']
        )
        self.treewidget.itemClicked.connect(self.on_item_clicked)
        self.treewidget.itemClicked.connect(self.action_signal)
        self.treewidget.setSortingEnabled(True)
        self.treewidget.setFixedHeight(150)

        self.layout.addWidget(self.treewidget)

        self.hwidget = QtWidgets.QWidget(self)
        self.hlayout = QtWidgets.QHBoxLayout()
        self.hwidget.setLayout(self.hlayout)
        self.layout.addWidget(self.hwidget)

        self.vwidget = QtWidgets.QWidget(self)
        self.vlayout = QtWidgets.QVBoxLayout()
        self.vwidget.setLayout(self.vlayout)
        #self.vlayout.addWidget(self.treewidget)

        self.sidepane1 = QtWidgets.QTextEdit("Selecciona una noticia.")
        self.sidepane1.setReadOnly(True)
        self.sidepane1.setFixedWidth(250)

        #self.hlayout.addWidget(self.vwidget)

        self.sidepane = QtWidgets.QTextEdit("Selecciona una noticia.")
        self.sidepane.setReadOnly(True)
        self.sidepane.setStyleSheet(
            "QTextEdit {background-color: #f4ECD8; color: #5b4636 }"
        )
        self.hlayout.addWidget(self.sidepane)
        self.hlayout.addWidget(self.sidepane1)

        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        self.tray_icon.setIcon(
            self.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon)
        )
        self.tray_icon.activated.connect(self.system_icon)

        menu = QtWidgets.QMenu()
        exitAction = menu.addAction("Exit")
        exitAction.triggered.connect(sys.exit)
        self.tray_icon.setContextMenu(menu)

        self.tray_icon.show()
        self.show()

    def on_item_clicked(self, it, col):
        self.currentItem = it
        self.news_id = (it, it.text(2), it.text(0))
        
    def set_items(self, items):
        self.cb.addItems([i for i in items.values()])

    def build_tree(self, noticias, site_name=None, reset=False):
        if reset:
            self.treewidget.clear()

        for link in noticias:
            try:
                time = datetime.utcfromtimestamp(
                    int(float(link[1]))).strftime('%d-%m-%Y'
                )
            except Exception:
                time = link[1]
            item = QtWidgets.QTreeWidgetItem(self.treewidget)
            item.setText(0, f"{link[0]}")
            item.setText(1, f"{time}")
            item.setToolTip(0, f"{link[0]}")
            item.setToolTip(1, f"{time}")

            if site_name != None:
                item.setText(2, f"{site_name}")
                item.setToolTip(2, f"{site_name}")
            else:
                item.setText(2, f"{link[2]}")
                item.setToolTip(2, f"{link[2]}")

        header = self.treewidget.header()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setStretchLastSection(False)
        self.treewidget.sortItems(1, QtCore.Qt.DescendingOrder)

    def fill_news_pane(self, noticia):
        self.sidepane.setText(f"{noticia['title']}\n\n{noticia['body']}")

    def fill_stats_pane(self, noticia):
        text = f"Categoria: {noticia['category']}\n"
        text += f"Autor: {noticia['author']}\n"
        text += f"Fecha: {noticia['date'].strip()}\n\n"
        text += f"Cantidad de Palabras: {noticia['word_count']}\n"
        text += f"Cantidad de Oraciones: {noticia['sentences']}\n"
        text += f"Cantidad de Parrafors: {noticia['paragraphs']}\n\n"
        text += f"Frecuencias de Palabras:\n"

        tmp_dict = {k: v for k, v in sorted(
            noticia['word_freq'].items(),
            key=lambda item: item[1],
            reverse=True)
        }
        n_items = islice(tmp_dict.items(), 15)
        for w, f in n_items:
            # text += f"{w.upper()}: {'+'*f}  | "
            text += f"{w.upper()}: #{f}\n"
        self.sidepane1.setText(text)

    def build_sub_tree(self, parent_item, noticia, reset=False):
        item = QtWidgets.QTreeWidgetItem(parent_item)
        item.setText(0, f"{noticia['title']}\n\n{noticia['body']}")
        item.setToolTip(0,
            f"{noticia['category']} - {noticia['author']} - {noticia['date']}"
        )

    def system_icon(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.Trigger:
            self.show()

    # Override closeEvent, to intercept the window closing event
    # The window will be closed only if there is no check mark in the check box
    def closeEvent(self, event):
        event.ignore()
        self.hide()


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = Window()
    window.show()
    app.exec_()

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

"""Notis IA.

Usage:
  notisia.py [--webscrapi <url>]
  notisia.py (-h | --help)
  notisia.py --version
"""

from src.gui import gui
from src.gui import controller
from src.model import notisia

import sys
from docopt import docopt
from PySide2 import QtWidgets


def main(url):
    app = QtWidgets.QApplication([])
    window = gui.Window()

    view = window
    model = notisia.Medium(url)
    c = controller.Controller(model=model, view=view)
    sys.exit(app.exec_())


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Notis pre-alpha 1.0')
    print(arguments)

    if arguments['--webscrapi'] is not None:
        url = arguments['<url>']
    else:
        url = None
        print('Error en la conexion. Utilizando sistema degrado')
    main(url)
        

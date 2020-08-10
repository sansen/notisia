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
# For further info, check  https://launchpad.net/encuentro
#
# Copyright 2019 Santiago Torres Batan

from gui import gui
from gui import controller
from src import notisia

import sys
from docopt import docopt
from PySide2 import QtWidgets


def main():
    app = QtWidgets.QApplication([])
    window = gui.Window()

    view = window
    model = notisia.Medium('http://127.0.0.1:8000')
    c = controller.Controller(model=model, view=view)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

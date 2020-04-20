#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtWidgets import QFileDialog
import os
from itertools import zip_longest
from descriptor import RGBHistogram
import pickle
import math
import sys
import cv2



IMAGES_FORMAT = ('.png', '.jpg', '.bmp', '.jpeg')


class Overlay(QtWidgets.QWidget):

    def __init__(self, parent=None):

        QtWidgets.QWidget.__init__(self, parent)
        palette = QtGui.QPalette(self.palette())
        palette.setColor(palette.Background, QtCore.Qt.transparent)
        self.setPalette(palette)

    def paintEvent(self, event):

        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.fillRect(
            event.rect(), QtGui.QBrush(QtGui.QColor(255, 255, 255, 127))
        )
        painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))

        for i in range(6):
            if (self.counter / 5) % 6 == i:
                painter.setBrush(
                    QtGui.QBrush(
                        QtGui.QColor(127 + (self.counter % 5)*32, 127, 127)
                    )
                )
            else:
                painter.setBrush(QtGui.QBrush(QtGui.QColor(127, 127, 127)))
            painter.drawEllipse(
                self.width()/2 + 30 * math.cos(2 * math.pi * i / 6.0) - 10,
                self.height()/2 + 30 * math.sin(2 * math.pi * i / 6.0) - 10,
                20, 20)

        painter.end()

    def showEvent(self, event):

        self.timer = self.startTimer(50)
        self.counter = 0

    def timerEvent(self, event):

        self.counter += 1
        self.update()
        if self.counter == 60:
            self.killTimer(self.timer)
            self.hide()


def clickable(widget):

    class Filter(QtCore.QObject):

        clicked = QtCore.pyqtSignal()

        def eventFilter(self, obj, event):

            if obj == widget:
                if event.type() == QtCore.QEvent.MouseButtonRelease:
                    if obj.rect().contains(event.pos()):
                        self.clicked.emit()
                        # The developer can opt for .emit(obj) to get the
                        # object within the slot.
                        return True

            return False

    filter = Filter(widget)
    widget.installEventFilter(filter)
    return filter.clicked


class Thumbnail(QtWidgets.QWidget):

    def __init__(self, images=None, columns=5):
        if images is None:
            images = []
        self.images = images
        self.columns = columns
        super(Thumbnail, self).__init__()
        self.grid = None
        self.initUI()

    def initUI(self):

        self.grid = QtWidgets.QGridLayout()
        self.setLayout(self.grid)

        nb_lines = len(list(zip_longest(*([iter(self.images)]*self.columns))))

        if len(self.images) < self.columns:
            columns = len(self.images)
        else:
            columns = self.columns

        positions = [
            (i, j) for i in range(nb_lines) for j in range(columns)
        ]

        for position, name in zip(positions, self.images):

            if name is None:
                break

            label = QtGui.QLabel(name)
            myPixmap = QtGui.QPixmap(name)
            w = self.width() / columns
            myScaledPixmap = myPixmap.scaledToWidth(w)
            label.setPixmap(myScaledPixmap)
            clickable(label).connect(show_text(name))
            self.grid.addWidget(label, *position)

    def update(self, images):
        self.images = images

        if len(self.images) < self.columns:
            columns = len(self.images)
        else:
            columns = self.columns
        for i in reversed(range(self.grid.count())):
            self.grid.itemAt(i).widget().setParent(None)
        nb_lines = len(list(zip_longest(*([iter(self.images)]*columns))))

        positions = [
            (i, j) for i in range(nb_lines) for j in range(columns)
        ]

        for position, name in zip(positions, self.images):

            if name is None:
                break

            label = QtWidgets.QLabel(name)
            myPixmap = QtGui.QPixmap(name)
            w = self.width() / columns
            myScaledPixmap = myPixmap.scaledToWidth(w)
            label.setPixmap(myScaledPixmap)
            clickable(label).connect(show_text(name))
            self.grid.addWidget(label, *position)


def show_text(name):
    def f():
        print(name)
    return f


class IndexerGui(QtWidgets.QDialog):
    def __init__(self):
        super(IndexerGui, self).__init__()
        self.initUI()

    def initUI(self):

        self.images = []
        self.thumnails = Thumbnail(self.images)
        scroll = QtWidgets.QScrollArea()
        scroll.setWidget(self.thumnails)
        scroll.setWidgetResizable(True)
        layout = QtWidgets.QVBoxLayout()
        btn_layout = QtWidgets.QHBoxLayout()
        layout.addWidget(scroll)
        btn_browse_dir = QtWidgets.QPushButton('Select Directory')
        btn_browse_imgs = QtWidgets.QPushButton('Select Images')
        self.index_images = QtWidgets.QPushButton('Index Images')
        self.index_images.setEnabled(False)
        btn_layout.addWidget(btn_browse_dir)
        btn_layout.addWidget(btn_browse_imgs)
        layout.addLayout(btn_layout)
        layout.addWidget(self.index_images)
        self.setLayout(layout)

        self.overlay = Overlay(self)
        self.overlay.hide()

        btn_browse_dir.clicked.connect(self.directory_browse)
        btn_browse_imgs.clicked.connect(self.browse_images)
        self.index_images.clicked.connect(self.index_imgs)

        self.resize(725, 400)
        self.setWindowTitle('Indexer')

    def directory_browse(self):

        path = QtWidgets.QFileDialog.getExistingDirectory(
            self, 'Select Directory'
        )
        if not path:
            return
        self.images = [
            os.path.join(path, x) for x in os.listdir(path)
            if any(x.endswith(f) for f in IMAGES_FORMAT)
        ]
        self.thumnails.update(self.images)
        if self.images:
            self.index_images.setEnabled(True)

    def browse_images(self):

        'Images (*.png *.xpm *.jpg)'
        filter_image = 'Images (%s)' % ' '.join(
            ['*' + x for x in IMAGES_FORMAT]
        )
        self.images,_ = QFileDialog.getOpenFileNames(
            self, 'Select Images', os.getenv('HOME'), filter_image
        )

        self.thumnails.update(self.images)
        if self.images:
            self.index_images.setEnabled(True)

    def index_imgs(self):
        self.index_images.setEnabled(False)
        if not self.images:
            QtGui.QMessageBox.critical(
                self, 'Selection error', 'No image selected'
            )
            return

        self.overlay.show()
        index = {}

        # initialize our image descriptor -- a 3D RGB histogram with
        # 8 bins per channel
        desc = RGBHistogram([8, 8, 8], 5)

        # use glob to grab the image paths and loop over them
        for imagePath in self.images:

            # load the image, describe it using our RGB histogram
            # descriptor, and update the index
            image = cv2.imread(imagePath)
            features = desc.describe(image)
            index[imagePath] = features

        # we are now done indexing our image -- now we can write our
        # index to disk
        filename = 'index.pkl'
        with open(filename, 'wb') as handle:
            pickle.dump(index, handle)
        self.overlay.hide()
        QtWidgets.QMessageBox.information(
            self, 'Indexing complete', '%s images indexed. Indexed file saves as %s' % (
                len(self.images), filename
            )
        )


def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = IndexerGui()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

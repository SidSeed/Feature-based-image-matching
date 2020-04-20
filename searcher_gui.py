# -*- coding: utf-8 -*-


from descriptor import RGBHistogram
from searcher import Searcher
import pickle
import cv2
from indexer_gui import IndexerGui, Thumbnail
from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication,QFileDialog
from PyQt5.QtCore import *
import os
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig)


class Ui_MainWindow(object):
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        self.filename = ""
        self.indexer = IndexerGui()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(440, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.formLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))

        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.formLayout.addWidget(self.pushButton)

        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setObjectName(_fromUtf8("pushButton_3"))
        self.formLayout.addWidget(self.pushButton_3)
        self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_4.setObjectName(_fromUtf8("pushButton_4"))
        self.formLayout.addWidget(self.pushButton_4)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.addWidget(self.label)

        lbl_results = QtWidgets.QLabel("Results:")
        self.formLayout.addWidget(lbl_results)
        self.formLayout.addWidget(lbl_results)

        self.thumbnail = Thumbnail(columns=2)
        self.thumbnail.setObjectName(_fromUtf8("thumbnail"))
        scroll = QtWidgets.QScrollArea()
        scroll.setWidget(self.thumbnail)
        scroll.setWidgetResizable(True)
        self.formLayout.addWidget(scroll)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def folderbrowse(self):

        directory = QtGui.QFileDialog.getExistingDirectory(
            self, "Pick a folder"
        )
        if directory:
            for file_name in os.listdir(directory):
                print("image name: "+file_name)

    def singlebrowse(self):

        self.filename, _ = QFileDialog.getOpenFileName(
            None, 'Open image: ', os.getenv('HOME'), '*.png'
        )

        myPixmap = QtGui.QPixmap(_fromUtf8(self.filename))
        myScaledPixmap = myPixmap.scaledToWidth(
            self.pushButton_3.size().width()
        )
        self.label.setPixmap(myScaledPixmap)

    def recognize(self):
        if not self.filename:
            QtWidgets.QMessageBox.critical(
                self.centralwidget, 'Selection error', 'You have to load a query image !'
            )
            return None
        queryImage = cv2.imread(self.filename)
        desc = RGBHistogram([8, 8, 8], 5)
        queryFeatures = desc.describe(queryImage)

        # load the index perform the search
        if not os.path.exists("index.pkl"):
            QtWidgets.QMessageBox.critical(
                self.centralwidget, 'Indexing error', 'You have to Index the images features from the dataset !'
            )
            self.open_indexer()
            return None
        with open("index.pkl", 'rb') as handle:
            index = pickle.load(handle)
        searcher = Searcher(index)
        results = searcher.search(queryFeatures)
        
        # loop over the top ten results
        images = [x[1] for x in results][:10]
        self.thumbnail.update(images)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            _translate("MainWindow", "Feature based image matching", None)
        )
        self.pushButton.setText(
            _translate("MainWindow", "Load Image query", None)
        )
        self.pushButton_3.setText(
            _translate("MainWindow", "Index Images Features", None)
        )
        self.pushButton_4.setText(
            _translate("MainWindow", "Recognize", None)
        )

        self.pushButton.clicked.connect(self.singlebrowse)
        self.pushButton_4.clicked.connect(self.recognize)
        self.pushButton_3.clicked.connect(self.open_indexer)

    def open_indexer(self):
        self.indexer.exec_()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    MainWindow.show()
    sys.exit(app.exec_())
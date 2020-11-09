from PyQt5 import QtWidgets,  QtCore, QtGui, uic#uic, QtCompat,  QtUiTools

import sys
import os
from functools import partial

from image_process.background_remove import BackgroundRemoval

cur_dir = os.path.dirname(os.path.dirname(__file__))
UI = os.path.join(cur_dir, 'ui', 'main_ui.ui')


class ImageViewerUi(QtWidgets.QWidget):
    def __init__(self):
        super(ImageViewerUi, self).__init__()
        # self.ui = QtCompat.loadUi(UI, self)
        self.ui = uic.loadUi(UI, self)
        # self.ui = self.loadUiWidget(UI, parent=self)
        self.image_file = None
        self.band = None
        self.view = Viewer()
        self._initialize()
        self.connections()

    def _initialize(self):
        self.ui.remove_bg_wd.hide()
        self.ui.img_option_wd.hide()
        self.ui.zoom_frm_wd.hide()
        self.apply_crop_pb.hide()

    def connections(self):
        self.ui.load_img_pb.clicked.connect(self.load_image)
        self.ui.crop_pb.clicked.connect(self.handle_crop)
        self.ui.resize_pb.clicked.connect(self.resize_wd_)
        self.ui.resize_apply_pb.clicked.connect(self.apply_resize)
        self.ui.resize_undo_pb.clicked.connect(self.undo_resize)
        self.apply_crop_pb.clicked.connect(self.save_img)
        self.ui.zoom_in_pb.clicked.connect(self.view.zoomIn)
        self.ui.zoom_out_pb.clicked.connect(self.view.zoomOut)
        self.ui.reset_zoom_pb.clicked.connect(self.view.resetZoom)
        self.ui.fit_to_screen_pb.clicked.connect(self.view.fitToWindow)
        self.ui.r_bg_pb.clicked.connect(self.remove_bg_options)
        self.ui.white_bg_pb.clicked.connect(partial(self.remove_bg, bg='white'))
        self.ui.black_bg_pb.clicked.connect(partial(self.remove_bg, bg='black'))
        self.ui.mask_red_pb.clicked.connect(partial(self.remove_bg, bg='red'))
        self.ui.mask_grey_pb.clicked.connect(partial(self.remove_bg, bg='grey'))
        self.ui.save_bg_pb.clicked.connect(self.save_bg)
        self.ui.save_resize_pb.clicked.connect(self.save_resize)

    def remove_bg_options(self):
        if self.ui.remove_bg_wd.isHidden():
            self.ui.remove_bg_wd.show()
        else:
            self.ui.remove_bg_wd.hide()

    def load_image(self):
        self.pixmap = self.open_browser()
        if self.pixmap:
            self.ui.img_lay.addWidget(self.view)
            self.view.setPixmap(self.pixmap)
            if self.ui.zoom_frm_wd.isHidden():
                self.ui.zoom_frm_wd.show()
            print (self.pixmap)
        # self.ui.img_lbl.setScaledContents(True)
        # self.ui.img_lbl.setPixmap(self.pixmap)

    def open_browser(self):
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFilter(dialog.filter() | QtCore.QDir.Hidden)
        dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
        dialog.setNameFilters(["Images (*.png *.jpeg *.jpg *.bmp *.gif)"])
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            fileName = (dialog.selectedFiles())[0]
            print (">>>", fileName)
            pixmap = QtGui.QPixmap(fileName)
            print('LLL', pixmap)
            if pixmap.isNull():
                QtWidgets.QMessageBox.information(
                    self, "Image Viewer", "Cannot load %s." % fileName)
                return
            self.image_file = fileName
            return pixmap


    def handle_crop(self):
        if self.ui.img_option_wd.isHidden():
            self.ui.img_option_wd.show()
            self.ui.resize_wd.hide()

        self.apply_crop_pb.show()
        if not self.band:
            self.band = Crop(self.view)
            self.band.setGeometry(0, 0, 150, 150)

    def save_img(self):
        x = self.band.pos().x()
        y = self.band.pos().y()
        w = self.band._band.size().height()
        h = self.band._band.size().width()
        rect = QtCore.QRect(QtCore.QPoint(x, y), QtCore.QSize(w, h))
        crop_pixmap = self.pixmap.copy(rect)
        print (">>>>>>>>>>>>>>", rect)
        # crop_pixmap.save(r'A:\workspace\demo\image_process\source\test\input_img\output.png')
        label = QtWidgets.QLabel(pixmap=crop_pixmap)
        button = QtWidgets.QPushButton('Save')
        button.clicked.connect(partial(self.save_crop_image, filename=crop_pixmap))
        dialog = QtWidgets.QDialog(self)
        lay = QtWidgets.QVBoxLayout(dialog)
        lay.addWidget(label)
        lay.addWidget(button)
        dialog.exec_()

    def save_crop_image(self, filename=None):
        file_name_path = self.view.open_file_browser()
        filename.save(file_name_path)
        self.band.hide()
        self.apply_crop_pb.hide()

    def resize_wd_(self):
        if self.ui.img_option_wd.isHidden() and self.pixmap:
            self.ui.img_option_wd.show()
            self.ui.resize_wd.show()
            w_size = self.pixmap.size().width()
            h_size = self.pixmap.size().height()
            self.ui.og_width.setText('Original Width {}'.format(w_size))
            self.ui.og_hight.setText('Original Height {}'.format(h_size))
        else:
            self.ui.img_option_wd.hide()

    def apply_resize(self):
        w_size = self.pixmap.size().width()
        h_size = self.pixmap.size().height()
        width = self.ui.width_le.text()
        hight = self.ui.hight_le.text()
        self.resized_pixmap = self.pixmap.scaled(int(width), int(hight), QtCore.Qt.KeepAspectRatio)
        self.view.setPixmap(self.resized_pixmap)

    def save_resize(self):
        file_path = self.view.open_file_browser()
        if not self.resized_pixmap.isNull():
            self.resized_pixmap.save(file_path)

    def undo_resize(self):
        self.view.setPixmap(self.pixmap)
        self.resized_pixmap = None

    def remove_bg(self, bg=None):
        temp_dir = os.path.join(os.path.dirname(cur_dir), 'temp')
        self.image_file = self.image_file.replace('/', '\\')
        self.bg = BackgroundRemoval(image_file=self.image_file)
        if bg in ('red', 'grey'):
            if bg == 'red':
                self.bg.masked_bg(colour=True)
                out = os.path.join(temp_dir, 'temp_color_img.png')
            else:
                self.bg.masked_bg()
                out = os.path.join(temp_dir, 'temp_grey_img.png')
        else:
            if bg == 'white':
                out = self.bg.white_bg()
            else:
                out = self.bg.black_bg()

        self.bg_pixmap = QtGui.QPixmap(out)
        self.view.setPixmap(self.bg_pixmap)

    def save_bg(self):
        file_path = self.view.open_file_browser()
        self.bg_pixmap.save(file_path)


class Crop(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Crop, self).__init__(parent)

        self.draggable = True
        self.dragging_threshold = 5
        self.mousePressPos = None
        self.mouseMovePos = None
        self.borderRadius = 5

        self.setWindowFlags(QtCore.Qt.SubWindow)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(
            QtWidgets.QSizeGrip(self), 0,
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        layout.addWidget(
            QtWidgets.QSizeGrip(self), 0,
            QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
        self._band = QtWidgets.QRubberBand(
            QtWidgets.QRubberBand.Rectangle, self)
        self._band.show()
        self.show()

    def resizeEvent(self, event):
        self._band.resize(self.size())

    def paintEvent(self, event):
        # Get current window size
        window_size = self.size()
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setRenderHint(QtGui.QPainter.Antialiasing, True)
        qp.drawRoundedRect(0, 0, window_size.width(), window_size.height(),
                           self.borderRadius, self.borderRadius)
        qp.end()

    def mousePressEvent(self, event):
        if self.draggable and event.button() == QtCore.Qt.RightButton:
            self.mousePressPos = event.globalPos()                # global
            self.mouseMovePos = event.globalPos() - self.pos()    # local
        super(Crop, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.draggable and event.buttons() & QtCore.Qt.RightButton:
            globalPos = event.globalPos()
            moved = globalPos - self.mousePressPos
            if moved.manhattanLength() > self.dragging_threshold:
                # Move when user drag window more than dragging_threshold
                diff = globalPos - self.mouseMovePos
                self.move(diff)
                self.mouseMovePos = globalPos - self.pos()
        super(Crop, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.mousePressPos is not None:
            if event.button() == QtCore.Qt.RightButton:
                moved = event.globalPos() - self.mousePressPos
                if moved.manhattanLength() > self.dragging_threshold:
                    # Do not call click event or so on
                    event.ignore()
                self.mousePressPos = None
        super(Crop, self).mouseReleaseEvent(event)


class Viewer(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(QtWidgets.QGraphicsScene(), parent)
        # self.scene = QtWidgets.QGraphicsScene()
        self.pixmap_item = self.scene().addPixmap(QtGui.QPixmap())
        self.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.setBackgroundRole(QtGui.QPalette.Dark)
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self.rubberBandChanged.connect(self.onRubberBandChanged)

        self.last_rect = QtCore.QPointF()

    def setPixmap(self, pixmap):
        self.pixmap_item.setPixmap(pixmap)

    def zoomIn(self):
        self.scale(1.25, 1.25)

    def zoomOut(self):
        self.scale(0.8, 0.8)

    def resetZoom(self):
        self.resetTransform()

    def fitToWindow(self):
        self.fitInView(self.pixmap_item)

    @QtCore.pyqtSlot(QtCore.QRect, QtCore.QPointF, QtCore.QPointF)
    def onRubberBandChanged(self, rubberBandRect, fromScenePoint, toScenePoint):
        if rubberBandRect.isNull():
            pixmap = self.pixmap_item.pixmap()
            rect = self.pixmap_item.mapFromScene(self.last_rect).boundingRect().toRect()
            if not rect.intersected(pixmap.rect()).isNull():
                crop_pixmap = pixmap.copy(rect)
                button = QtWidgets.QPushButton('Save')
                button.clicked.connect(partial(self.save_crop_image, filename=crop_pixmap))
                label = QtWidgets.QLabel(pixmap=crop_pixmap)
                dialog = QtWidgets.QDialog(self)
                lay = QtWidgets.QVBoxLayout(dialog)
                lay.addWidget(label)
                lay.addWidget(button)
                dialog.exec_()
            self.last_rect = QtCore.QRectF()
        else:
            self.last_rect = QtCore.QRectF(fromScenePoint, toScenePoint)

    def save_crop_image(self, filename=None):
        file_name_path = self.open_file_browser()
        print("OOO filename", file_name_path, type(filename), type(file_name_path))
        filename.save(file_name_path)

    def open_file_browser(self):
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFilter(dialog.filter() | QtCore.QDir.Hidden)
        dialog.setDefaultSuffix('PNG')
        dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        dialog.setNameFilters(['PNG (*.PNG)'])
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            file_path_name = (dialog.selectedFiles())
            return file_path_name[0]


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    ocr = ImageViewerUi()
    ocr.show()
    sys.exit(app.exec_())
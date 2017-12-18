# -*- coding: utf-8 -*-

from copy import deepcopy
import glob
import os
from PySide import QtGui
import re
import shutil
import subprocess
import sys
import time
import win32api


import config
from hsaudiotag import auto
import qdarkstyle

from ui.movie_app_ui import Ui_Movie_app


class movie_app(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(movie_app, self).__init__(parent)
        self.ui = Ui_Movie_app()
        self.error = QtGui.QErrorMessage(self)
        self.ui.setupUi(self)
        # self.setStyleSheet(qdarkstyle.load_stylesheet())
        self.setup_connections()
        self.set_button_visibility()
        self.args = {}
        self.source = {}
        self.dest = {}
        self.recent_dict = {}
        self.valid_extensions = ['mp4', 'mov', 'txt']
        self.movie_progress = []
        self.cancel = False
        # self.config = config.load_config()
        # self.ui.log_list.setFont(
        #     QtGui.QFont("Courier New", 8, QtGui.QFont.Bold))
        # self.ui.line_drive_a.setText('C:\Users\paula\movies')
        # self.ui.line_inbox_a.setText('C:\Users\paula\movies\inbox')
        self.ui.line_drive_a.setText('E:\Movies')
        # self.ui.line_drive_b.setText('C:\Users\paula\moviesB')
        # self.ui.line_inbox_b.setText('C:\Users\paula\moviesB\inbox')
        # self.ui.line_drive_b.setText('D:\Movies')

    def setup_connections(self):
        self.ui.button_cancel.clicked.connect(self.cancel)
        self.ui.button_browse_a.clicked.connect(
            lambda: self.file_browser(drive='drive_a'))
        self.ui.button_browse_b.clicked.connect(
            lambda: self.file_browser(drive='drive_b'))
        self.ui.button_browse_a_inbox.clicked.connect(
            lambda: self.file_browser(drive='inbox_a'))
        self.ui.button_browse_b_inbox.clicked.connect(
            lambda: self.file_browser(drive='inbox_b'))

        self.ui.button_compare.clicked.connect(self.compare_drives)
        self.ui.button_list_all.clicked.connect(
            lambda: self.toggle_lists('all'))
        self.ui.button_list_unique.clicked.connect(
            lambda: self.toggle_lists('unique'))
        self.ui.button_rename_a.clicked.connect(
            lambda: self.rename_files(file_list='a'))
        self.ui.button_rename_b.clicked.connect(
            lambda: self.rename_files(file_list='b'))
        self.ui.button_copy_ab.clicked.connect(
            lambda: self.copy_files(copy_files='a'))
        self.ui.button_copy_ba.clicked.connect(
            lambda: self.copy_files(copy_files='b'))

        self.ui.line_drive_a.editingFinished.connect(
            lambda: self.drive_line_changed(drive='drive_a'))
        self.ui.line_drive_b.editingFinished.connect(
            lambda: self.drive_line_changed(drive='drive_b'))
        self.ui.line_inbox_a.editingFinished.connect(
            lambda: self.drive_line_changed(drive='inbox_a'))
        self.ui.line_inbox_b.editingFinished.connect(
            lambda: self.drive_line_changed(drive='inbox_b'))

        self.ui.line_inbox_a.editingFinished.connect(
            lambda: self.inbox_line_changed(drive='a'))
        self.ui.line_inbox_b.editingFinished.connect(
            lambda: self.inbox_line_changed(drive='b'))

        self.ui.button_copy_both.clicked.connect(self.copy_files)

    def cancel(self):
        self.cancel = True
    def set_button_visibility(self, a=0, b=0, all_off=0, default=0):
        if all_off:
            a = 0
            b = 0
        self.ui.button_rename_a.setVisible(a)
        self.ui.button_rename_b.setVisible(b)
        self.ui.button_copy_ab.setVisible(default)
        self.ui.button_copy_ba.setVisible(default)
        self.ui.button_copy_both.setVisible(default)
        # self.ui.button_list_all.setVisible(all)
        # self.ui.button_list_unique.setVisible(unique)
        self.ui.list_a_all.setVisible(0)
        self.ui.list_b_all.setVisible(0)
        self.ui.list_a.setVisible(0)
        self.ui.list_b.setVisible(0)
        self.ui.label_count_a.setVisible(a)
        self.ui.label_count_b.setVisible(b)
        self.ui.label_unique_a.setVisible(a)
        self.ui.label_unique_b.setVisible(b)
        self.ui.progress_bar.setVisible(0)

    def toggle_lists(self, mode):
        self.set_button_visibility(default=1)
        if mode == 'all':
            self.ui.list_a_all.setVisible(1)
            self.ui.list_b_all.setVisible(1)
            self.ui.list_a.setVisible(0)
            self.ui.list_b.setVisible(0)
            self.ui.button_list_unique.setVisible(1)
            self.ui.button_list_all.setVisible(0)
            self.ui.label_count_a.setVisible(1)
            self.ui.label_count_b.setVisible(1)
            self.ui.label_unique_a.setVisible(0)
            self.ui.label_unique_b.setVisible(0)
        if mode == 'unique':
            self.ui.list_a.setVisible(1)
            self.ui.list_b.setVisible(1)
            self.ui.list_a_all.setVisible(0)
            self.ui.list_b_all.setVisible(0)
            self.ui.button_list_unique.setVisible(0)
            self.ui.button_list_all.setVisible(1)
            self.ui.label_count_a.setVisible(0)
            self.ui.label_count_b.setVisible(0)
            self.ui.label_unique_a.setVisible(1)
            self.ui.label_unique_b.setVisible(1)

    def inbox_line_changed(self, drive):
        drive = drive[-1]
        input_path = eval('self.ui.line_drive_{}.text()'.format(drive))
        inbox_path = eval('self.ui.line_inbox_{}.text()'.format(drive))
        if not os.path.isdir(inbox_path):
            exec('self.ui.line_inbox_{}.setText("")'.format(drive))
        if not input_path:
            exec("self.ui.line_inbox_{}.setText('')".format(drive))
            return
        if not inbox_path:
            exec('self.ui.line_inbox_{}.setText("{}")'.format(
                drive, os.path.join(input_path, 'inbox')))

    def drive_line_changed(self, drive):
        path = eval('self.ui.line_{}.text()'.format(drive))
        path = self.path_cleaner(path)
        if not os.path.isdir(path):
            exec("self.ui.line_{}.setText('')".format(drive))

        if drive.startswith('drive'):
            drive = drive[-1]
            self.get_volume_name(path, drive)
            if eval('self.ui.line_inbox_{}.text()'.format(drive)) == '':
                exec("self.ui.line_inbox_{}.setText('{}')".format(drive, path))

    def file_browser(self, drive):
        directory = os.path.dirname(eval(
            'self.ui.line_{}.text()'.format(drive)
        ))
        path = QtGui.QFileDialog.getExistingDirectory(
            caption='Select root directory to compare from',
            filter='*.{}'.format(' *.'.join(self.valid_extensions)),
            dir=directory
        )
        if path:
            path = self.path_cleaner(path)
            exec(
                "self.ui.line_{}.setText('{}')".format(drive, path)
            )
            self.inbox_line_changed(drive)
            self.get_volume_name(path, drive[-1])

    def path_cleaner(self, path):
        path = path.replace('/', '\\')
        if path.endswith('\\'):
            path = path[:-1]
        return path if os.path.isdir(path) else ''

    def rename_files(self, file_list):
        file_list = eval('self.{}_files'.format(file_list))
        self.renamed_files = []
        for movie in sorted(file_list):
            basename, ext = os.path.splitext(movie)
            directory = os.path.dirname(file_list[movie][0])
            basename = basename.replace('_', ' ')
            basename = self.titlecase(basename)
            if basename.lower().startswith('the '):
                basename = '{} (The)'.format(basename[4:])
            basename = basename.replace('(the)', '(The)')
            basename = basename.replace(' (', '(')
            basename = basename.replace('(', ' (')
            renamed = '{}{}'.format(os.path.join(directory, basename), ext)
            if str(renamed) == str(file_list[movie][0]):
                continue
            try:
                os.rename(file_list[movie][0], renamed)
                self.log(3, '"{}" renmaed to "{}"'.format(
                    os.path.basename(file_list[movie][0]),
                    os.path.basename(renamed)
                ))
            except OSError:
                self.log(2, 'Could not rename {}'.format(file_list[movie][0]))
        self.compare_drives()

    def compare_drives(self):
        for path in [self.ui.line_drive_a.text(), self.ui.line_drive_b.text()]:
            if not self.path_cleaner(path):
                self.log(1, 'Declare two drives to compare \ sync \ copy')
                # return
        if not self.ensure_seperate_drives():
            return

        [list_.clear() for list_ in [self.ui.list_a, self.ui.list_b]]
        self.ui.button_list_all.setVisible(1)
        self.ui.button_list_unique.setVisible(1)
        self.ui.list_a.setVisible(0)
        self.ui.list_b.setVisible(0)
        self.ui.list_b_all.setVisible(0)
        self.ui.list_a_all.setVisible(0)
        self.set_button_visibility(all_off=1, default=0)

        drive_a = self.ui.line_drive_a.text()
        drive_b = self.ui.line_drive_b.text()

        self.a_files = self.gather_files(drive_a)
        self.b_files = self.gather_files(drive_b)

        if self.a_files:
            self.log(0, 'Searching for movies at: {}'.format(drive_a))
        if self.b_files:
            self.log(0, 'Searching for movies at: {}'.format(drive_b))

        matches = list(set([
            a_title for a_title in self.a_files
            for b_title in self.b_files
            if a_title != b_title
        ]))
        self.a_unique = sorted(
            [file_ for file_ in self.a_files if file_ not in matches])
        self.b_unique = sorted(
            [file_ for file_ in self.b_files if file_ not in matches])

        [self.ui.list_a.addItem(title) for title in self.a_unique]
        [self.ui.list_a_all.addItem(title) for title in sorted(self.a_files)]
        [self.ui.list_b.addItem(title) for title in self.b_unique]
        [self.ui.list_b_all.addItem(title) for title in sorted(self.b_files)]
        self.ui.label_count_a.setText(
            'Total movie count of Drive A: {}'.format(len(self.a_files)))
        self.ui.label_count_b.setText(
            'Total movie count of Drive B: {}'.format(len(self.b_files)))
        self.ui.label_unique_a.setText(
            'Unique movie count of Drive A: {}'.format(len(self.a_unique)))
        self.ui.label_unique_b.setText(
            'Unique movie count of Drive B: {}'.format(len(self.b_unique)))
        if not self.a_unique and not self.b_unique:
            self.log(0, 'Movies already sync between these drives')
        self.toggle_lists('all')

    def gather_files(self, path):
        return {
            os.path.basename(y): [
                y, os.path.getctime(y), os.path.getsize(y)]
            for x in os.walk(path)
            for y in glob.glob(os.path.join(x[0], '*.*'))
            if y.split('.')[-1] in self.valid_extensions
        }

    def copy_files(self, copy_files='all'):
        if not self.check_all_paths_valid():
            return
        self.start_time = time.time()
        if copy_files == 'all':
            self.copy_a_to_b()
            self.copy_b_to_a()
        if copy_files == 'a':
            self.copy_a_to_b()
        if copy_files == 'b':
            self.copy_b_to_a()

    def copy_a_to_b(self):
        a_movies = [
            str(self.ui.list_a.item(i).text())
            for i in range(self.ui.list_a.count())
        ]

        for movie in a_movies:
            if self.cancel:
                break
            self.movie_time = time.time()
            source = self.a_files[movie][0]
            destination = os.path.join(
                self.inbox_b[0], os.path.basename(source))

            self.update_progress(a_movies, movie, 'B')
            time.sleep(.05)
            shutil.copyfile(source, destination)
            self.log(0, '{} took {} seconds'.format(
                movie, int(time.time() - self.movie_time)))

        self.update_progress(None, None, complete=True)
        self.cancel = False

    def copy_b_to_a(self):
        b_movies = [
            str(self.ui.list_b.item(i).text())
            for i in range(self.ui.list_b.count())
        ]

        for movie in b_movies:
            if self.cancel:
                break
            self.movie_time = time.time()
            source = self.b_files[movie][0]
            destination = os.path.join(
                self.inbox_a[0], os.path.basename(source))

            self.update_progress(b_movies, movie, 'A')
            time.sleep(.05)
            shutil.copyfile(source, destination)
            self.log(0, '{} took {} seconds'.format(
                movie, int(time.time() - self.movie_time)))

        self.update_progress(None, None, complete=True)
        self.cancel = False

    def update_progress(
        self,
        movie_list=None,
        movie=None,
        dest=None,
        complete=False
            ):
        if complete:
            self.log(0, 'Operation completed in {} seconds!'.format(
                int(time.time() - self.start_time)))
            self.ui.progress_bar.setVisible(0)
            self.compare_drives()
            self.movie_progress = []
            return

        percent_complete = (
            float(len(self.movie_progress)) / float(len(movie_list))) * 100
        self.log(3, 'Copying "{}" to Drive: {}'.format(movie, dest))
        self.ui.progress_bar.setVisible(1)
        self.ui.progress_bar.setValue(percent_complete)
        app.processEvents()
        self.movie_progress.append(movie)

    def check_all_paths_valid(self):
        self.drive_a = (self.ui.line_drive_a.text(), 'Drive A')
        self.drive_b = (self.ui.line_drive_b.text(), 'Drive B')
        self.inbox_a = (self.ui.line_inbox_a.text(), 'Inbox A')
        self.inbox_b = (self.ui.line_inbox_b.text(), 'Inbox B')
        for path in [self.drive_a, self.drive_b]:
            if not os.path.isdir(path[0]):
                self.log(1, '{} path invalid'.format(path[1]))
                return

        for path in [self.inbox_a, self.inbox_b]:
            try:
                os.makedirs(path[0])
            except OSError:
                pass
            if not os.path.isdir(path[0]):
                self.log(1, '{} path invalid'.format(path[1]))
                return

        return True

    def log(self, verbose, message):
        level = ['', 'WARNING: ', 'ERROR: ', 'PROCESSING: ']
        message = '{}{}'.format(level[verbose], message)
        self.ui.list_log.addItem(message)
        self.ui.list_log.scrollToBottom()

    def get_volume_name(self, path, drive):
        path = self.path_cleaner(path)
        label = 'VOLUME NAME: '
        if path:
            path = '{}/'.format(os.path.splitdrive(path)[0])
            label = '{}{}'.format(
                label, win32api.GetVolumeInformation(path)[0])
            exec('self.ui.label_volume_{}.setText("{}")'.format(drive, label))

    def ensure_seperate_drives(self):
        return True

    def titlecase(self, string):
        exceptions = [
            'a', 'an', 'at', 'by', 'from', 'for', 'and', 'of', 'the', 'is']
        string = re.sub(
            r"[A-Za-z]+('[A-Za-z]+)?",
            lambda mo: mo.group(0)[0].upper() +
            mo.group(0)[1:].lower(), string
        )
        word_list = re.split(' ', string)       # re.split behaves as expected
        final = [word_list[0].capitalize()]
        for word in word_list[1:]:
            final.append(
                word.lower() if word.lower() in exceptions
                else word.capitalize()
            )
        return " ".join(final)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = movie_app()
    myapp.show()
    sys.exit(app.exec_())

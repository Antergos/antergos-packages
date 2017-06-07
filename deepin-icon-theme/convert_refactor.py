#!/usr/bin/env python2
#-*- coding:utf-8 -*-


import os
import sys
import shutil
import ConfigParser

class PngGenerate(object):

    def __init__(self, theme_dir, src_dir):
        self.theme = theme_dir
        self.src = src_dir
        self.config_file = os.path.join(self.theme, "index.theme")
        self._init_config()
        self._init_dirs()


    def _init_config(self):
        # Read needed vars in index.theme file.
        self.config = ConfigParser.ConfigParser()
        self.config.read(self.config_file)
        self.directories = self.config.get('Icon Theme', 'Directories').split(',')
        self.theme_name = self.config.get('Icon Theme', 'Name')


    def _init_dirs(self):
        # Initialize direcotries variable.
        self.icon_dirs = {}
        # check if directory in format '16x16/apps'
        if self.directories[0].split('/')[0][0].isdigit():
            self.digit_first = True
        else:
            self.digit_first = False

        for directory in self.directories:
            if self.digit_first:
                size = directory.split('/')[0]
                icon_type = directory.split('/')[1]
            else:
                size = directory.split('/')[1]
                icon_type = directory.split('/')[0]
            size = size.split('x')[0]

            if not self.icon_dirs.has_key(icon_type):
                self.icon_dirs[icon_type] = []

            if not (size, directory) in self.icon_dirs[icon_type]:
                self.icon_dirs[icon_type].append((size,directory))


    def _generate_png(self, image_path, icon_type):
        # Convert given image into given type_dir.
        image_name = os.path.basename(image_path)[:-4]
        for size,directory in self.icon_dirs[icon_type]:
            if size == 'scalable':
                shutil.copy(image_path,
                            os.path.join(self.theme, directory, "%s.svg" % image_name))
                continue

            output_file = os.path.join(self.theme, directory, "%s.png" % image_name)
            PngGenerate.svg_to_png(image_path, size, output_file)


    def convert(self):
        # Main method to convert svg files in src_dir.
        for directory in os.listdir(self.src):
            current_path = os.path.join(self.src, directory)
            for svg_file in os.listdir(current_path):
                image_path = os.path.join(current_path, svg_file)
                if not svg_file.endswith(".svg"):
                    continue
                if not self.icon_dirs.has_key(directory):
                    raise Exception, 'Theme does not contain dir: %s' % directory
                self._generate_png(image_path, directory)


    @classmethod
    def svg_to_png(cls, input_file, size, output_file):
        # Convert svg to png file using command:
        # inkscape -f input_file -w width -e output_file
        dir_name = os.path.dirname(output_file)

        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        print "converting %s to %s" % (input_file, output_file)
        os.system("inkscape -f %s -w %s -e %s" % (input_file, size, output_file))



if __name__ == "__main__":
    if not len(sys.argv) == 3:
        print "Usage: %s Theme_dir Svg_dir" % __file__
        exit()

    theme_dir = sys.argv[1]
    src_dir = sys.argv[2]
    if not os.path.exists(src_dir):
        print "%s not exists." % src_dir
        exit()
    if not os.path.exists(theme_dir):
        print "%s not exists." % theme_dir
        exit()

    converter = PngGenerate(theme_dir, src_dir)
    converter.convert()

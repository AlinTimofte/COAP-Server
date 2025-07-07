import os

from numpy.testing.print_coercion_tables import print_new_cast_table

import coap_tools as ct


def create_default_directories():

    os.mkdir(ct.defaultServerFileLocation)
    os.mkdir(ct.defaultToolsFileLocation)


def create_dir(path, dir_name):
    if not os.path.exists(path):
        return -1
    if os.path.exists(path + '/' + dir_name):
        return -2

    try:
        os.makedirs(path + '/' + dir_name)
        return 0
    except OSError:
        # TODO: return an error message
        return False


def create_file(path, filename, text, extension):

    if not os.path.exists(path):
        return -1

    if os.path.exists(path + '/' + filename + '.' + extension):
        print('exista deja')
        return -2
    try:
        file = open(path + '/' + filename + '.' + extension, 'w')
        file.write(text)
    except FileNotFoundError:
        print('')
    return 0


def add_to_file(path, filename, extension, text):

    if not os.path.exists(path):
        return -1
    if not os.path.isfile(path + '/' + filename + '.' + extension):
        return -1
    try:
        file = open(path + '/' + filename + '.' + extension, 'a')
        file.write(text)
        return 0
    except FileNotFoundError:
        print('')


def rename(path, name, extension, new_name):
    if extension == '':
        if not os.path.isdir(path + '/' + name):
            return -1
        os.rename(path + '/' + name, path + '/' + new_name)
    else:
        if not os.path.isfile(path + '/' + name + '.' + extension):
            return -1
        os.rename(path + '/' + name + '.' + extension, path + '/' + new_name + '.' + extension)
    return 0


def delete(path, name, extension):

    if extension == '':
        if not os.path.isdir(path + '/' + name):
            return -1
        if os.listdir(path + '/' + name):
            return -3
        os.rmdir(path + '/' + name)
    else:
        if not os.path.isfile(path + '/' + name + '.' + extension):
            return -1
        os.remove(path + '/' + name + '.' + extension)

    return 0


def move_dir(path, new_path, name):
    if not os.path.exists(path + '/' + name):
        return -1
    if os.listdir(path + '/' + name):
        return -3
    print(new_path)
    if not os.path.exists(new_path):
        return -1
    os.rmdir(path + '/' + name)
    os.mkdir(new_path + '/' + name)
    return 0

# https://www.codespeedy.com/how-to-delete-similar-images-from-a-directory-or-folder-in-python/
# A file hash method (best for exact matches, even if filename is different.

import hashlib
from imageio import imread
import matplotlib.pyplot as plt
import os
import shutil


def move_file(path, file_name):

    src = os.path.join(path, file_name)
    dst = os.path.join(path, 'similar', file_name)

    try:
        print('source: %s > destination: %s' % (src, dst))
        shutil.move(src, dst)

    except FileNotFoundError:
        print('cannot move %s' % src)


def main(path, show_results=False):

    os.chdir(path)
    os.getcwd()

    # Make a directory for moving images to
    if os.path.exists('similar') is False:
        os.mkdir('similar')

    files_list = os.listdir('.')
    print('number to process: %s' % len(files_list))
    duplicates = []
    hash_keys = dict()

    for index, filename in enumerate(os.listdir('.')):

        if os.path.isfile(filename):
            with open(filename, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()

            if file_hash not in hash_keys:
                hash_keys[file_hash] = index

            else:
                duplicates.append((index, hash_keys[file_hash]))

    print('number of duplicates: %s' % len(duplicates))

    if show_results is True:
        for index in duplicates:
            try:
                print(index)
                plt.subplot(121), plt.imshow(imread(files_list[index[1]]))
                plt.title(files_list[index[1]]), plt.xticks([]), plt.yticks([])
                plt.subplot(122), plt.imshow(imread(files_list[index[0]]))
                plt.title(files_list[index[0]] + ' duplicate'), plt.xticks([]), plt.yticks([])
                plt.show()

            except OSError as e:
                continue

    # Move Duplicates
    for index in duplicates:
        move_file(path, files_list[index[0]])
        move_file(path, files_list[index[1]])

    print('Done')


if __name__ == "__main__":
    main(r'V:\Male', show_results=False)

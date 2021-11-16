
import os
import shutil

base_path = 'V:\\Art'

for f in os.listdir(base_path):

    full_path = os.path.join(base_path, f)
    file_name, ext = os.path.splitext(f)

    if '.jfif' in ext:

        new_path = os.path.join(base_path, file_name + ".jpg")
        print(full_path, new_path)

        shutil.move(full_path, new_path)

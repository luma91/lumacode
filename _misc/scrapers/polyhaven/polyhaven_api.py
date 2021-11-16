
# https://github.com/Poly-Haven/Public-API

import json
from datetime import datetime
import os
import requests
import urllib.request


download_dir = 'X:\\polyhaven'
api_url = 'https://api.polyhaven.com'


agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) ' \
        'Chrome/35.0.1916.47 Safari/537.36'


def get_assets(asset_type):
    return requests.get(api_url + '/assets?t=%s' % asset_type).json()


def get_info(asset_name):
    return requests.get(api_url + '/info/%s' % asset_name).json()


def get_files(asset_name):
    return requests.get(api_url + '/files/%s' % asset_name).json()


def download_it(url, path):

    # Set urllib parameters
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent', agent)]
    urllib.request.install_opener(opener)

    # Do download
    urllib.request.urlretrieve(url, path)


def get_preview(asset_name, path):
    preview_path = 'https://cdn.polyhaven.com/asset_img/thumbs/%s.png?height=780' % asset_name
    download_it(preview_path, os.path.join(path, 'thumb.png'))


def write_metadata(incoming_data, file_path, url):

    metadata_path = os.path.join(file_path, 'info.json')

    author = [x for x in incoming_data['authors']]
    keywords = incoming_data['categories']
    tags = incoming_data['tags']
    date = datetime.fromtimestamp(incoming_data['date_published']).strftime('%d %b %Y %H:%M')
    new_data = {"authors": author, "url": url, "date": date, "keywords": keywords, "tags": tags}

    scale = incoming_data.get('scale')
    if scale:
        new_data.update({'scale': scale})

    print(new_data)

    with open(metadata_path, 'w') as f:
        data = json.dumps(new_data)
        f.write(data)


def main(asset_type='textures', skip_on_folder=True):

    assets = get_assets(asset_type)

    for asset in assets:

        exists = False
        path = os.path.join(download_dir, asset_type, asset)
        contents_path = os.path.join(path, 'versions', 'v001')

        if os.path.exists(path) is False:
            os.makedirs(path)

        else:
            exists = True

        if skip_on_folder and exists:
            print('Skipping %s' % asset)
            continue

        asset_info = get_info(asset)

        print('-------------------')
        print('ASSET: %s' % asset)
        print('--- %s' % asset_info)

        url = 'http://polyhaven.com/a/%s' % asset
        write_metadata(asset_info, path, url)

        """
        get_preview(asset, path)
        asset_data = get_files(asset)

        for data_type in asset_data:

            # Filter out types
            # if data_type in ['nor_gl', 'nor_dx', 'arm', 'gltf', 'blend']:
            #    continue

            print('--- %s' % data_type)

            for resolution in asset_data[data_type]:

                # Skip low res types, we can make these ourselves if needed.
                if resolution in ['1k', '2k']:
                    continue

                # Make path for resolution
                res_path = os.path.join(contents_path, resolution)
                if os.path.exists(res_path) is False:
                    os.makedirs(res_path)

                files = asset_data[data_type][resolution]
                print('------ %s' % resolution)

                for ext in files:

                    # Skip PNG, we have JPG and EXR already!
                    if 'png' in ext:
                        continue

                    # Make extension folder
                    full_path = os.path.join(res_path, ext)
                    if os.path.exists(full_path) is False:
                        os.mkdir(full_path)

                    file_url = files[ext]['url']
                    print('------------ %s: %s' % (ext, file_url))

                    file_name = file_url.split('/')[-1]
                    full_file_path = os.path.join(full_path, file_name)

                    if os.path.exists(full_file_path) is False:
                        download_it(file_url, full_file_path)
                    else:
                        print('file exists. skipping download...')

        print('-------------------')
        """


if __name__ == "__main__":
    main()

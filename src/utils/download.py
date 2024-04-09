import pandas as pd

import os
import requests
import tarfile
from tqdm import tqdm

cur_path = os.path.abspath('tables')
parent_directory = os.path.dirname(os.path.dirname(cur_path))


def download_file(url, destination):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024
    with open(destination, 'wb') as file:
        with tqdm(total=total_size, unit='B', unit_scale=True, disable=True) as progress_bar:
            for data in response.iter_content(block_size):
                file.write(data)
                progress_bar.update(len(data))
                percent_complete = (file.tell() / total_size) * 100
                print(f'\rDownloading... {percent_complete:.2f}%', end='', flush=True)
    print('\nDownload complete')


# def extract_tar_gz(archive_path, destination):
#     with tarfile.open(archive_path, 'r:gz') as tar:
#         tar.extractall(path=destination)

def extract_tar_gz(archive_path, destination):
    with tarfile.open(archive_path, 'r:gz') as tar:
        with tqdm(total=len(tar.getmembers()), unit='files', unit_scale=True, disable=True) as progress_bar:
            tar.extractall(path=destination)
            progress_bar.update(len(tar.getmembers()))


def remove_archive(archive_path):
    os.remove(archive_path)


def download():
    download_directory = f'{parent_directory}/downloads_json'

    if not os.path.exists(download_directory):
        os.makedirs(download_directory)

    json_df = pd.read_csv(f'{parent_directory}/tables/json_links.csv')
    json_df = json_df[:1]
    urls = json_df['link'].tolist()
    for url in tqdm(urls):
        file_name = url.split('/')[-1]

        archive_path = os.path.join(download_directory, file_name)

        print("  Downloading:", url)
        download_file(url, archive_path)

        print("  Extracting:", archive_path)
        extract_tar_gz(archive_path, download_directory)

        print("Removing:", archive_path)
        remove_archive(archive_path)

    print("Done")


if __name__ == '__main__':
    download()

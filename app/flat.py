import boto
import zipfile
from os import path
import config


def download_modelzip(zip_path):
    conn = boto.connect_s3(
        config.AWS_ACCESS_KEY_ID, config.AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(config.modelzip_bucket, validate=False)
    key = bucket.get_key(config.modelzip_filename)
    key.get_contents_to_filename(zip_path)

def unzip_model(zip_path):
    zip_ref = zipfile.ZipFile(zip_path, 'r')
    zip_ref.extractall(config.path_base)
    zip_ref.close()

def extract_flat():
    path_unzip = path.join(config.path_base, config.modelzip_filename)
    download_modelzip(path_unzip)
    unzip_model(path_unzip)


if __name__ == '__main__':
    extract_flat()

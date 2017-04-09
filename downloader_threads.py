#!/usr/bin/env python3
import os
import sys
import os.path
import argparse

import csv

import urllib
import urllib.error
import urllib.parse
import urllib.request
import urllib.response
import re

import threading
import numpy as np

# 4441138248,1957,1957-01-01 00:00:00,6,https://farm5.staticflickr.com/4029/4441138248_c640aa4f98.jpg,kcox5342,"Niagara Falls, 1957",Attribution-NonCommercial License,https://creativecommons.org/licenses/by-nc/2.0/

FLICKR_ID = 0
YEAR = 1
DATE = 2
DATE_GRANULARITY = 3
URL = 4
USER = 5
TITLE = 6
LICENSE_TEXT = 7
LICENSE_URL = 8

THREADS = 8


def chunks(l, n):
    index_list = np.linspace(0, len(l), n + 1)
    for i in range(0, n):
        yield l[int(index_list[i]):int(index_list[i + 1])]


def read_image(url):

    try:
        with urllib.request.urlopen(url) as f:
            return (f.read())
    except urllib.error.URLError as err:
        pass
    except urllib.error.HTTPError as err:
        print(str(err.code) + " : " + str(err.reason))
        if err.code == 429:
            time.sleep(5)
    return None


def parse_args():
    parser = argparse.ArgumentParser(description='Downloader for the Date Estimation in the Wild Dataset')

    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument(
        '-i', '--input', dest='input_path', type=str, required=True, help='Path to the meta.csv file from radar')
    parser.add_argument(
        '-o',
        '--output',
        dest='output_path',
        type=str,
        help='Output path to the downloaded images. Will be create if not exists')
    args = parser.parse_args()
    return args


def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def compute_image_folder(folder, id):
    image_path = "{}.jpg".format(id)
    return os.path.join(folder, image_path[0:1], image_path[1:3])


def download_job(images_to_download, output_path, missed_images, count, verbose, thread_id):
    local_count = 0
    for flickr_id, url in images_to_download:
        image_folder = compute_image_folder(output_path, flickr_id)
        image = read_image(url)
        if image is None:
            missed_images.append((flickr_id, url))
            continue

        create_folder(image_folder)

        with open(os.path.join(image_folder, '{}.jpg'.format(flickr_id)), 'wb') as f:
            f.write(image)

        local_count += 1
        count['count'] += 1

        if verbose and local_count % 10 == 0:
            print('Downloaded {} out of {} images in thread {}'.format(local_count, len(images_to_download), thread_id))


def main():
    args = parse_args()

    # read args or use defaults
    output_path = 'images'
    if args.output_path:
        output_path = args.output_path

    # create output folder
    create_folder(output_path)

    #flickr_id check

    flickr_id_re = re.compile(r'\d+')

    # read meta.csv
    missed_images = []
    images_to_download = []
    with open(args.input_path, 'r') as source_file:
        spamreader = csv.reader(source_file, delimiter=',')
        for row in spamreader:
            if re.match(flickr_id_re, row[FLICKR_ID]):
                images_to_download.append((row[FLICKR_ID], row[URL]))

    exists_images = []
    # remove all entries that already exists in the download folder
    for root, dirs, files in os.walk(output_path):
        for f in files:
            exists_images.append(f)

    images_to_download = list(filter(lambda item: '{}.jpg'.format(item[0]) not in exists_images, images_to_download))

    count = {'count': 0}
    missed_images = []
    thread_list = []
    thread_args = list(chunks(images_to_download, THREADS))
    for x in range(THREADS):
        t = threading.Thread(
            target=download_job, args=(thread_args[x], output_path, missed_images, count, args.verbose, x))
        t.start()

        thread_list.append(t)

    for x in thread_list:
        x.join()

    # write missed files
    with open(os.path.join(output_path, 'missing_images.csv'), 'w') as missed_file:
        spamwriter = csv.writer(missed_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for entry in missed_images:
            spamwriter.writerow(entry)

    if args.verbose:
        print('{} out of {} images are downloaded in total'.format(count['count'], len(images_to_download)))
        print('Finish')

    return 0


if __name__ == '__main__':
    sys.exit(main())

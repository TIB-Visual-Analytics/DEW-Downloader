# DEW-Downloader
Python3 downloader for the Date Estimation in the Wild dataset

We provide two versions of the downloader:
  downloader.py
  downloader_threads.py

While downloader.py can be used without additional python packages,
downloader_threads.py is parallelized and further requires the
numpy package.

Both version can be executed in the same way

1. Download the meta.csv from: https://doi.org/10.22000/0001abcde
2. Run the script in the following way:

```bash
  python3 downloader.py -i <path/to/meta.csv>
  python3 downloader.py -i <path/to/meta.csv> -o <path/to/output/folder> # define output folder
  python3 downloader.py -i <path/to/meta.csv> -o <path/to/output/folder> -v # verbose outputs
```

Images which can not be downloaded are stored in the following file:
<path/to/output/folder>/missing_images.csv

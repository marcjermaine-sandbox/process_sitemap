import csv
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor

import requests
from tqdm import tqdm


def parse_sitemap(sitemap_path):
    tree = ET.parse(sitemap_path)
    root = tree.getroot()

    urls = [
        element.text
        for element in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
    ]
    return urls


def check_url(url):
    response = requests.get(url)
    if response.status_code != 200:
        with open("broken_links.csv", "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([url])
        return url


def check_urls(urls):
    broken_links = []

    with ThreadPoolExecutor() as executor:
        futures = []
        for url in urls:
            future = executor.submit(check_url, url)
            futures.append(future)

        for future in tqdm(futures, total=len(futures)):
            result = future.result()
            if result:
                broken_links.append(result)

    if not broken_links:
        print("No broken links found.")
    else:
        print(f"Found {len(broken_links)} broken links. See broken_links.csv for details.")


sitemap_paths = ["sitemap1.xml", "sitemap2.xml", "sitemap3.xml"]
# sitemap_path = "sitemap3.xml"  # Replace with the path to your local sitemap.xml file
# urls = parse_sitemap(sitemap_path)
# check_urls(urls)
for sitemap_path in sitemap_paths:
    urls = parse_sitemap(sitemap_path)
    check_urls(urls)

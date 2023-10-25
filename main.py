import subprocess
import os
import requests
from bs4 import BeautifulSoup

STEAMCMD_PATH = ""
GMAD_PATH = ""
OUTPUT_PATH = ""

COLLECTION_URL = ""


def download_addon(id, path=OUTPUT_PATH, output_name=None):
    cmd = [STEAMCMD_PATH, f"+force_install_dir {path}", "+login anonymous", f"+workshop_download_item 4000 {id} validate", "+quit"]

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if process is None:
        print(f"Error downloading addon {id}")
        return
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            decode = output.strip().decode()
            if f"Success. Downloaded item {id}" in decode:
                print(f"Successfully downloaded addon {id}")
                process.kill()
                break
            if "ERROR!" in decode:
                print(f"Error downloading addon {id}")
                process.kill()
                return "ERROR"

    downloaded_file_folder = path + f"\\steamapps\\workshop\\content\\4000\\{id}"

    downloaded_file = None
    for file in os.listdir(downloaded_file_folder):
        downloaded_file = file

    if downloaded_file is None:
        print(f"Error downloading addon {id}")
        return "ERROR"

    output_name = output_name.replace(" ", "_")

    if output_name is None:
        output_name = id

    os.replace(f"{downloaded_file_folder}\\{downloaded_file}", f"{path}\\{output_name}.gma")

    return f"{output_name}.gma"


def extract_addon(file_path, delete_gma=True):
    file_name = file_path.split("\\")[-1]

    cmd = [GMAD_PATH, "extract", "-file", file_path]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if process is None:
        print(f"Error extracting addon {file_path}")
        return
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            decode = output.strip().decode()
            if f"Done!" in decode:
                print(f"Successfully extracted addon {file_name}")
                process.kill()
                break

    if delete_gma:
        os.remove(file_path)


def download_and_extract_addon(id, addon_name=None, delete_gma=True):
    print(f"\nDownloading addon {id}")

    if addon_name is not None:
        file_name = download_addon(id, OUTPUT_PATH, addon_name)
    else:
        file_name = download_addon(id, OUTPUT_PATH)

    if file_name == "ERROR":
        return "ERROR"

    extract_addon(OUTPUT_PATH + "\\" + file_name, delete_gma)


def parse_collection(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    workshop_items = soup.find_all("div", class_="collectionItem")

    addon_info = []

    for item in workshop_items:
        workshop_item = item.find("div", class_="collectionItemDetails")
        workshop_item_link = workshop_item.find("a", href=True)
        addon_id = workshop_item_link['href'].split("?id=")[1]
        addon_name = workshop_item_link.text

        addon_info.append((addon_id, addon_name))

    return addon_info


def download_collection(url):
    addon_info = parse_collection(url)

    for addon in addon_info:
        status = download_and_extract_addon(addon[0], addon[1], True)


def main():
    download_collection(COLLECTION_URL)


if __name__ == "__main__":
    main()

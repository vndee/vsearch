import requests
from glob import glob
from tqdm import tqdm


if __name__ == "__main__":
    list_files = glob("data/tiki/*/*.jpg")
    URL = "http://localhost:8000/index/"

    for fi in tqdm(list_files, desc="Indexing.."):
        id = fi.split("/")[2]

        dc = {
            "image": (fi, open(fi, "rb")),
        }

        response = requests.post(URL, files=dc, data={ "id": id })

        # print(f"{fi}: {response.json()}")

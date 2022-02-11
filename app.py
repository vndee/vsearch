import json
import requests
import http.client
import streamlit as st
from PIL import Image

URL = "http://localhost:8000/search/"
STATIC_URL = "http://localhost:8000/"
PDP_API = "https://tiki.vn/api/v2/products/{}?platform=web&spid={}"

with open("css/labs.css") as fin:
    css0 = fin.read()
with open("css/masonry.css") as fin:
    css1 = fin.read()

app_name = "Visual Search"
st.set_page_config(
    layout="wide", page_title=app_name,
)

st.sidebar.header("Visual Search")
uploaded_file = st.sidebar.file_uploader("Choose an image...", type="jpg")

conn = http.client.HTTPSConnection("tiki.vn")
payload = ""
headers = {}

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    with st.sidebar.container():
        st.image(image, width=150, caption='Uploaded image')

    st.header("Results")
    with st.spinner('Searching...'):
        dc = {
            "image": ("uploaded_file.jpg", uploaded_file.getbuffer()),
        }

        results = requests.post(URL, files=dc)
        results = results.json()
        for i, res in enumerate(results.get("results")):
            conn.request("GET", PDP_API.format(res[0], res[0]))
            response = conn.getresponse()
            data = response.read()
            data = json.loads(data.decode("utf-8"))

            try:
                results["results"][i].append(data["name"])
                results["results"][i].append(data["list_price"])
            except Exception as ex:
                results["results"][i].append("Cannot fetch data")
                results["results"][i].append("NULL")

        results["results"] = sorted(results["results"], key=lambda x: x[1], reverse=True)

        divs = [
            f"""
            <div class="brick">
                <a href="https://tiki.vn/p/{res[0]}/">
                    <img src="{STATIC_URL}{res[2]}">
                    <figcaption>product_id: {res[0]} - score: {round(res[1], 2)}</figcaption>
                    <figcaption>{res[3].capitalize()} - {res[4]}₫</figcaption>
                </a>
            </div>
            """
            for res in results.get("results")
        ]
        divs = "\n".join(divs)

        html = """
        <html>
          <base target="_blank" />
          <head>
            <style> %s </style>
            <style> %s </style>
          </head>
          <body>
              <div class="masonry">
                %s
              </div>
          </body>
        </html>
        """ % (
            css0,
            css1,
            divs,
        )

        st.components.v1.html(html, height=1000, scrolling=True)

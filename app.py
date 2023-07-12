import os
import zipfile
import xml.etree.ElementTree as ET
import urllib.request
from flask import Flask, render_template

import constants as c

app = Flask(__name__)

def save_xml():
    if not os.path.exists(c.DATA_PATH):
        os.makedirs(c.DATA_PATH)

    urllib.request.urlretrieve(c.URL, f"{c.DATA_PATH}/{c.ZIP}")

    with zipfile.ZipFile(f"{c.DATA_PATH}/{c.ZIP}", 'r') as zip_ref:
        zip_ref.extractall(c.DATA_PATH)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/products/count')
def product_count():
    xml_path = f"{c.DATA_PATH}/{c.XML_NAME}"
    if not os.path.exists(xml_path):
        save_xml()

    tree = ET.parse(xml_path)
    root = tree.getroot()
    product_count = len(root.findall(".//item"))

    return render_template('count.html', product_count=product_count, page='product_count')

@app.route('/products/names')
def product_names():
    xml_path = f"{c.DATA_PATH}/{c.XML_NAME}"
    if not os.path.exists(xml_path):
        save_xml()

    tree = ET.parse(xml_path)
    root = tree.getroot()

    product_names = [product.attrib['name'] for product in root.findall(".//item")]

    return render_template('names.html', product_names=product_names, page='product_names')


def find_items_recursive(element, parent_categories=[], results=[]):
    item_child = element.find("item")
    if item_child is not None:
        parent_categories = parent_categories + [element]
        item_names = [item.attrib.get("name") for item in element.findall(".//item")]
        parent_category_names = [category.attrib.get("name") for category in parent_categories]

        # print("Item Names:", item_names)
        # print("Parent Category Names:", parent_category_names)
        # print()

        result = {
            "items": item_names,
            "parents": parent_category_names[1:]
        }
        results.append(result)

    else:
        for child in element.findall("category"):
            find_items_recursive(child, parent_categories + [element], results)


def find_categories_recursive(element, parent_categories=[], results=[]):
    if element.attrib.get("type") == "part":
        find_items_recursive(element, parent_categories, results)

    for child in element.findall("category"):
        find_categories_recursive(child, parent_categories + [element], results)


@app.route('/products/spare_parts')
def product_spare_parts():
    xml_path = f"{c.DATA_PATH}/{c.XML_NAME}"
    if not os.path.exists(xml_path):
        save_xml()

    tree = ET.parse(xml_path)
    root = tree.getroot()

    categories_new = root.find(".//categoriesNew")
    results = []
    find_categories_recursive(categories_new, [], results)


    return render_template('spare_parts.html', results=results, page='product_spare_parts')
    # return render_template('spare_parts.html', spare_parts=spare_parts, page='spare_parts')

if __name__ == '__main__':
    app.run()

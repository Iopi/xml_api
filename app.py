import os
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

from flask import Flask, render_template

import constants as c

app = Flask(__name__)


def save_xml():
    """
    Ukládá XML data z URL do složky DATA_PATH.
    :return:
    """
    if not os.path.exists(c.DATA_PATH):
        os.makedirs(c.DATA_PATH)

    urllib.request.urlretrieve(c.URL, f"{c.DATA_PATH}/{c.ZIP}")

    with zipfile.ZipFile(f"{c.DATA_PATH}/{c.ZIP}", 'r') as zip_ref:
        zip_ref.extractall(c.DATA_PATH)


@app.route('/')
def index():
    """
    Displays the home page of the application.
    :return:
    """
    return render_template('index.html')


@app.route('/products/count')
def product_count():
    """
    Handles a request to the URL path '/products/count'.

    The function reads an XML file, gets the number of products from the tree, and returns a response with the rendered template 'count.html'.
    It passes the variable 'product_count' with the number of products.

    :return: Response with rendered template 'count.html'
    """
    xml_path = f"{c.DATA_PATH}/{c.XML_NAME}"
    if not os.path.exists(xml_path):
        save_xml()

    tree = ET.parse(xml_path)
    root = tree.getroot()
    items = root.find("items")
    product_count = len(items.findall(".//item"))
    discontinued_items = root.find("discontinuedItems")
    dis_product_count = len(discontinued_items.findall(".//item"))

    return render_template('count.html', prod_count=product_count, dis_prod_count = dis_product_count, page='product_count')


@app.route('/products/names')
def product_names():
    """
    Handles a request for the URL path '/products/names'.

    The function reads the XML file, gets the product names from the tree, and returns a response with the 'names.html' template rendered.
    It passes the variable 'product_names' with the product names.

    :return: Response with rendered template 'names.html'
    """
    xml_path = f"{c.DATA_PATH}/{c.XML_NAME}"
    if not os.path.exists(xml_path):
        save_xml()

    tree = ET.parse(xml_path)
    root = tree.getroot()

    items = root.find("items")
    product_names = [product.attrib['name'] for product in items.findall(".//item")]

    return render_template('names.html', product_names=product_names, page='product_names')


@app.route('/products/spare_parts')
def product_spare_parts():
    """
    Displays the product spare parts page.

    Loads an XML file and searches a tree of categories and items. Searches for categories with 'type' attribute equal to 'parts'
    and calls the functions 'find_categories_recursive_parts' and 'find_items_recursive_parts' to get the results.

    The function reads the XML file, gets the all spare parts items and parents categories.

    The results are passed to the 'spare_parts.html' template which is displayed on the page.

    :return: response with rendered template 'spare_parts.html'
    """
    xml_path = f"{c.DATA_PATH}/{c.XML_NAME}"
    if not os.path.exists(xml_path):
        save_xml()

    tree = ET.parse(xml_path)
    root = tree.getroot()

    results = []
    items = root.find("items")
    item_elements = items.findall(".//item")
    for item in item_elements:
        parts = item.find("parts")
        if parts is not None:
            item_name = item.attrib.get('name')
            item_parts = [item.attrib.get("name") for item in parts.findall(".//item")]

            result = {
                "name": item_name,
                "item_parts": item_parts
            }
            results.append(result)

    return render_template('spare_parts.html', results=results, page='product_spare_parts')


if __name__ == '__main__':
    app.run()

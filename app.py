import os
import zipfile
import xml.etree.ElementTree as ET
import urllib.request
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
    product_count = len(root.findall(".//item"))

    return render_template('count.html', product_count=product_count, page='product_count')


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

    product_names = [product.attrib['name'] for product in root.findall(".//item")]

    return render_template('names.html', product_names=product_names, page='product_names')


def find_items_recursive(element, parent_categories=[], results=[]):
    """
    It recursively searches the XML tree for items.

    The function creates a dictionary containing items names and a list of parent category names.
    The results are gradually added to the 'results' list.

    :param element: XML tree element
    :param parent_categories: List of parent categories
    :param results: List of results
    :return:
    """
    if element.find("item") is not None:
        parent_categories = parent_categories + [element]
        item_names = [item.attrib.get("name") for item in element.findall(".//item")]
        parent_category_names = [category.attrib.get("name") for category in parent_categories]

        result = {
            "items": item_names,
            "parents": parent_category_names[1:]
        }
        results.append(result)

    else:
        for child in element.findall("category"):
            find_items_recursive(child, parent_categories + [element], results)


def find_categories_recursive(element, parent_categories=[], results=[]):
    """
    It recursively searches the XML tree for categories with spare parts.

    It then searches for items in this category using the 'find_items_recursive' function.

    :param element: XML tree element
    :param parent_categories: List of parent categories
    :param results: List of results
    :return:
    """
    if element.attrib.get("type") == "part":
        find_items_recursive(element, parent_categories, results)

    for child in element.findall("category"):
        find_categories_recursive(child, parent_categories + [element], results)


def find_items_recursive_parts(element, parent_categories, results):
    """
    It recursively searches the XML tree for items in element 'part'.

    The function creates a dictionary containing items names and a list of parent category names.
    The results are gradually added to the 'results' list.

    :param element: XML tree element
    :param parent_categories: List of parent categories
    :param results: List of results
    :return:
    """
    if element.find("part") is not None:
        for part in element.findall("part"):
            if part.find("item") is not None:
                parent_categories_new = parent_categories + [element]
                item_names = [item.attrib.get("name") for item in element.findall(".//item")]
                parent_category_names = [category.attrib.get("name") for category in parent_categories_new] + [
                    part.attrib.get("itemName")]

                result = {
                    "items": item_names,
                    "parents": parent_category_names[1:]
                }
                results.append(result)

    else:
        for child in element.findall("category"):
            find_items_recursive_parts(child, parent_categories + [element], results)


def find_categories_recursive_parts(element, parent_categories=[], results=[]):
    """
    It recursively searches the XML tree for categories with spare parts.

    It then searches for items in this category using the 'find_categories_recursive_parts' function.

    :param element: XML tree element
    :param parent_categories: List of parent categories
    :param results: List of results
    :return:
    """
    if element.attrib.get("type") == "parts":
        find_items_recursive_parts(element, parent_categories, results)

    for child in element.findall("category"):
        find_categories_recursive_parts(child, parent_categories + [element], results)


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
    categories_with_parts = root.find(".//categoriesWithParts")
    find_categories_recursive_parts(categories_with_parts, [], results)

    return render_template('spare_parts.html', results=results, page='product_spare_parts')


if __name__ == '__main__':
    app.run()

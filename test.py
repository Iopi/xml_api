import pytest
from app import app


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert '<h1>XML API</h1>'.encode('utf-8') in response.data


def test_product_count(client):
    response = client.get('/products/count')

    assert response.status_code == 200
    assert '<h1>Počet produktů</h1>'.encode('utf-8') in response.data
    assert response.status_code == 200


def test_product_names(client):
    response = client.get('/products/names')
    assert response.status_code == 200
    assert '<h1>Názvy produktů</h1>'.encode('utf-8') in response.data


def test_product_spare_parts(client):
    response = client.get('/products/spare_parts')
    assert response.status_code == 200
    assert '<h1>Náhradní díly</h1>'.encode('utf-8') in response.data

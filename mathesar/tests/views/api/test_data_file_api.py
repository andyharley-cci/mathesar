import pytest
from django.core.files import File

from mathesar.models import DataFile


def verify_data_file_data(data_file, data_file_dict):
    assert data_file_dict['id'] == data_file.id
    assert data_file_dict['file'] == f'http://testserver/media/{data_file.file.name}'
    if data_file.table_imported_to:
        assert data_file_dict['table_imported_to'] == data_file.table_imported_to.id
    else:
        assert data_file_dict['table_imported_to'] is None
    if data_file.user:
        assert data_file_dict['user'] == data_file.user.id
    else:
        assert data_file_dict['user'] is None
    assert data_file_dict['delimiter'] == data_file.delimiter
    assert data_file_dict['quotechar'] == data_file.quotechar
    assert data_file_dict['escapechar'] == data_file.escapechar
    assert data_file_dict['header'] == data_file.header


@pytest.fixture
def data_file(csv_filename):
    with open(csv_filename, 'rb') as csv_file:
        data_file = DataFile.objects.create(file=File(csv_file))
    return data_file


def test_data_file_list(client, data_file):
    """
    Desired format:
    {
        "count": 1,
        "results": [
            {
                "id": 1,
                "file": "http://testserver/media/anonymous/patents.csv",
                "table": {
                    "id": 1,
                    "name": "NASA Patents",
                    "url": "http://testserver/api/v0/tables/1/"
                },
                "user": 1
            }
        ]
    }
    """
    response = client.get('/api/v0/data_files/')
    response_data = response.json()

    assert response.status_code == 200
    assert response_data['count'] == 1
    assert len(response_data['results']) == 1

    data_file_dict = response_data['results'][0]
    verify_data_file_data(data_file, data_file_dict)


def test_data_file_detail(client, data_file):
    response = client.get(f'/api/v0/data_files/{data_file.id}/')
    data_file_dict = response.json()

    assert response.status_code == 200
    verify_data_file_data(data_file, data_file_dict)


def test_data_file_create_csv(client, csv_filename):
    num_data_files = DataFile.objects.count()

    with open(csv_filename, 'rb') as csv_file:
        response = client.post('/api/v0/data_files/', data={'file': csv_file})
        data_file_dict = response.json()
        data_file = DataFile.objects.get(id=data_file_dict['id'])

    assert response.status_code == 201
    assert DataFile.objects.count() == num_data_files + 1
    assert data_file.delimiter == ','
    assert data_file.quotechar == '"'
    assert data_file.escapechar == ''
    verify_data_file_data(data_file, data_file_dict)


def test_data_file_create_tsv(client, tsv_filename):
    num_data_files = DataFile.objects.count()

    with open(tsv_filename, 'rb') as tsv_file:
        response = client.post('/api/v0/data_files/', data={'file': tsv_file})
        data_file_dict = response.json()
        data_file = DataFile.objects.get(id=data_file_dict['id'])

    assert response.status_code == 201
    assert DataFile.objects.count() == num_data_files + 1
    assert data_file.delimiter == '\t'
    assert data_file.quotechar == '"'
    assert data_file.escapechar == ''
    verify_data_file_data(data_file, data_file_dict)


def test_datafile_create_mixed_quotes(client):
    file = 'mathesar/tests/data/csv_parsing/mixed_quote.csv'
    with open(file, 'r') as f:
        response = client.post('/api/v0/data_files/', data={'file': f})
        data_file_dict = response.json()
        data_file = DataFile.objects.get(id=data_file_dict['id'])
    assert response.status_code == 201
    assert data_file.delimiter == ','
    assert data_file.quotechar == "'"
    assert data_file.escapechar == ''
    verify_data_file_data(data_file, data_file_dict)


def test_datafile_create_double_quote(client):
    file = 'mathesar/tests/data/csv_parsing/double_quote.csv'
    with open(file, 'r') as f:
        response = client.post('/api/v0/data_files/', data={'file': f})
        data_file_dict = response.json()
        data_file = DataFile.objects.get(id=data_file_dict['id'])
    assert response.status_code == 201
    assert data_file.delimiter == ','
    assert data_file.quotechar == '"'
    assert data_file.escapechar == ''
    verify_data_file_data(data_file, data_file_dict)


def test_datafile_create_escaped_quote(client):
    file = 'mathesar/tests/data/csv_parsing/escaped_quote.csv'
    with open(file, 'r') as f:
        response = client.post('/api/v0/data_files/', data={'file': f})
        data_file_dict = response.json()
        data_file = DataFile.objects.get(id=data_file_dict['id'])
    assert response.status_code == 201
    assert data_file.delimiter == ','
    assert data_file.quotechar == '"'
    assert data_file.escapechar == '\\'
    verify_data_file_data(data_file, data_file_dict)


def test_data_file_update(client, data_file):
    response = client.put(f'/api/v0/data_files/{data_file.id}/')
    assert response.status_code == 405
    assert response.json()['detail'] == 'Method "PUT" not allowed.'


def test_data_file_partial_update(client, data_file):
    response = client.patch(f'/api/v0/data_files/{data_file.id}/')
    assert response.status_code == 405
    assert response.json()['detail'] == 'Method "PATCH" allowed only for header.'


def test_data_file_delete(client, data_file):
    response = client.delete(f'/api/v0/data_files/{data_file.id}/')
    assert response.status_code == 405
    assert response.json()['detail'] == 'Method "DELETE" not allowed.'


def test_data_file_404(client, data_file):
    data_file_id = data_file.id
    data_file.delete()
    response = client.get(f'/api/v0/data_files/{data_file_id}/')
    assert response.status_code == 404
    assert response.json()['detail'] == 'Not found.'


def test_datafile_create_invalid_delimiter(client):
    file = 'mathesar/tests/data/csv_parsing/patents_invalid.csv'
    with open(file, 'r') as f:
        response = client.post('/api/v0/data_files/', data={'file': f})
        data_file_dict = response.json()
    assert response.status_code == 400
    assert data_file_dict["file"] == 'Unable to tabulate datafile'


def test_datafile_create_extra_quote(client):
    file = 'mathesar/tests/data/csv_parsing/extra_quote_invalid.csv'
    with open(file, 'r') as f:
        response = client.post('/api/v0/data_files/', data={'file': f})
        data_file_dict = response.json()
    assert response.status_code == 400
    assert data_file_dict["file"] == 'Unable to tabulate datafile'


def test_datafile_create_escaped_quote_invalid(client):
    file = 'mathesar/tests/data/csv_parsing/escaped_quote_invalid.csv'
    with open(file, 'r') as f:
        response = client.post('/api/v0/data_files/', data={'file': f})
        data_file_dict = response.json()
    assert response.status_code == 400
    assert data_file_dict["file"] == 'Unable to tabulate datafile'


def test_data_file_create_csv_headerless(client, csv_filename):
    num_data_files = DataFile.objects.count()

    with open(csv_filename, 'rb') as csv_file:
        data = {'file': csv_file, 'header': False}
        response = client.post('/api/v0/data_files/', data=data)
        data_file_dict = response.json()
        data_file = DataFile.objects.get(id=data_file_dict['id'])

    assert response.status_code == 201
    assert DataFile.objects.count() == num_data_files + 1
    assert data_file.delimiter == ','
    assert data_file.quotechar == '"'
    assert data_file.escapechar == ''
    assert data_file.header is False
    verify_data_file_data(data_file, data_file_dict)

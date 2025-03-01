from unittest.mock import patch
from django.core.cache import cache
from mathesar import models


def test_schema_name_sets_cache(monkeypatch, test_db_model):
    monkeypatch.setattr(
        models.Schema, '_sa_engine', lambda x: None
    )
    monkeypatch.setattr(
        models.schemas, 'get_schema_name_from_oid', lambda x, y: 'myname'
    )
    cache.clear()
    schema = models.Schema(oid=123, database=test_db_model)
    name = schema.name
    assert cache.get(f"{schema.database.name}_schema_name_{schema.oid}") == name


def test_schema_name_uses_cache(monkeypatch, test_db_model):
    monkeypatch.setattr(
        models.Schema, '_sa_engine', lambda x: None
    )
    cache.clear()
    with patch.object(
            models.schemas, 'get_schema_name_from_oid', return_value='myname'
    ) as mock_get_name:
        schema = models.Schema(oid=123, database=test_db_model)
        name_one = schema.name
        name_two = schema.name
    assert name_one == name_two
    assert mock_get_name.call_count == 1


def test_schema_name_handles_missing(monkeypatch, test_db_model):
    monkeypatch.setattr(
        models.Schema, '_sa_engine', lambda x: None
    )
    cache.clear()

    def mock_name_getter(oid, engine):
        raise TypeError
    monkeypatch.setattr(
        models.schemas, 'get_schema_name_from_oid', mock_name_getter
    )
    schema = models.Schema(oid=123, database=test_db_model)
    name_ = schema.name
    assert name_ == 'MISSING'

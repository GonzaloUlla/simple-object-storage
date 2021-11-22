import pytest

from simple_object_storage.config import settings
from .utils import get_uuid


def test_index(api_client):
    response = api_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World!"}


def test_using_testing_db():
    assert settings.DB_NAME == "test_simple_object_storage"
    assert "test_simple_object_storage" in settings.DB_URL


def test_get_objects_in_bucket(api_client):
    bucket = "a"
    object_id1 = get_uuid(bucket, 1)
    object_id2 = get_uuid(bucket, 2)
    object_data1 = f"{bucket}1 data"
    object_data2 = f"{bucket}2 data"
    response = api_client.get(f"/objects/{bucket}")
    assert response.status_code == 200
    assert {"_id": str(object_id1), "data": object_data1} in response.json()
    assert {"_id": str(object_id2), "data": object_data2} in response.json()


def test_get_objects_in_non_existent_bucket(api_client):
    response = api_client.get("/objects/c")
    assert response.status_code == 404
    assert response.json() == {"detail": f"Bucket with name c is empty or not found"}


def test_get_object(api_client):
    bucket = "b"
    object_int = 1
    object_id = get_uuid(bucket, object_int)
    object_data = f"{bucket}{object_int} data"
    response = api_client.get(f"/objects/{bucket}/{object_id}")
    assert response.status_code == 200
    assert response.json() == {"_id": str(object_id), "data": object_data}


@pytest.mark.parametrize("bucket,object_int", [("a", 3), ("d", 1)])
def test_get_non_existent_object(api_client, bucket, object_int):
    object_id = get_uuid(bucket, object_int)
    response = api_client.get(f"/objects/{bucket}/{object_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": f"Object with id {object_id} not found in bucket {bucket}"}


@pytest.mark.parametrize("bucket,object_int", [("a", 3), ("b", 9), ("c", 1)])
def test_insert_object(api_client, bucket: str, object_int: int):
    object_id = get_uuid(bucket, object_int)
    object_data = f"{bucket}{object_int} data"
    response = api_client.put(f"/objects/{bucket}/{object_id}", json=object_data)
    assert response.status_code == 201
    assert response.json() == {"_id": str(object_id), "data": object_data}


def test_update_object(api_client):
    bucket = "a"
    object_int = 2
    object_id = get_uuid(bucket, object_int)
    new_object_data = f"new {bucket}{object_int} data"
    response = api_client.put(f"/objects/{bucket}/{object_id}", json=new_object_data)
    assert response.status_code == 200
    assert response.json() == {"_id": str(object_id), "data": new_object_data}


def test_delete_object(api_client):
    bucket = "a"
    object_int = 1
    object_id = get_uuid(bucket, object_int)
    response = api_client.delete(f"/objects/{bucket}/{object_id}")
    assert response.status_code == 204
    assert response.json() is None
    assert api_client.get(f"/objects/{bucket}/{object_id}").status_code == 404


@pytest.mark.parametrize("bucket,object_int", [("a", 8), ("f", 1)])
def test_delete_non_existent_object(api_client, bucket, object_int):
    object_id = get_uuid(bucket, object_int)
    response = api_client.delete(f"/objects/{bucket}/{object_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": f"Object with id {object_id} not found in bucket {bucket}"}

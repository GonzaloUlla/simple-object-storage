# simple-object-storage

HTTP service to store objects in buckets. Made with Python 3.8

## Run with Docker

Start services and wait until they are ready:

```shell
docker-compose up -d --build
docker-compose ps
```

## Docs

- Swagger API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc API docs: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Mongo Express

For development purposes, you can Explore data in MongoDB Express by browsing to `localhost:8081` and adding a DB with
name `simple_object_storage`


## Development

Create a virtualenv and install dependencies:

```shell
python3 -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

Run the project:

```shell
cd simple_object_storage
uvicorn main:app --reload --port 8001
```

Run tests:

```shell
pytest
```
"""Main API module with all endpoints and methods"""
from typing import List
from uuid import UUID, uuid4

from fastapi import Body, FastAPI, Path, status, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from config import settings
from deps import get_db

app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION
)

object_id_path_param = Path(..., title="Object ID", description="A valid UUID")
bucket_path_param = Path(..., title="Bucket name", description="A non-empty string", regex="^(?!\s*$).+")


class ObjectModel(BaseModel):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    data: str

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "id": "00010203-0405-0607-0809-0a0b0c0d0e0f",
                "data": "My data payload",
            }
        }


@app.get("/")
async def index() -> dict:
    return {"message": "Hello World!"}


@app.get(
    "/objects/{bucket}",
    response_model=List[ObjectModel],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Bucket Empty or Not Found"}
    }
)
async def get_objects(bucket: str = bucket_path_param, db=Depends(get_db)):
    objects = await db[bucket].find().to_list(1000)
    if objects:
        return objects
    raise HTTPException(status_code=404, detail=f"Bucket with name {bucket} is empty or not found")


@app.get(
    "/objects/{bucket}/{object_id}",
    response_model=ObjectModel,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Object Not Found"}
    }
)
async def get_object(bucket: str = bucket_path_param, object_id: UUID = object_id_path_param, db=Depends(get_db)):
    obj = await db[bucket].find_one({"_id": jsonable_encoder(object_id)})
    if obj is not None:
        return obj
    raise HTTPException(status_code=404, detail=f"Object with id {object_id} not found in bucket {bucket}")


@app.put(
    "/objects/{bucket}/{object_id}",
    response_model=ObjectModel,
    responses={
        status.HTTP_200_OK: {"description": "Object Updated"},
        status.HTTP_201_CREATED: {"description": "Object Created"}
    }
)
async def upsert_object(
        bucket: str = bucket_path_param,
        object_id: UUID = object_id_path_param,
        object_data: str = Body(...),
        db=Depends(get_db)
) -> JSONResponse:
    obj = ObjectModel(id=object_id, data=object_data)
    find_result = await db[bucket].find_one({"_id": jsonable_encoder(obj.id)})
    if find_result is None:
        insert_result = await db[bucket].insert_one(jsonable_encoder(obj))
        created_obj = await db[bucket].find_one({"_id": insert_result.inserted_id})
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_obj)
    else:
        update_result = await db[bucket].update_one(
            {"_id": jsonable_encoder(obj.id)},
            {"$set": {"data": jsonable_encoder(obj.data)}}
        )
        if update_result.modified_count == 1:
            updated_obj = await db[bucket].find_one({"_id": jsonable_encoder(obj.id)})
            return JSONResponse(status_code=status.HTTP_200_OK, content=updated_obj)


@app.delete(
    "/objects/{bucket}/{object_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_description="Object Deleted",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Object Not Found"}
    }
)
async def delete_object(bucket: str = bucket_path_param, object_id: UUID = object_id_path_param, db=Depends(get_db)):
    delete_result = await db[bucket].delete_one({"_id": jsonable_encoder(object_id)})

    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Object with id {object_id} not found in bucket {bucket}")

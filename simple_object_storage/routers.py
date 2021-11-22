"""API endpoints and methods"""

from typing import List
from uuid import UUID

from crud import (
    delete_object_by_id,
    get_object_by_id,
    get_objects_by_bucket,
    insert_object,
    update_object_data,
)
from deps import get_db
from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from fastapi.responses import JSONResponse
from models import ObjectModel

router = APIRouter()

object_id_path_param = Path(..., title="Object ID", description="A valid UUID")
bucket_path_param = Path(
    ..., title="Bucket name", description="A non-empty string", regex="^(?!\s*$).+"
)


@router.get(
    "/{bucket}",
    response_model=List[ObjectModel],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Bucket Empty or Not Found"}},
)
async def get_objects(bucket: str = bucket_path_param, db=Depends(get_db)):
    objects = await get_objects_by_bucket(db, bucket)
    if objects:
        return objects
    raise HTTPException(
        status_code=404, detail=f"Bucket with name {bucket} is empty or not found"
    )


@router.get(
    "/{bucket}/{object_id}",
    response_model=ObjectModel,
    responses={status.HTTP_404_NOT_FOUND: {"description": "Object Not Found"}},
)
async def get_object(
    bucket: str = bucket_path_param,
    object_id: UUID = object_id_path_param,
    db=Depends(get_db),
):
    obj = await get_object_by_id(db, bucket, object_id)
    if obj is not None:
        return obj
    raise HTTPException(
        status_code=404,
        detail=f"Object with id {object_id} not found in bucket {bucket}",
    )


@router.put(
    "/{bucket}/{object_id}",
    response_model=ObjectModel,
    responses={
        status.HTTP_200_OK: {"description": "Object Updated"},
        status.HTTP_201_CREATED: {"description": "Object Created"},
    },
)
async def upsert_object(
    bucket: str = bucket_path_param,
    object_id: UUID = object_id_path_param,
    object_data: str = Body(...),
    db=Depends(get_db),
) -> JSONResponse:
    obj = ObjectModel(id=object_id, data=object_data)
    find_result = await get_object_by_id(db, bucket, obj.id)
    if find_result is None:
        insert_result = await insert_object(db, bucket, obj)
        created_obj = await get_object_by_id(db, bucket, insert_result.inserted_id)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_obj)
    else:
        update_result = await update_object_data(db, bucket, obj.id, obj.data)
        if update_result.modified_count == 1:
            updated_obj = await get_object_by_id(db, bucket, obj.id)
            return JSONResponse(status_code=status.HTTP_200_OK, content=updated_obj)


@router.delete(
    "/{bucket}/{object_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_description="Object Deleted",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Object Not Found"}},
)
async def delete_object(
    bucket: str = bucket_path_param,
    object_id: UUID = object_id_path_param,
    db=Depends(get_db),
):
    delete_result = await delete_object_by_id(db, bucket, object_id)

    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(
        status_code=404,
        detail=f"Object with id {object_id} not found in bucket {bucket}",
    )

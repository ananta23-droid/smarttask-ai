from datetime import datetime
from typing import List
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException, status
from pymongo.errors import PyMongoError

from app.database import get_task_collection
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


def parse_object_id(task_id: str) -> ObjectId:
    """Validates and parses a string into a BSON ObjectId."""
    try:
        return ObjectId(task_id)
    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task ID format. Must be a 24-character hexadecimal string."
        )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task_in: TaskCreate):
    """Creates a new task in MongoDB."""
    collection = get_task_collection()
    new_task_doc = {
        "title": task_in.title,
        "description": task_in.description or "",
        "priority": task_in.priority.value,
        "status": task_in.status.value,
        "created_at": datetime.utcnow().isoformat()
    }

    try:
        result = collection.insert_one(new_task_doc)
        created_doc = collection.find_one({"_id": result.inserted_id})
        if not created_doc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve task after creation."
            )
        return TaskResponse.from_mongo(created_doc)
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while creating task."
        )


@router.get("", response_model=List[TaskResponse], status_code=status.HTTP_200_OK)
def get_all_tasks():
    """Retrieves all tasks sorted by creation date descending."""
    collection = get_task_collection()
    try:
        cursor = collection.find().sort("created_at", -1)
        tasks = [TaskResponse.from_mongo(doc) for doc in cursor]
        return tasks
    except PyMongoError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while fetching tasks."
        )


@router.get("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def get_task_by_id(task_id: str):
    """Retrieves a single task by its unique ID."""
    oid = parse_object_id(task_id)
    collection = get_task_collection()
    try:
        doc = collection.find_one({"_id": oid})
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found."
            )
        return TaskResponse.from_mongo(doc)
    except HTTPException:
        raise
    except PyMongoError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while retrieving task."
        )


@router.put("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def update_task(task_id: str, task_in: TaskUpdate):
    """Updates an existing task."""
    oid = parse_object_id(task_id)
    collection = get_task_collection()

    # Build update dictionary for provided fields only
    update_data = {}
    if task_in.title is not None:
        update_data["title"] = task_in.title
    if task_in.description is not None:
        update_data["description"] = task_in.description
    if task_in.priority is not None:
        update_data["priority"] = task_in.priority.value
    if task_in.status is not None:
        update_data["status"] = task_in.status.value

    if not update_data:
        # Nothing to update, simply return existing document
        existing = collection.find_one({"_id": oid})
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found."
            )
        return TaskResponse.from_mongo(existing)

    try:
        result = collection.update_one({"_id": oid}, {"$set": update_data})
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found."
            )
        updated_doc = collection.find_one({"_id": oid})
        return TaskResponse.from_mongo(updated_doc)
    except HTTPException:
        raise
    except PyMongoError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while updating task."
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str):
    """Deletes a task by its unique ID."""
    oid = parse_object_id(task_id)
    collection = get_task_collection()
    try:
        result = collection.delete_one({"_id": oid})
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found."
            )
        return None
    except HTTPException:
        raise
    except PyMongoError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while deleting task."
        )

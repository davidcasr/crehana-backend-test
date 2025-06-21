from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..application.dtos import (
    TaskListCreateRequest, 
    TaskListUpdateRequest, 
    TaskListResponse
)
from ..application.use_cases.task_list import TaskListUseCases
from ..dependencies import get_db, get_task_list_use_cases
from ..domain.exceptions import (
    TaskListNotFoundException, 
    TaskListNameAlreadyExistsException,
    ValidationError
)

router = APIRouter(prefix="/task-lists", tags=["Task Lists"])


@router.post("/", response_model=TaskListResponse, status_code=status.HTTP_201_CREATED)
def create_task_list(
    request: TaskListCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a new task list."""
    try:
        use_cases = get_task_list_use_cases(db)
        task_list_entity = use_cases.create_task_list(
            name=request.name,
            description=request.description
        )
        return TaskListResponse.from_entity(task_list_entity)
    
    except TaskListNameAlreadyExistsException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/", response_model=List[TaskListResponse])
def get_all_task_lists(db: Session = Depends(get_db)):
    """Get all task lists."""
    try:
        use_cases = get_task_list_use_cases(db)
        task_list_entities = use_cases.get_all_task_lists()
        return [TaskListResponse.from_entity(task_list) for task_list in task_list_entities]
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/{task_list_id}", response_model=TaskListResponse)
def get_task_list(
    task_list_id: int,
    db: Session = Depends(get_db)
):
    """Get a task list by ID."""
    try:
        use_cases = get_task_list_use_cases(db)
        task_list_entity = use_cases.get_task_list(task_list_id)
        return TaskListResponse.from_entity(task_list_entity)
    
    except TaskListNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")



@router.put("/{task_list_id}", response_model=TaskListResponse)
def update_task_list(
    task_list_id: int,
    request: TaskListUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update a task list."""
    try:
        use_cases = get_task_list_use_cases(db)
        task_list_entity = use_cases.update_task_list(
            task_list_id=task_list_id,
            name=request.name,
            description=request.description
        )
        return TaskListResponse.from_entity(task_list_entity)
    
    except TaskListNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except TaskListNameAlreadyExistsException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete("/{task_list_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_list(
    task_list_id: int,
    db: Session = Depends(get_db)
):
    """Delete a task list."""
    try:
        use_cases = get_task_list_use_cases(db)
        use_cases.delete_task_list(task_list_id)
    
    except TaskListNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error") 
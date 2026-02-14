"""
Task API endpoints.

This module defines all task-related API routes with strict user isolation.
Every endpoint enforces that users can only access their own tasks.

**Endpoints**:
- GET /api/{user_id}/tasks - List all user's tasks
- POST /api/{user_id}/tasks - Create new task
- GET /api/{user_id}/tasks/{id} - Get single task
- PUT /api/{user_id}/tasks/{id} - Update task
- PATCH /api/{user_id}/tasks/{id}/complete - Toggle completion
- DELETE /api/{user_id}/tasks/{id} - Delete task
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List
from datetime import datetime

from src.database import get_session
from src.schemas.task import TaskCreate, TaskUpdate, TaskRead, TaskStatusUpdate
from src.services.task_service import TaskService
from src.services.permissions import PermissionService
from src.services.activity_service import ActivityService
from src.models.activity import ActivityType
from src.models.task import TaskStatus, TaskPriority # Updated import
from src.middleware.auth import validate_user_id
from src.models.user import User # Added for get_current_user
from src.middleware.auth import get_current_user # Added for current user


# Create router for task endpoints
router = APIRouter(prefix="/api", tags=["Tasks"])


@router.get(
    "/{user_id}/tasks",
    response_model=List[TaskRead],
    status_code=status.HTTP_200_OK,
    summary="List all user's tasks",
    description="""
    Retrieve all tasks for the authenticated user, ordered by creation date (newest first).

    **Security**: Requires valid JWT token. User can only access their own tasks.

    **Returns:**
    - HTTP 200: List of tasks (may be empty array if no tasks)
    - HTTP 401: If authentication fails
    - HTTP 403: If user_id in URL doesn't match authenticated user

    **Authorization**: Bearer {jwt_token}
    """
)
async def list_tasks(
    user_id: str = Depends(validate_user_id),
    session: Session = Depends(get_session)
) -> List[TaskRead]:
    """
    List all tasks for authenticated user.

    The validate_user_id dependency ensures user_id matches the authenticated user.
    This prevents User A from accessing User B's tasks.

    Args:
        user_id: User ID from URL (validated to match JWT token)
        session: Database session (injected)

    Returns:
        List[TaskRead]: All user's tasks, newest first (empty array if none)

    Example Request:
        GET /api/7c9e6679-7425-40de-944b-e07fc1f90ae7/tasks
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

    Example Response (200):
        [
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Complete project documentation",
                "description": "Write comprehensive API docs",
                "is_completed": false,
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z",
                "user_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7"
            }
        ]

    Example Response (Empty, 200):
        []
    """
    # Get all tasks for user (ordered by created_at DESC)
    tasks = TaskService.get_user_tasks(session, user_id)

    # Return list of tasks (empty array if no tasks)
    return [TaskRead.model_validate(task) for task in tasks]


@router.post(
    "/{user_id}/tasks",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="""
    Create a new task for the authenticated user.

    **Security**: Requires valid JWT token. User can only create tasks for themselves.

    **Validation**:
    - Title: Required, 1-500 characters
    - Description: Optional, 0-5000 characters

    **Returns:**
    - HTTP 201: Task created successfully
    - HTTP 400: If user_id is invalid format
    - HTTP 401: If authentication fails
    - HTTP 403: If user_id in URL doesn't match authenticated user
    - HTTP 422: If validation fails (empty title, too long, etc.)

    **Authorization**: Bearer {jwt_token}
    """
)
async def create_task(
    task_data: TaskCreate,
    user_id: str = Depends(validate_user_id),
    session: Session = Depends(get_session)
) -> TaskRead:
    """
    Create a new task for authenticated user.

    Args:
        task_data: TaskCreate schema with title and optional description
        user_id: User ID from URL (validated to match JWT token)
        session: Database session (injected)

    Returns:
        TaskRead: Newly created task

    Raises:
        HTTPException 422: If validation fails (Pydantic)

    Example Request:
        POST /api/7c9e6679-7425-40de-944b-e07fc1f90ae7/tasks
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
        Content-Type: application/json

        {
            "title": "Complete project documentation",
            "description": "Write comprehensive API documentation"
        }

    Example Response (201):
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "title": "Complete project documentation",
            "description": "Write comprehensive API documentation",
            "is_completed": false,
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z",
            "user_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7"
        }
    """
    # Create personal task (no workspace) directly
    import uuid as uuid_module
    from datetime import datetime
    from src.models.task import Task, TaskStatus, TaskPriority
    
    user_uuid = uuid_module.UUID(user_id)
    
    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority or TaskPriority.MEDIUM,
        status=task_data.status or TaskStatus.TO_DO,
        created_by=user_uuid,  # Set created_by
        user_id=user_uuid,  # Set user_id for compatibility
        workspace_id=None,  # Personal task - no workspace
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    session.add(new_task)
    session.commit()
    session.refresh(new_task)

    # Return created task
    return TaskRead.model_validate(new_task)


@router.put(
    "/{user_id}/tasks/{task_id}",
    response_model=TaskRead,
    status_code=status.HTTP_200_OK,
    summary="Update an existing task",
    description="""
    Update a task's details (title and/or description).

    **Security**: Requires valid JWT token. User can only update their own tasks.

    **Note**: All fields in request body are optional. Only provided fields will be updated.

    **Returns:**
    - HTTP 200: Task updated successfully
    - HTTP 400: If task_id or user_id is invalid format
    - HTTP 401: If authentication fails
    - HTTP 403: If user tries to update another user's task
    - HTTP 404: If task not found
    - HTTP 422: If validation fails

    **Authorization**: Bearer {jwt_token}
    """
)
async def update_task(
    task_id: str,
    update_data: TaskUpdate,
    user_id: str = Depends(validate_user_id),
    session: Session = Depends(get_session)
) -> TaskRead:
    """
    Update an existing task's details.

    Args:
        task_id: Task ID from URL path
        update_data: TaskUpdate schema with optional title/description
        user_id: User ID from URL (validated to match JWT token)
        session: Database session (injected)

    Returns:
        TaskRead: Updated task

    Raises:
        HTTPException 404: If task not found
        HTTPException 403: If task belongs to another user
        HTTPException 422: If validation fails

    Example Request:
        PUT /api/7c9e6679-7425-40de-944b-e07fc1f90ae7/tasks/550e8400-e29b-41d4-a716-446655440000
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
        Content-Type: application/json

        {
            "title": "Updated: Complete project documentation",
            "description": "Updated description with more details"
        }

    Example Response (200):
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "title": "Updated: Complete project documentation",
            "description": "Updated description with more details",
            "is_completed": false,
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T14:00:00Z",
            "user_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7"
        }
    """
    # Update task via service layer (enforces ownership)
    updated_task = TaskService.update_task_simple(session, user_id, task_id, update_data)

    # Return updated task
    return TaskRead.model_validate(updated_task)


@router.patch(
    "/{user_id}/tasks/{task_id}/complete",
    response_model=TaskRead,
    status_code=status.HTTP_200_OK,
    summary="Toggle task completion status",
    description="""
    Toggle a task's completion status (completed ↔ not completed).

    **Security**: Requires valid JWT token. User can only toggle their own tasks.

    **Returns:**
    - HTTP 200: Task completion status toggled successfully
    - HTTP 400: If task_id or user_id is invalid format
    - HTTP 401: If authentication fails
    - HTTP 403: If user tries to toggle another user's task
    - HTTP 404: If task not found

    **Authorization**: Bearer {jwt_token}
    """
)
async def toggle_task_completion(
    task_id: str,
    user_id: str = Depends(validate_user_id),
    session: Session = Depends(get_session)
) -> TaskRead:
    """
    Toggle task completion status.

    If task is completed, it becomes not completed (and vice versa).

    Args:
        task_id: Task ID from URL path
        user_id: User ID from URL (validated to match JWT token)
        session: Database session (injected)

    Returns:
        TaskRead: Task with toggled completion status

    Raises:
        HTTPException 404: If task not found
        HTTPException 403: If task belongs to another user

    Example Request:
        PATCH /api/7c9e6679-7425-40de-944b-e07fc1f90ae7/tasks/550e8400-e29b-41d4-a716-446655440000/complete
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

    Example Response (200):
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "title": "Complete project documentation",
            "description": "Write comprehensive API documentation",
            "is_completed": true,  # Toggled from false to true
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T15:00:00Z",
            "user_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7"
        }
    """
    # Toggle completion status via service layer (enforces ownership)
    toggled_task = TaskService.toggle_task_completion(session, user_id, task_id)

    # Return updated task
    return TaskRead.model_validate(toggled_task)


@router.get(
    "/{user_id}/tasks/{task_id}",
    response_model=TaskRead,
    status_code=status.HTTP_200_OK,
    summary="Get a specific task",
    description="""
    Retrieve details of a specific task by ID.

    **Security**: Requires valid JWT token. User can only access their own tasks.

    **Returns:**
    - HTTP 200: Task details returned successfully
    - HTTP 400: If task_id or user_id is invalid format
    - HTTP 401: If authentication fails
    - HTTP 403: If user tries to access another user's task
    - HTTP 404: If task not found

    **Authorization**: Bearer {jwt_token}
    """
)
async def get_task(
    task_id: str,
    user_id: str = Depends(validate_user_id),
    session: Session = Depends(get_session)
) -> TaskRead:
    """
    Get a specific task by ID.

    Args:
        task_id: Task ID from URL path
        user_id: User ID from URL (validated to match JWT token)
        session: Database session (injected)

    Returns:
        TaskRead: Task details

    Raises:
        HTTPException 404: If task not found
        HTTPException 403: If task belongs to another user

    Example Request:
        GET /api/7c9e6679-7425-40de-944b-e07fc1f90ae7/tasks/550e8400-e29b-41d4-a716-446655440000
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

    Example Response (200):
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "title": "Complete project documentation",
            "description": "Write comprehensive API documentation",
            "is_completed": false,
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z",
            "user_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7"
        }
    """
    # Get task via service layer (enforces ownership)
    task = TaskService.get_task_by_id(session, user_id, task_id)

    # Return task details
    return TaskRead.model_validate(task)


@router.delete(
    "/{user_id}/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description="""
    Permanently delete a task.

    **Security**: Requires valid JWT token. User can only delete their own tasks.

    **Returns:**
    - HTTP 204: Task deleted successfully (no response body)
    - HTTP 400: If task_id or user_id is invalid format
    - HTTP 401: If authentication fails
    - HTTP 403: If user tries to delete another user's task
    - HTTP 404: If task not found

    **Authorization**: Bearer {jwt_token}
    """
)
async def delete_task(
    task_id: str,
    user_id: str = Depends(validate_user_id),
    session: Session = Depends(get_session)
) -> None:
    """
    Delete a task permanently.

    Args:
        task_id: Task ID from URL path
        user_id: User ID from URL (validated to match JWT token)
        session: Database session (injected)

    Returns:
        None (HTTP 204 No Content)

    Raises:
        HTTPException 404: If task not found
        HTTPException 403: If task belongs to another user

    Example Request:
        DELETE /api/7c9e6679-7425-40de-944b-e07fc1f90ae7/tasks/550e8400-e29b-41d4-a716-446655440000
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

    Example Response (204):
        No content (empty response body)
    """
    # Delete task via service layer (enforces ownership)
    TaskService.delete_task(session, user_id, task_id)

    # Return 204 No Content (FastAPI handles this automatically)
    return None


# ===== WORKSPACE-AWARE ENDPOINTS (007-interactive-workspace-views) =====

@router.patch(
    "/workspaces/{workspace_id}/tasks/{task_id}/status",
    response_model=TaskRead,
    status_code=status.HTTP_200_OK,
    summary="Update task status (Kanban drag-and-drop)",
    description="""
    Update a task's status for Kanban board drag-and-drop operations.

    **Security**:
    - Requires valid JWT token
    - User must have at least MEMBER role in the workspace
    - Task must belong to the workspace

    **Status Values**: TO_DO, IN_PROGRESS, REVIEW, DONE

    **Activity Logging**: Status changes are logged automatically

    **Returns:**
    - HTTP 200: Task status updated successfully
    - HTTP 400: If task_id or workspace_id is invalid format
    - HTTP 401: If authentication fails
    - HTTP 403: If user lacks permission (not a workspace member)
    - HTTP 404: If task or workspace not found
    - HTTP 422: If validation fails (invalid status value)

    **Authorization**: Bearer {jwt_token}
    """
)
async def update_task_status(
    workspace_id: str,
    task_id: str,
    status_update: TaskStatusUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> TaskRead:
    """
    Update task status for Kanban drag-and-drop.

    This endpoint is optimized for Kanban board operations with:
    - Workspace permission validation (MEMBER role required)
    - Automatic activity logging
    - Optimistic UI support (< 1 second response time)

    Args:
        workspace_id: Workspace ID from URL path
        task_id: Task ID from URL path
        status_update: TaskStatusUpdate schema with new status
        user_id: User ID from JWT token (injected)
        session: Database session (injected)

    Returns:
        TaskRead: Updated task with new status

    Raises:
        HTTPException 404: If task or workspace not found
        HTTPException 403: If user lacks workspace access or task doesn't belong to workspace
        HTTPException 422: If status value is invalid

    Example Request:
        PATCH /api/workspaces/450e8400-e29b-41d4-a716-446655440001/tasks/550e8400-e29b-41d4-a716-446655440000/status
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
        Content-Type: application/json

        {
            "status": "IN_PROGRESS"
        }

    Example Response (200):
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "title": "Complete project documentation",
            "description": "Write comprehensive API documentation",
            "is_completed": false,
            "status": "IN_PROGRESS",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T15:30:00Z",
            "user_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
            "workspace_id": "450e8400-e29b-41d4-a716-446655440001"
        }
    """
    import uuid as uuid_module

    # Convert string IDs to UUID
    try:
        workspace_uuid = uuid_module.UUID(workspace_id)
        task_uuid = uuid_module.UUID(task_id)
        user_uuid = current_user.id # Use current_user.id directly
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format"
        )

    # Check workspace permission (MEMBER role required to edit tasks)
    if not PermissionService.user_can_edit_task(session, user_uuid, workspace_uuid):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to edit tasks in this workspace"
        )

    # Get task and verify it belongs to workspace
    task = TaskService.get_task_by_id_and_workspace(session, current_user, workspace_uuid, task_uuid)

    # Store old status for activity logging
    old_status = task.status

    # Update task status
    task.status = status_update.status

    # Auto-mark as completed if moved to DONE
    if status_update.status == TaskStatus.DONE:
        task.completed_at = datetime.utcnow()
    elif task.completed_at and status_update.status != TaskStatus.DONE:
        # Unmark completion if moved away from DONE
        task.completed_at = None

    session.add(task)
    session.commit()
    session.refresh(task)

    # Log activity (async in background for production)
    try:
        activity_description = f"Task '{task.title}' moved from {old_status.value} to {status_update.status.value}"
        ActivityService.log_activity(
            db=session,
            workspace_id=workspace_uuid,
            user_id=user_uuid,
            activity_type=ActivityType.TASK_STATUS_CHANGED,
            description=activity_description,
            task_id=task_uuid
        )
    except Exception as e:
        # Don't fail the request if activity logging fails
        print(f"Warning: Activity logging failed: {e}")

    return TaskRead.model_validate(task)


@router.get(
    "/workspaces/{workspace_id}/tasks",
    response_model=List[TaskRead],
    status_code=status.HTTP_200_OK,
    summary="List workspace tasks",
    description="""
    Retrieve all tasks for a workspace.

    **Security**:
    - Requires valid JWT token
    - User must be a member of the workspace (any role)

    **Returns:**
    - HTTP 200: List of tasks (may be empty array)
    - HTTP 401: If authentication fails
    - HTTP 403: If user is not a workspace member
    - HTTP 404: If workspace not found

    **Authorization**: Bearer {jwt_token}
    """
)
async def list_workspace_tasks(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> List[TaskRead]:
    """
    List all tasks in a workspace.

    Args:
        workspace_id: Workspace ID from URL path
        user_id: User ID from JWT token (injected)
        session: Database session (injected)

    Returns:
        List[TaskRead]: All tasks in workspace

    Raises:
        HTTPException 403: If user is not a workspace member
        HTTPException 404: If workspace not found
    """
    import uuid as uuid_module

    try:
        workspace_uuid = uuid_module.UUID(workspace_id)
        user_uuid = current_user.id # Use current_user.id directly
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format"
        )

    # Check workspace access
    if not PermissionService.user_has_workspace_access(session, user_uuid, workspace_uuid):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this workspace"
        )

    # Get workspace tasks
    from sqlmodel import select
    from src.models.task import Task

    statement = (
        select(Task)
        .where(Task.workspace_id == workspace_uuid)
        .order_by(Task.created_at.desc())
    )
    tasks = session.exec(statement).all()

    return [TaskRead.model_validate(task) for task in tasks]



@router.post(
    "/workspaces/{workspace_id}/tasks",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task in workspace",
    description="""
    Create a new task in a workspace.

    **Security**:
    - Requires valid JWT token
    - User must have at least MEMBER role in the workspace

    **Returns:**
    - HTTP 201: Task created successfully
    - HTTP 401: If authentication fails
    - HTTP 403: If user lacks permission
    - HTTP 404: If workspace not found

    **Authorization**: Bearer {jwt_token}
    """
)
async def create_workspace_task(
    workspace_id: str,
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> TaskRead:
    """
    Create a new task in a workspace.

    Args:
        workspace_id: Workspace ID from URL path
        task_data: TaskCreate schema
        current_user: Authenticated user (injected)
        session: Database session (injected)

    Returns:
        TaskRead: Newly created task

    Raises:
        HTTPException 403: If user lacks workspace access
        HTTPException 404: If workspace not found
    """
    import uuid as uuid_module

    try:
        workspace_uuid = uuid_module.UUID(workspace_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format"
        )

    # Debug logging
    print(f"Creating task in workspace {workspace_uuid} for user {current_user.id}")
    print(f"Task data: {task_data}")

    # Create task via service layer
    try:
        new_task = TaskService.create_task(session, current_user, workspace_uuid, task_data)
        print(f"Task created successfully: {new_task.id}")
        return TaskRead.model_validate(new_task)
    except HTTPException as e:
        print(f"Permission error: {e.detail}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

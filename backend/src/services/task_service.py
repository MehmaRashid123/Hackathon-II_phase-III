"""
Task business logic service layer.

This module provides the TaskService class which handles all task-related
business logic with strict user isolation. Every method ensures that users
can only access their own tasks.

**Security**: All methods filter by user_id to prevent horizontal privilege escalation.
"""

from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException, status
import uuid

from src.models.task import Task, TaskStatus, TaskPriority
from src.models.user import User
from src.models.workspace_member import WorkspaceMember, WorkspaceRole
from src.models.project import Project 
from src.schemas.task import TaskCreate, TaskUpdate
from src.services.activity_service import ActivityService
from src.models.activity import ActivityType
from src.services.permissions import PermissionService


class TaskService:
    """
    Service layer for task operations with user isolation.

    All methods enforce user isolation by filtering queries with user_id.
    This ensures User A cannot access User B's tasks.

    **Critical Security Pattern**:
    Every database query MUST include: `.where(Task.user_id == user_id)`
    """

    @staticmethod
    def get_user_tasks(session: Session, user_id: str) -> List[Task]:
        """
        Retrieve all tasks for a specific user, ordered by creation date (newest first).

        Args:
            session: Database session
            user_id: User's UUID (string format)

        Returns:
            List[Task]: All tasks belonging to the user, ordered by created_at DESC

        Example:
            tasks = TaskService.get_user_tasks(session, "7c9e6679-7425-40de-944b-e07fc1f90ae7")
            # Returns all tasks for that user, newest first
        """
        # Parse user_id to UUID
        user_uuid = uuid.UUID(user_id)

        # Query tasks filtered by created_by (not user_id), ordered by created_at descending
        statement = (
            select(Task)
            .where(Task.created_by == user_uuid)
            .order_by(Task.created_at.desc())
        )

        tasks = session.exec(statement).all()
        return list(tasks)

    @staticmethod
    def get_workspace_tasks(
        session: Session,
        current_user: User,
        workspace_id: uuid.UUID
    ) -> List[Task]:
        """
        Retrieve all tasks for a specific workspace, ensuring the current user
        has access to that workspace.
        """
        if not PermissionService.user_has_workspace_access(session, current_user.id, workspace_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this workspace."
            )

        statement = (
            select(Task)
            .where(Task.workspace_id == workspace_id)
            .order_by(Task.created_at.desc())
        )
        tasks = session.exec(statement).all()
        return list(tasks)

    @staticmethod
    def create_task(
        session: Session,
        current_user: User,
        workspace_id: uuid.UUID,
        task_data: TaskCreate
    ) -> Task:
        """
        Create a new task for a specific user within a workspace.

        Args:
            session: Database session
            current_user: The authenticated user
            workspace_id: ID of the workspace
            task_data: TaskCreate schema

        Returns:
            Task: Newly created task object
        """
        # Check if user has permission to create tasks in this workspace
        if not PermissionService.user_can_edit_task(session, current_user.id, workspace_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to create tasks in this workspace"
            )

        new_task = Task(
            title=task_data.title,
            description=task_data.description,
            priority=task_data.priority,
            status=task_data.status,
            project_id=task_data.project_id,
            assigned_to=task_data.assigned_to,
            workspace_id=workspace_id,
            created_by=current_user.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            completed_at=datetime.utcnow() if task_data.status == TaskStatus.DONE else None
        )

        # Debug logging
        print(f"DEBUG: task_data.status = {task_data.status}")
        print(f"DEBUG: task_data.status.value = {task_data.status.value}")
        print(f"DEBUG: new_task.status = {new_task.status}")
        print(f"DEBUG: new_task.status type = {type(new_task.status)}")

        session.add(new_task)
        session.commit()
        session.refresh(new_task)
        
        # Log activity
        ActivityService.log_activity(
            db=session,
            workspace_id=workspace_id,
            user_id=current_user.id,
            activity_type=ActivityType.TASK_CREATED,
            description=f"Task '{new_task.title}' created in workspace '{workspace_id}'"
        )

        return new_task

    @staticmethod
    def get_task_by_id_and_workspace(
        session: Session,
        current_user: User,
        workspace_id: uuid.UUID,
        task_id: uuid.UUID
    ) -> Task:
        """
        Retrieve a specific task by ID, ensuring it belongs to the specified workspace
        and the current user has access to that workspace.
        """
        # Check if user is a member of the workspace
        if not PermissionService.user_has_workspace_access(session, current_user.id, workspace_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this workspace."
            )

        statement = (
            select(Task)
            .where(Task.id == task_id)
            .where(Task.workspace_id == workspace_id)
        )
        task = session.exec(statement).first()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found in workspace {workspace_id}"
            )
        
        return task
    @staticmethod
    def update_task(
        session: Session,
        current_user: User,
        workspace_id: uuid.UUID,
        task_id: uuid.UUID,
        update_data: TaskUpdate
    ) -> Task:
        """
        Update a task's details within a workspace, ensuring it belongs to the
        specified workspace and the current user has permission to edit tasks.
        """
        # Check if user has permission to update tasks in this workspace
        if not PermissionService.user_can_edit_task(session, current_user.id, workspace_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to update tasks in this workspace"
            )

        task = TaskService.get_task_by_id_and_workspace(session, current_user, workspace_id, task_id)

        # Track changes for activity logging
        changes = []
        old_status = task.status
        old_priority = task.priority
        old_assigned_to = task.assigned_to
        old_project_id = task.project_id

        update_data_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_data_dict.items():
            setattr(task, field, value)
            if field == "status" and old_status != value:
                changes.append(f"status from '{old_status.value}' to '{value.value}'")
            elif field == "priority" and old_priority != value:
                changes.append(f"priority from '{old_priority.value}' to '{value.value}'")
            elif field == "assigned_to":
                if old_assigned_to != value:
                    old_assignee_email = session.get(User, old_assigned_to).email if old_assigned_to else "unassigned"
                    new_assignee_email = session.get(User, value).email if value else "unassigned"
                    changes.append(f"assignee from '{old_assignee_email}' to '{new_assignee_email}'")
            elif field == "project_id":
                if old_project_id != value:
                    old_project_name = session.get(Project, old_project_id).name if old_project_id else "no project"
                    new_project_name = session.get(Project, value).name if value else "no project"
                    changes.append(f"project from '{old_project_name}' to '{new_project_name}'")
            elif field == "title" or field == "description":
                changes.append(f"{field} updated")

        # Update completed_at based on status change
        if task.status == TaskStatus.DONE and not task.completed_at:
            task.completed_at = datetime.utcnow()
            changes.append("marked as completed")
        elif task.status != TaskStatus.DONE and task.completed_at:
            task.completed_at = None
            changes.append("marked as not completed")

        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()
        session.refresh(task)

        if changes:
            try:
                activity_type = ActivityType.TASK_UPDATED
                if "status" in update_data_dict:
                    activity_type = ActivityType.TASK_STATUS_CHANGED
                elif "assigned_to" in update_data_dict:
                    activity_type = ActivityType.TASK_ASSIGNED

                ActivityService.log_activity(
                    db=session,
                    workspace_id=workspace_id,
                    user_id=current_user.id,
                    task_id=task_id,
                    activity_type=activity_type,
                    description=f"Task '{task.title}' updated: {', '.join(changes)}"
                )
            except Exception as e:
                # Log error but don't fail the request
                print(f"Warning: Activity logging failed during task update: {e}")

        return task
    @staticmethod
    def delete_task(
        session: Session,
        current_user: User,
        workspace_id: uuid.UUID,
        task_id: uuid.UUID
    ) -> None:
        """
        Delete a task within a workspace, ensuring it belongs to the specified workspace
        and the current user has permission to delete tasks.
        """
        if not PermissionService.user_can_edit_task(session, current_user.id, workspace_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete tasks in this workspace"
            )

        task = TaskService.get_task_by_id_and_workspace(session, current_user, workspace_id, task_id)

        session.delete(task)
        session.commit()

        ActivityService.log_activity(
            db=session,
            workspace_id=workspace_id,
            user_id=current_user.id,
            task_id=task_id,
            activity_type=ActivityType.TASK_DELETED,
            description=f"Task '{task.title}' deleted from workspace '{workspace_id}'"
        )

    @staticmethod
    def create_task_simple(
        session: Session,
        user_id: str,
        title: str,
        description: str = ""
    ) -> Task:
        """
        Create a simple personal task without workspace (for AI assistant).
        
        Args:
            session: Database session
            user_id: User UUID as string
            title: Task title
            description: Optional task description
        
        Returns:
            Created Task object
        """
        user_uuid = uuid.UUID(user_id)
        
        new_task = Task(
            title=title,
            description=description,
            created_by=user_uuid,
            user_id=user_uuid,  # Add user_id for compatibility
            status=TaskStatus.TO_DO,
            priority=TaskPriority.MEDIUM
        )
        
        session.add(new_task)
        session.commit()
        session.refresh(new_task)
        
        return new_task
    
    @staticmethod
    def get_task_by_id(
        session: Session,
        task_id: str,
        user_id: str
    ) -> Optional[Task]:
        """
        Get a task by ID for a specific user (for AI assistant).
        
        Args:
            session: Database session
            task_id: Task UUID as string
            user_id: User UUID as string
        
        Returns:
            Task object or None if not found
        """
        task_uuid = uuid.UUID(task_id)
        user_uuid = uuid.UUID(user_id)
        
        statement = (
            select(Task)
            .where(Task.id == task_uuid)
            .where(Task.created_by == user_uuid)
        )
        
        return session.exec(statement).first()
    
    @staticmethod
    def update_task_simple(
        session: Session,
        user_id: str,
        task_id: str,
        update_data: "TaskUpdate"
    ) -> Task:
        """
        Update a personal task (for personal tasks without workspace).
        
        Args:
            session: Database session
            user_id: User UUID as string
            task_id: Task UUID as string
            update_data: TaskUpdate schema with fields to update
        
        Returns:
            Updated Task object
        
        Raises:
            HTTPException: If task not found or doesn't belong to user
        """
        from fastapi import HTTPException, status as http_status
        
        task = TaskService.get_task_by_id(session, task_id, user_id)
        
        if not task:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Update fields from update_data
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(task, field, value)
        
        # Update timestamp
        from datetime import datetime
        task.updated_at = datetime.utcnow()
        
        session.add(task)
        session.commit()
        session.refresh(task)
        
        return task
    
    @staticmethod
    def toggle_task_completion(
        session: Session,
        user_id: str,
        task_id: str
    ) -> Task:
        """
        Toggle task completion status (for personal tasks).
        
        Args:
            session: Database session
            user_id: User UUID as string
            task_id: Task UUID as string
        
        Returns:
            Updated Task object with toggled status
        
        Raises:
            HTTPException: If task not found or doesn't belong to user
        """
        from fastapi import HTTPException, status as http_status
        
        task = TaskService.get_task_by_id(session, task_id, user_id)
        
        if not task:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Toggle status between DONE and TO_DO
        if task.status == TaskStatus.DONE:
            task.status = TaskStatus.TO_DO
            task.completed_at = None
        else:
            task.status = TaskStatus.DONE
            task.completed_at = datetime.utcnow()
        
        # Update timestamp
        task.updated_at = datetime.utcnow()
        
        session.add(task)
        session.commit()
        session.refresh(task)
        
        return task

"""
Task SQLModel for persistent task storage.

This module defines the Task entity for the todo application.
Each task belongs to a single user and contains task details.
"""

from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from typing import Optional, List
import uuid
from enum import Enum

class TaskPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"

class TaskStatus(str, Enum):
    TO_DO = "TO_DO"
    IN_PROGRESS = "IN_PROGRESS"
    REVIEW = "REVIEW"
    DONE = "DONE"


class Task(SQLModel, table=True):
    """
    Task model representing a todo item.

    **Schema Design**:
    - Each task belongs to one user (many-to-one relationship)
    - Foreign key constraint with CASCADE delete (user deleted → tasks deleted)
    - Indexes on user_id and created_at for efficient filtering and sorting

    **Fields**:
    - id: UUID primary key
    - title: Task title (1-500 characters, required)
    - description: Task description (0-5000 characters, optional)
    - created_at: Timestamp of task creation (UTC)
    - updated_at: Timestamp of last update (UTC)
    - user_id: Owner's UUID (foreign key to users.id)
    """

    __tablename__ = "tasks"

    # Primary key
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
        description="Unique identifier for the task"
    )

    # Task details
    title: str = Field(
        max_length=500,
        nullable=False,
        description="Task title (1-500 characters)"
    )

    description: Optional[str] = Field(
        default=None,
        max_length=5000,
        nullable=True,
        description="Optional task description (0-5000 characters)"
    )



    # Timestamps (UTC)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Timestamp of task creation (UTC)"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Timestamp of last update (UTC)",
        sa_column_kwargs={"onupdate": datetime.utcnow}
    )
    completed_at: Optional[datetime] = None

    created_by: uuid.UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="User who created this task"
    )
    
    # Legacy field for backward compatibility
    user_id: uuid.UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="User ID (same as created_by for compatibility)"
    )
    
    assigned_to: Optional[uuid.UUID] = Field(
        default=None,
        foreign_key="users.id",
        nullable=True,
        index=True,
        description="User to whom this task is assigned"
    )

    # Workspace integration (007-interactive-workspace-views) - OPTIONAL for personal tasks
    workspace_id: Optional[uuid.UUID] = Field(
    default=None,
        foreign_key="workspace.id",
        nullable=True,  # Allow personal tasks without workspace
        index=True,
        description="Foreign key to workspace.id (workspace this task belongs to) - NULL for personal tasks"
    )

    # New fields for Pro Task Engine
    parent_id: Optional[uuid.UUID] = Field(
        default=None,
        foreign_key="tasks.id",
        nullable=True,
        index=True,
        description="ID of the parent task for subtasks"
    )
    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM,
        nullable=False,
        description="Priority of the task"
    )
    status: TaskStatus = Field(
        default=TaskStatus.TO_DO,
        nullable=False,
        description="Status of the task"
    )
    due_date: Optional[datetime] = Field(
        default=None,
        nullable=True,
        description="Due date for the task"
    )
    recurrence_rule: Optional[str] = Field(
        default=None,
        nullable=True,
        description="Simplified string for recurrence patterns"
    )
    section_id: Optional[uuid.UUID] = Field(
        default=None,
        foreign_key="sections.id", # This will be created in T006
        nullable=True,
        index=True, # Added index for efficient filtering
        description="ID of the section this task belongs to"
    )
    project_id: Optional[uuid.UUID] = Field(
        default=None,
        foreign_key="project.id", # This will be created in T005
        nullable=True,
        index=True, # Added index for efficient filtering
        description="ID of the project this task belongs to"
    )

    # Relationships
    parent_task: Optional["Task"] = Relationship(
        back_populates="subtasks",
        sa_relationship_kwargs={"remote_side": "Task.id"}
    )
    subtasks: List["Task"] = Relationship(
        back_populates="parent_task",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    section: Optional["Section"] = Relationship(back_populates="tasks")
    project: Optional["Project"] = Relationship(back_populates="tasks")
    workspace: Optional["Workspace"] = Relationship(back_populates="tasks")
    activities: List["Activity"] = Relationship(back_populates="task")
    creator: "User" = Relationship(back_populates="created_tasks", sa_relationship_kwargs={"foreign_keys": "[Task.created_by]"})
    assignee: Optional["User"] = Relationship(back_populates="assigned_tasks", sa_relationship_kwargs={"foreign_keys": "[Task.assigned_to]"})

    class Config:
        """SQLModel configuration."""
        # Add composite index on (user_id, created_at) for efficient sorting
        # This will be added in the Alembic migration
        indexes = [
            {"fields": ["user_id"]},  # Single index on user_id
            {"fields": ["user_id", "created_at"]},  # Composite index for sorting
        ]

"""
Tool Executor Functions for OpenRouter Assistant

These functions wrap the service layer to provide simple tool execution
for the AI assistant.
"""

import logging
from typing import Dict, Any
from uuid import UUID
from datetime import datetime

from src.agents.context import AgentContext
from src.services.task_service import TaskService
from src.core.database import Session, engine
from src.models.user import User
from src.models.task import TaskStatus

logger = logging.getLogger(__name__)


async def add_task(context: AgentContext, title: str, description: str = "") -> Dict[str, Any]:
    """
    Add a new task for the user.
    
    Args:
        context: Agent context with user_id
        title: Task title
        description: Optional task description
    
    Returns:
        Dict with task details or error
    """
    try:
        with Session(engine) as session:
            # Get user
            user = session.get(User, context.user_id)
            if not user:
                return {"error": "User not found"}
            
            # Create task without workspace (personal task)
            task = TaskService.create_task_simple(
                session=session,
                user_id=str(context.user_id),
                title=title,
                description=description
            )
            
            return {
                "success": True,
                "task_id": str(task.id),
                "title": task.title,
                "description": task.description,
                "status": task.status.value if task.status else "todo"
            }
    except Exception as e:
        logger.error(f"Error adding task: {e}")
        return {"error": str(e)}


async def list_tasks(context: AgentContext) -> Dict[str, Any]:
    """
    List all tasks for the user.
    
    Args:
        context: Agent context with user_id
    
    Returns:
        Dict with list of tasks or error
    """
    try:
        with Session(engine) as session:
            tasks = TaskService.get_user_tasks(
                session=session,
                user_id=str(context.user_id)
            )
            
            task_list = [
                {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description or "",
                    "status": task.status.value if task.status else "todo",
                    "priority": task.priority.value if task.priority else "medium",
                    "created_at": task.created_at.isoformat() if task.created_at else None
                }
                for task in tasks
            ]
            
            return {
                "success": True,
                "count": len(task_list),
                "tasks": task_list
            }
    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        return {"error": str(e)}


async def complete_task(context: AgentContext, task_id: str) -> Dict[str, Any]:
    """
    Mark a task as complete.
    
    Args:
        context: Agent context with user_id
        task_id: UUID of the task to complete
    
    Returns:
        Dict with success status or error
    """
    try:
        with Session(engine) as session:
            task = TaskService.get_task_by_id(
                session=session,
                task_id=task_id,
                user_id=str(context.user_id)
            )
            
            if not task:
                return {"error": "Task not found"}
            
            # Update task status to DONE
            task.status = TaskStatus.DONE
            task.completed_at = datetime.utcnow()
            session.add(task)
            session.commit()
            session.refresh(task)
            
            return {
                "success": True,
                "task_id": str(task.id),
                "title": task.title,
                "status": "completed"
            }
    except Exception as e:
        logger.error(f"Error completing task: {e}")
        return {"error": str(e)}


async def delete_task(context: AgentContext, task_id: str) -> Dict[str, Any]:
    """
    Delete a task.
    
    Args:
        context: Agent context with user_id
        task_id: UUID of the task to delete
    
    Returns:
        Dict with success status or error
    """
    try:
        with Session(engine) as session:
            task = TaskService.get_task_by_id(
                session=session,
                task_id=task_id,
                user_id=str(context.user_id)
            )
            
            if not task:
                return {"error": "Task not found"}
            
            session.delete(task)
            session.commit()
            
            return {
                "success": True,
                "task_id": task_id,
                "message": f"Task '{task.title}' deleted successfully"
            }
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        return {"error": str(e)}


async def update_task(
    context: AgentContext,
    task_id: str,
    title: str = None,
    description: str = None,
    status: str = None,
    priority: str = None
) -> Dict[str, Any]:
    """
    Update a task.
    
    Args:
        context: Agent context with user_id
        task_id: UUID of the task to update
        title: New title (optional)
        description: New description (optional)
        status: New status (optional)
        priority: New priority (optional)
    
    Returns:
        Dict with updated task details or error
    """
    try:
        with Session(engine) as session:
            task = TaskService.get_task_by_id(
                session=session,
                task_id=task_id,
                user_id=str(context.user_id)
            )
            
            if not task:
                return {"error": "Task not found"}
            
            # Update fields
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            if status is not None:
                task.status = status
            if priority is not None:
                task.priority = priority
            
            session.add(task)
            session.commit()
            session.refresh(task)
            
            return {
                "success": True,
                "task_id": str(task.id),
                "title": task.title,
                "description": task.description,
                "status": task.status.value if task.status else "todo",
                "priority": task.priority.value if task.priority else "medium"
            }
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        return {"error": str(e)}


# Tool name to function mapping
TOOL_FUNCTIONS = {
    "add_task": add_task,
    "list_tasks": list_tasks,
    "complete_task": complete_task,
    "delete_task": delete_task,
    "update_task": update_task
}


def get_tool_function(tool_name: str):
    """Get the executor function for a tool by name."""
    return TOOL_FUNCTIONS.get(tool_name)

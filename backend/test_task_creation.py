"""
Test task creation and retrieval to debug the issue.
"""

import sys
sys.path.insert(0, 'src')

from sqlmodel import Session, select
from src.core.database import engine
from src.models.task import Task
from src.models.user import User
from uuid import UUID

def test_tasks():
    """Check tasks in database."""
    
    with Session(engine) as session:
        # Get all users
        users = session.exec(select(User)).all()
        print(f"Total users in database: {len(users)}\n")
        
        for user in users:
            print(f"User: {user.email}")
            print(f"  ID: {user.id}")
            
            # Get tasks for this user
            tasks = session.exec(
                select(Task).where(Task.user_id == user.id)
            ).all()
            
            print(f"  Tasks (user_id): {len(tasks)}")
            for task in tasks:
                print(f"    - {task.title} (id: {task.id})")
                print(f"      user_id: {task.user_id}")
                print(f"      created_by: {task.created_by}")
            
            # Also check by created_by
            tasks_by_created = session.exec(
                select(Task).where(Task.created_by == user.id)
            ).all()
            
            print(f"  Tasks (created_by): {len(tasks_by_created)}")
            for task in tasks_by_created:
                print(f"    - {task.title} (id: {task.id})")
                print(f"      user_id: {task.user_id}")
                print(f"      created_by: {task.created_by}")
            
            print()
        
        # Get all tasks
        all_tasks = session.exec(select(Task)).all()
        print(f"\nTotal tasks in database: {len(all_tasks)}")
        for task in all_tasks:
            print(f"  - {task.title}")
            print(f"    user_id: {task.user_id}")
            print(f"    created_by: {task.created_by}")
            print(f"    workspace_id: {task.workspace_id}")

if __name__ == "__main__":
    test_tasks()

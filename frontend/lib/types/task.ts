// frontend/lib/types/task.ts
export type TaskStatus = "TO_DO" | "IN_PROGRESS" | "REVIEW" | "DONE";
export type TaskPriority = "LOW" | "MEDIUM" | "HIGH" | "URGENT";

export interface Task {
  id: string;
  title: string;
  description: string | null;
  priority: TaskPriority;
  status: TaskStatus;
  workspace_id: string | null; // Nullable for personal tasks
  project_id: string | null;
  created_by: string;
  assigned_to: string | null;
  created_at: string; // ISO date string
  updated_at: string; // ISO date string
  completed_at: string | null;
  is_completed?: boolean; // For backward compatibility
  user_id?: string; // For backward compatibility
}

export interface TaskRead extends Task {
    creator_email?: string;
    assignee_email?: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority?: TaskPriority;
  status?: TaskStatus;
  project_id?: string;
  assigned_to?: string;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  priority?: TaskPriority;
  status?: TaskStatus;
  project_id?: string;
  assigned_to?: string;
}

// Alias for backward compatibility
export type TaskCreateInput = TaskCreate;
export type TaskUpdateInput = TaskUpdate;
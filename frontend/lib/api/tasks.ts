/**
 * Task API methods.
 *
 * All task CRUD operations with workspace context.
 */

import { apiClient } from "./client";
import { Task, TaskCreateInput, TaskUpdateInput } from "../types/task";

export const taskApi = {
  /**
   * Get all tasks (workspace or personal).
   *
   * GET /api/workspaces/{workspace_id}/tasks (if workspace provided)
   * GET /api/{user_id}/tasks (if no workspace - personal tasks)
   */
  async list(workspaceId?: string): Promise<Task[]> {
    if (!workspaceId) {
      // Try to get from localStorage
      if (typeof window !== "undefined") {
        workspaceId = localStorage.getItem("current_workspace_id") || undefined;
      }
    }
    
    if (workspaceId) {
      // Workspace tasks
      try {
        return await apiClient.get<Task[]>(`/api/workspaces/${workspaceId}/tasks`);
      } catch (error) {
        console.error("Failed to fetch workspace tasks:", error);
        return [];
      }
    } else {
      // Personal tasks (no workspace)
      try {
        const userId = apiClient.getUserId();
        if (!userId) {
          console.warn("No user ID found, returning empty task list");
          return [];
        }
        return await apiClient.get<Task[]>(`/api/${userId}/tasks`);
      } catch (error) {
        console.error("Failed to fetch personal tasks:", error);
        return [];
      }
    }
  },

  /**
   * Create a new task (workspace or personal).
   *
   * POST /api/workspaces/{workspace_id}/tasks (if workspace provided)
   * POST /api/{user_id}/tasks (if no workspace - personal task)
   */
  async create(data: TaskCreateInput, workspaceId?: string): Promise<Task> {
    // Get workspace ID if not provided
    if (!workspaceId && typeof window !== "undefined") {
      workspaceId = localStorage.getItem("current_workspace_id") || undefined;
    }
    
    if (workspaceId) {
      // Create workspace task
      return apiClient.post<Task>(`/api/workspaces/${workspaceId}/tasks`, data);
    } else {
      // Create personal task (no workspace)
      const userId = apiClient.getUserId();
      if (!userId) throw new Error("User not authenticated");
      
      return apiClient.post<Task>(`/api/${userId}/tasks`, data);
    }
  },

  /**
   * Get a single task by ID.
   *
   * GET /api/{user_id}/tasks/{task_id}
   */
  async get(taskId: string): Promise<Task> {
    const userId = apiClient.getUserId();
    if (!userId) throw new Error("User not authenticated");

    return apiClient.get<Task>(`/api/${userId}/tasks/${taskId}`);
  },

  /**
   * Update an existing task.
   *
   * PUT /api/{user_id}/tasks/{task_id}
   */
  async update(taskId: string, data: TaskUpdateInput): Promise<Task> {
    const userId = apiClient.getUserId();
    if (!userId) throw new Error("User not authenticated");

    return apiClient.put<Task>(`/api/${userId}/tasks/${taskId}`, data);
  },

  /**
   * Delete a task.
   *
   * DELETE /api/{user_id}/tasks/{task_id}
   */
  async delete(taskId: string): Promise<void> {
    const userId = apiClient.getUserId();
    if (!userId) throw new Error("User not authenticated");

    return apiClient.delete<void>(`/api/${userId}/tasks/${taskId}`);
  },

  /**
   * Toggle task completion status.
   *
   * PATCH /api/{user_id}/tasks/{task_id}/complete
   */
  async toggleComplete(taskId: string): Promise<Task> {
    const userId = apiClient.getUserId();
    if (!userId) throw new Error("User not authenticated");

    return apiClient.patch<Task>(`/api/${userId}/tasks/${taskId}/complete`);
  },

  /**
   * Update task status (for Kanban board).
   *
   * PATCH /api/workspaces/{workspace_id}/tasks/{task_id}/status
   */
  async updateStatus(workspaceId: string, taskId: string, status: string): Promise<Task> {
    return apiClient.patch<Task>(
      `/api/workspaces/${workspaceId}/tasks/${taskId}/status`,
      { status }
    );
  },
};

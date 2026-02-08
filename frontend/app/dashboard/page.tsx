/**
 * Dashboard Page - Overview and quick stats.
 *
 * Protected route - requires authentication.
 */

"use client";

import { useEffect, useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import { auth } from "@/lib/api/auth";
import { useTasks } from "@/lib/hooks/useTasks";
import { PageTransition } from "@/components/ui/PageTransition";
import { SkeletonCard } from "@/components/SkeletonCard";
import {
  LayoutDashboard,
  CheckCircle2,
  Clock,
  AlertCircle,
  TrendingUp,
  ListTodo,
  Grid3x3,
  BarChart3,
  Activity,
  ArrowRight,
  Target,
} from "lucide-react";
import Link from "next/link";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<{ email: string } | null>(null);
  const [workspaceId, setWorkspaceId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Route protection and workspace loading
  useEffect(() => {
    const currentUser = auth.getUser();
    if (!currentUser) {
      router.push("/login");
      return;
    }
    setUser(currentUser);

    const wsId = localStorage.getItem("current_workspace_id");
    if (wsId) {
      setWorkspaceId(wsId);
      setLoading(false);
    } else {
      const fetchWorkspace = async () => {
        try {
          const token = auth.getToken();
          if (!token) {
            router.push("/login");
            return;
          }

          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/workspaces`, {
            headers: { Authorization: `Bearer ${token}` },
          });

          if (response.ok) {
            const workspaces = await response.json();
            if (workspaces.length > 0) {
              const wsId = workspaces[0].id;
              setWorkspaceId(wsId);
              localStorage.setItem("current_workspace_id", wsId);
            }
            // No redirect if no workspace - allow personal tasks
          }
        } catch (error) {
          console.error("Failed to fetch workspace:", error);
        } finally {
          setLoading(false);
        }
      };

      fetchWorkspace();
    }
  }, [router]);

  const { tasks, loading: tasksLoading } = useTasks(workspaceId || undefined);

  // Calculate stats
  const stats = useMemo(() => {
    const total = tasks.length;
    const completed = tasks.filter((t) => t.status === "DONE").length;
    const inProgress = tasks.filter((t) => t.status === "IN_PROGRESS").length;
    const todo = tasks.filter((t) => t.status === "TO_DO").length;
    const review = tasks.filter((t) => t.status === "REVIEW").length;
    const highPriority = tasks.filter(
      (t) => t.priority === "HIGH" || t.priority === "URGENT"
    ).length;
    const completionRate = total > 0 ? Math.round((completed / total) * 100) : 0;

    return {
      total,
      completed,
      inProgress,
      todo,
      review,
      highPriority,
      completionRate,
    };
  }, [tasks]);

  // Recent tasks (last 5)
  const recentTasks = useMemo(() => {
    return [...tasks]
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      .slice(0, 5);
  }, [tasks]);

  // Status distribution for chart
  const statusData = [
    { name: "To Do", value: stats.todo, color: "#6B7280" },
    { name: "In Progress", value: stats.inProgress, color: "#3B82F6" },
    { name: "Review", value: stats.review, color: "#F59E0B" },
    { name: "Done", value: stats.completed, color: "#10B981" },
  ];

  if (!user || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <PageTransition>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-900 dark:via-slate-900 dark:to-gray-900">
        {/* Decorative Background */}
        <div className="fixed inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
        </div>

        {/* Header */}
        <div className="relative bg-white/70 dark:bg-gray-800/70 backdrop-blur-xl border-b border-gray-200/50 dark:border-gray-700/50 shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                  <LayoutDashboard className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    Dashboard
                  </h1>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Welcome back, {user.email}
                  </p>
                </div>
              </div>
              {!workspaceId && (
                <Link
                  href="/dashboard/workspaces/create"
                  className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-lg shadow-lg transition-all font-semibold text-sm"
                >
                  + Create Workspace
                </Link>
              )}
            </div>
          </div>
        </div>

        {/* Main Content */}
        <main className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {tasksLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
            </div>
          ) : (
            <>
              {/* Stats Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                {/* Total Tasks */}
                <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md rounded-2xl shadow-xl border border-gray-200/50 dark:border-gray-700/50 p-6 hover:shadow-2xl transition-all duration-300 hover:scale-105">
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center">
                      <Target className="w-6 h-6 text-white" />
                    </div>
                  </div>
                  <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
                    {stats.total}
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Total Tasks</p>
                </div>

                {/* Completed */}
                <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md rounded-2xl shadow-xl border border-gray-200/50 dark:border-gray-700/50 p-6 hover:shadow-2xl transition-all duration-300 hover:scale-105">
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-green-600 rounded-xl flex items-center justify-center">
                      <CheckCircle2 className="w-6 h-6 text-white" />
                    </div>
                  </div>
                  <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
                    {stats.completed}
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {stats.completionRate}% Complete
                  </p>
                </div>

                {/* In Progress */}
                <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md rounded-2xl shadow-xl border border-gray-200/50 dark:border-gray-700/50 p-6 hover:shadow-2xl transition-all duration-300 hover:scale-105">
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-yellow-500 to-yellow-600 rounded-xl flex items-center justify-center">
                      <Clock className="w-6 h-6 text-white" />
                    </div>
                  </div>
                  <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
                    {stats.inProgress}
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">In Progress</p>
                </div>

                {/* High Priority */}
                <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md rounded-2xl shadow-xl border border-gray-200/50 dark:border-gray-700/50 p-6 hover:shadow-2xl transition-all duration-300 hover:scale-105">
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-red-500 to-red-600 rounded-xl flex items-center justify-center">
                      <AlertCircle className="w-6 h-6 text-white" />
                    </div>
                  </div>
                  <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
                    {stats.highPriority}
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">High Priority</p>
                </div>
              </div>

              {/* Quick Actions & Overview */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
                {/* Quick Actions */}
                <div className="lg:col-span-1">
                  <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md rounded-2xl shadow-xl border border-gray-200/50 dark:border-gray-700/50 p-6">
                    <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
                      Quick Actions
                    </h3>
                    <div className="space-y-3">
                      <Link
                        href="/dashboard/tasks"
                        className="flex items-center justify-between p-4 bg-gradient-to-r from-blue-50 to-blue-100 dark:from-blue-900/30 dark:to-blue-800/30 rounded-xl hover:shadow-md transition-all group"
                      >
                        <div className="flex items-center gap-3">
                          <ListTodo className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                          <span className="font-medium text-gray-900 dark:text-white">
                            View All Tasks
                          </span>
                        </div>
                        <ArrowRight className="w-5 h-5 text-blue-600 dark:text-blue-400 group-hover:translate-x-1 transition-transform" />
                      </Link>

                      <Link
                        href="/dashboard/kanban"
                        className="flex items-center justify-between p-4 bg-gradient-to-r from-purple-50 to-purple-100 dark:from-purple-900/30 dark:to-purple-800/30 rounded-xl hover:shadow-md transition-all group"
                      >
                        <div className="flex items-center gap-3">
                          <Grid3x3 className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                          <span className="font-medium text-gray-900 dark:text-white">
                            Kanban Board
                          </span>
                        </div>
                        <ArrowRight className="w-5 h-5 text-purple-600 dark:text-purple-400 group-hover:translate-x-1 transition-transform" />
                      </Link>

                      <Link
                        href="/dashboard/analytics"
                        className="flex items-center justify-between p-4 bg-gradient-to-r from-green-50 to-green-100 dark:from-green-900/30 dark:to-green-800/30 rounded-xl hover:shadow-md transition-all group"
                      >
                        <div className="flex items-center gap-3">
                          <BarChart3 className="w-5 h-5 text-green-600 dark:text-green-400" />
                          <span className="font-medium text-gray-900 dark:text-white">
                            Analytics
                          </span>
                        </div>
                        <ArrowRight className="w-5 h-5 text-green-600 dark:text-green-400 group-hover:translate-x-1 transition-transform" />
                      </Link>

                      <Link
                        href="/dashboard/activity"
                        className="flex items-center justify-between p-4 bg-gradient-to-r from-orange-50 to-orange-100 dark:from-orange-900/30 dark:to-orange-800/30 rounded-xl hover:shadow-md transition-all group"
                      >
                        <div className="flex items-center gap-3">
                          <Activity className="w-5 h-5 text-orange-600 dark:text-orange-400" />
                          <span className="font-medium text-gray-900 dark:text-white">
                            Activity Feed
                          </span>
                        </div>
                        <ArrowRight className="w-5 h-5 text-orange-600 dark:text-orange-400 group-hover:translate-x-1 transition-transform" />
                      </Link>
                    </div>
                  </div>
                </div>

                {/* Status Distribution Chart */}
                <div className="lg:col-span-2">
                  <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md rounded-2xl shadow-xl border border-gray-200/50 dark:border-gray-700/50 p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                        Task Distribution
                      </h3>
                      <Link
                        href="/dashboard/analytics"
                        className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
                      >
                        View Details
                      </Link>
                    </div>
                    {stats.total > 0 ? (
                      <ResponsiveContainer width="100%" height={250}>
                        <PieChart>
                          <Pie
                            data={statusData}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ name, percent }) =>
                              `${name}: ${((percent || 0) * 100).toFixed(0)}%`
                            }
                            outerRadius={80}
                            fill="#8884d8"
                            dataKey="value"
                          >
                            {statusData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                          </Pie>
                          <Tooltip />
                        </PieChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="flex items-center justify-center h-64 text-gray-500 dark:text-gray-400">
                        No tasks to display
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Recent Tasks */}
              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md rounded-2xl shadow-xl border border-gray-200/50 dark:border-gray-700/50 p-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                    Recent Tasks
                  </h3>
                  <Link
                    href="/dashboard/tasks"
                    className="text-sm text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1"
                  >
                    View All
                    <ArrowRight className="w-4 h-4" />
                  </Link>
                </div>
                {recentTasks.length > 0 ? (
                  <div className="space-y-3">
                    {recentTasks.map((task) => (
                      <div
                        key={task.id}
                        className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                      >
                        <div className="flex items-center gap-3 flex-1 min-w-0">
                          <div
                            className={`w-2 h-2 rounded-full flex-shrink-0 ${
                              task.status === "DONE"
                                ? "bg-green-500"
                                : task.status === "IN_PROGRESS"
                                ? "bg-blue-500"
                                : task.status === "REVIEW"
                                ? "bg-yellow-500"
                                : "bg-gray-500"
                            }`}
                          />
                          <div className="flex-1 min-w-0">
                            <p className="font-medium text-gray-900 dark:text-white truncate">
                              {task.title}
                            </p>
                            <p className="text-xs text-gray-600 dark:text-gray-400">
                              {task.status.replace("_", " ")} • {task.priority}
                            </p>
                          </div>
                        </div>
                        <span className="text-xs text-gray-500 dark:text-gray-400 flex-shrink-0 ml-4">
                          {new Date(task.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                    <ListTodo className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p>No tasks yet. Create your first task to get started!</p>
                    <Link
                      href="/dashboard/tasks"
                      className="inline-block mt-4 px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all"
                    >
                      Create Task
                    </Link>
                  </div>
                )}
              </div>
            </>
          )}
        </main>
      </div>
    </PageTransition>
  );
}

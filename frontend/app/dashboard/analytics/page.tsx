"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { auth } from "@/lib/api/auth";
import { useTasks } from "@/lib/hooks/useTasks";
import { SkeletonCard } from "@/components/SkeletonCard";
import {
  BarChart3,
  TrendingUp,
  CheckCircle2,
  Clock,
  AlertCircle,
  Target,
  Calendar,
  Activity,
} from "lucide-react";
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

export default function AnalyticsPage() {
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
          const token = localStorage.getItem("access_token");
          if (!token) {
            router.push("/login");
            return;
          }

          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/workspaces`, {
            headers: { Authorization: `Bearer ${token}` },
          });

          if (response.ok) {
            const workspaces = await response.json();
            if (workspaces.length > 0) {
              const wsId = workspaces[0].id;
              setWorkspaceId(wsId);
              localStorage.setItem("current_workspace_id", wsId);
            }
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

  // Calculate analytics data
  const analytics = {
    total: tasks.length,
    completed: tasks.filter((t) => t.status === "DONE").length,
    inProgress: tasks.filter((t) => t.status === "IN_PROGRESS").length,
    todo: tasks.filter((t) => t.status === "TO_DO").length,
    review: tasks.filter((t) => t.status === "REVIEW").length,
    highPriority: tasks.filter((t) => t.priority === "HIGH" || t.priority === "URGENT").length,
    completionRate: tasks.length > 0 ? Math.round((tasks.filter((t) => t.status === "DONE").length / tasks.length) * 100) : 0,
  };

  // Status distribution data
  const statusData = [
    { name: "To Do", value: analytics.todo, color: "#6B7280" },
    { name: "In Progress", value: analytics.inProgress, color: "#3B82F6" },
    { name: "Review", value: analytics.review, color: "#F59E0B" },
    { name: "Done", value: analytics.completed, color: "#10B981" },
  ];

  // Priority distribution data
  const priorityData = [
    { name: "Low", count: tasks.filter((t) => t.priority === "LOW").length },
    { name: "Medium", count: tasks.filter((t) => t.priority === "MEDIUM").length },
    { name: "High", count: tasks.filter((t) => t.priority === "HIGH").length },
    { name: "Urgent", count: tasks.filter((t) => t.priority === "URGENT").length },
  ];

  // Weekly completion trend (last 7 days)
  const getTrendData = () => {
    const last7Days = Array.from({ length: 7 }, (_, i) => {
      const date = new Date();
      date.setDate(date.getDate() - (6 - i));
      return date.toISOString().split("T")[0];
    });

    return last7Days.map((date) => {
      const completed = tasks.filter((t) => {
        if (!t.completed_at) return false;
        const completedDate = new Date(t.completed_at).toISOString().split("T")[0];
        return completedDate === date;
      }).length;

      return {
        date: new Date(date).toLocaleDateString("en-US", { month: "short", day: "numeric" }),
        completed,
      };
    });
  };

  const trendData = getTrendData();

  if (!user || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-w-7xl w-full px-4">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
      </div>
    );
  }

  if (!workspaceId) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
        <div className="bg-white/80 backdrop-blur-md rounded-2xl shadow-xl border border-gray-200/50 p-8 text-center max-w-md">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">No Workspace Found</h2>
          <p className="text-gray-600 mb-6">
            Please create a workspace to view analytics.
          </p>
          <button
            onClick={() => router.push("/dashboard")}
            className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-xl shadow-lg transition-all font-semibold"
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-900 dark:via-slate-900 dark:to-gray-900">
      {/* Decorative Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
      </div>

      {/* Header */}
      <div className="relative bg-white/70 dark:bg-gray-800/70 backdrop-blur-xl border-b border-gray-200/50 dark:border-gray-700/50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
              <BarChart3 className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Analytics Dashboard
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Track your productivity and task insights
              </p>
            </div>
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
              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md rounded-2xl shadow-xl border border-gray-200/50 dark:border-gray-700/50 p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center">
                    <Target className="w-6 h-6 text-white" />
                  </div>
                  <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Total</span>
                </div>
                <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
                  {analytics.total}
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">All tasks</p>
              </div>

              {/* Completed Tasks */}
              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md rounded-2xl shadow-xl border border-gray-200/50 dark:border-gray-700/50 p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-green-600 rounded-xl flex items-center justify-center">
                    <CheckCircle2 className="w-6 h-6 text-white" />
                  </div>
                  <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Done</span>
                </div>
                <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
                  {analytics.completed}
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {analytics.completionRate}% completion rate
                </p>
              </div>

              {/* In Progress */}
              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md rounded-2xl shadow-xl border border-gray-200/50 dark:border-gray-700/50 p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-yellow-500 to-yellow-600 rounded-xl flex items-center justify-center">
                    <Clock className="w-6 h-6 text-white" />
                  </div>
                  <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Active</span>
                </div>
                <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
                  {analytics.inProgress}
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">In progress</p>
              </div>

              {/* High Priority */}
              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md rounded-2xl shadow-xl border border-gray-200/50 dark:border-gray-700/50 p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-red-500 to-red-600 rounded-xl flex items-center justify-center">
                    <AlertCircle className="w-6 h-6 text-white" />
                  </div>
                  <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Urgent</span>
                </div>
                <div className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
                  {analytics.highPriority}
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">High priority</p>
              </div>
            </div>

            {/* Charts Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Status Distribution Pie Chart */}
              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md rounded-2xl shadow-xl border border-gray-200/50 dark:border-gray-700/50 p-6">
                <div className="flex items-center gap-3 mb-6">
                  <Activity className="w-5 h-5 text-blue-600" />
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                    Status Distribution
                  </h3>
                </div>
                <ResponsiveContainer width="100%" height={300}>
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
              </div>

              {/* Priority Distribution Bar Chart */}
              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md rounded-2xl shadow-xl border border-gray-200/50 dark:border-gray-700/50 p-6">
                <div className="flex items-center gap-3 mb-6">
                  <AlertCircle className="w-5 h-5 text-orange-600" />
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                    Priority Distribution
                  </h3>
                </div>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={priorityData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis dataKey="name" stroke="#6b7280" />
                    <YAxis stroke="#6b7280" />
                    <Tooltip />
                    <Bar dataKey="count" fill="#8b5cf6" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Completion Trend Line Chart */}
              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md rounded-2xl shadow-xl border border-gray-200/50 dark:border-gray-700/50 p-6 lg:col-span-2">
                <div className="flex items-center gap-3 mb-6">
                  <TrendingUp className="w-5 h-5 text-green-600" />
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                    Completion Trend (Last 7 Days)
                  </h3>
                </div>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={trendData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis dataKey="date" stroke="#6b7280" />
                    <YAxis stroke="#6b7280" />
                    <Tooltip />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="completed"
                      stroke="#10b981"
                      strokeWidth={3}
                      dot={{ fill: "#10b981", r: 6 }}
                      activeDot={{ r: 8 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Empty State */}
            {tasks.length === 0 && (
              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md rounded-2xl shadow-xl border border-gray-200/50 dark:border-gray-700/50 p-12 text-center mt-8">
                <div className="w-20 h-20 bg-gradient-to-br from-blue-100 to-purple-100 dark:from-blue-900/30 dark:to-purple-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
                  <BarChart3 className="w-10 h-10 text-blue-600 dark:text-blue-400" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                  No Data Yet
                </h3>
                <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-md mx-auto">
                  Create some tasks to see your analytics and productivity insights.
                </p>
                <button
                  onClick={() => router.push("/dashboard/tasks")}
                  className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-xl shadow-lg hover:shadow-xl transition-all font-semibold"
                >
                  <Target size={20} />
                  Create Your First Task
                </button>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}

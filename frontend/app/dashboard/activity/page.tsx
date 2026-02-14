"use client";

import { useEffect, useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import { auth } from "@/lib/api/auth";
import { useTasks } from "@/lib/hooks/useTasks";
import { SkeletonCard } from "@/components/SkeletonCard";
import { PageTransition } from "@/components/ui/PageTransition";
import { Activity, Clock, CheckCircle2, Plus, Edit, Trash2 } from "lucide-react";

export default function ActivityPage() {
  const router = useRouter();
  const [user, setUser] = useState<{ email: string } | null>(null);
  const { tasks, loading } = useTasks();

  // Route protection
  useEffect(() => {
    const currentUser = auth.getUser();
    if (!currentUser) {
      router.push("/login");
      return;
    }
    setUser(currentUser);
  }, [router]);

  // Generate activity feed from tasks
  const activities = useMemo(() => {
    const activityList = tasks.map((task) => {
      const createdDate = new Date(task.created_at);
      const updatedDate = new Date(task.updated_at);
      const isUpdated = updatedDate.getTime() !== createdDate.getTime();

      return {
        id: task.id,
        type: task.status === "DONE" ? "completed" : isUpdated ? "updated" : "created",
        task: task.title,
        status: task.status,
        timestamp: isUpdated ? updatedDate : createdDate,
        date: isUpdated ? task.updated_at : task.created_at,
      };
    });

    // Sort by timestamp (newest first)
    return activityList.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
  }, [tasks]);

  const getActivityIcon = (type: string) => {
    switch (type) {
      case "completed":
        return <CheckCircle2 className="w-5 h-5 text-green-500" />;
      case "updated":
        return <Edit className="w-5 h-5 text-blue-500" />;
      case "created":
        return <Plus className="w-5 h-5 text-purple-500" />;
      default:
        return <Activity className="w-5 h-5 text-gray-500" />;
    }
  };

  const getActivityText = (type: string, task: string) => {
    switch (type) {
      case "completed":
        return (
          <>
            Completed task <span className="font-semibold">"{task}"</span>
          </>
        );
      case "updated":
        return (
          <>
            Updated task <span className="font-semibold">"{task}"</span>
          </>
        );
      case "created":
        return (
          <>
            Created task <span className="font-semibold">"{task}"</span>
          </>
        );
      default:
        return task;
    }
  };

  const formatTimestamp = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? "s" : ""} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? "s" : ""} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? "s" : ""} ago`;
    
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: date.getFullYear() !== now.getFullYear() ? "numeric" : undefined,
    });
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <PageTransition>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-900 dark:via-slate-900 dark:to-gray-900">
        {/* Header */}
        <div className="relative bg-white/70 dark:bg-gray-800/70 backdrop-blur-xl border-b border-gray-200/50 dark:border-gray-700/50 shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-br from-orange-500 to-red-600 rounded-xl flex items-center justify-center shadow-lg">
                <Activity className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-4xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">
                  Activity
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Track your recent task activities
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <main className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {loading && activities.length === 0 ? (
            <div className="space-y-4">
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
            </div>
          ) : activities.length === 0 ? (
            <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md rounded-2xl shadow-xl border border-gray-200/50 dark:border-gray-700/50 p-12 text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-orange-100 to-red-100 dark:from-orange-900/30 dark:to-red-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
                <Activity className="w-10 h-10 text-orange-600 dark:text-orange-400" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                No activity yet
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                Start creating and managing tasks to see your activity here
              </p>
            </div>
          ) : (
            <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md rounded-2xl shadow-xl border border-gray-200/50 dark:border-gray-700/50 overflow-hidden">
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Recent Activity
                </h2>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  {activities.length} {activities.length === 1 ? "activity" : "activities"}
                </p>
              </div>

              <div className="divide-y divide-gray-200 dark:divide-gray-700">
                {activities.map((activity) => (
                  <div
                    key={activity.id}
                    className="p-6 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                  >
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0 w-10 h-10 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center">
                        {getActivityIcon(activity.type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-gray-900 dark:text-white">
                          {getActivityText(activity.type, activity.task)}
                        </p>
                        <div className="flex items-center gap-2 mt-1">
                          <Clock className="w-3 h-3 text-gray-400" />
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            {formatTimestamp(activity.date)}
                          </p>
                          <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400">
                            {activity.status.replace("_", " ")}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </main>
      </div>
    </PageTransition>
  );
}

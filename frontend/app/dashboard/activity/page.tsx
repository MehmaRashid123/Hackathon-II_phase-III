"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { auth } from "@/lib/api/auth";
import { ActivityFeed } from "@/components/activity/ActivityFeed";
import { SkeletonCard } from "@/components/SkeletonCard";
import { Activity, Clock, TrendingUp } from "lucide-react";

export default function ActivityPage() {
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

  if (!user || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
        <div className="grid grid-cols-1 gap-4 max-w-3xl w-full px-4">
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
            Please create a workspace to view activity feed.
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
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
              <Activity className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Activity Feed
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Track all workspace activities in real-time
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md rounded-xl shadow-lg border border-gray-200/50 dark:border-gray-700/50 p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
                <Activity className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="text-xs text-gray-600 dark:text-gray-400">Live Updates</p>
                <p className="text-sm font-semibold text-gray-900 dark:text-white">Real-time</p>
              </div>
            </div>
          </div>

          <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md rounded-xl shadow-lg border border-gray-200/50 dark:border-gray-700/50 p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Clock className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="text-xs text-gray-600 dark:text-gray-400">History</p>
                <p className="text-sm font-semibold text-gray-900 dark:text-white">Last 50 events</p>
              </div>
            </div>
          </div>

          <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md rounded-xl shadow-lg border border-gray-200/50 dark:border-gray-700/50 p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-green-600 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="text-xs text-gray-600 dark:text-gray-400">Tracking</p>
                <p className="text-sm font-semibold text-gray-900 dark:text-white">All actions</p>
              </div>
            </div>
          </div>
        </div>

        {/* Activity Feed */}
        <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md rounded-2xl shadow-xl border border-gray-200/50 dark:border-gray-700/50 p-6">
          <ActivityFeed workspaceId={workspaceId} />
        </div>
      </main>
    </div>
  );
}

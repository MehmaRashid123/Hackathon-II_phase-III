"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { auth } from "@/lib/api/auth";
import { KanbanBoard } from "@/components/kanban/KanbanBoard";
import { SkeletonCard } from "@/components/SkeletonCard";

export default function KanbanPage() {
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

    // Get workspace ID from localStorage
    const wsId = localStorage.getItem("current_workspace_id");
    if (wsId) {
      setWorkspaceId(wsId);
      setLoading(false);
    } else {
      // Fetch workspace if not in localStorage
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

  // Show loading while checking auth
  if (!user || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 max-w-7xl w-full px-4">
          <SkeletonCard />
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
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Workspace Optional</h2>
          <p className="text-gray-600 mb-6">
            You can use the Kanban board with personal tasks or create a workspace for team collaboration.
          </p>
          <div className="flex gap-3 justify-center">
            <button
              onClick={() => router.push("/dashboard/tasks")}
              className="px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white rounded-xl shadow-lg transition-all font-semibold"
            >
              Use Personal Tasks
            </button>
            <button
              onClick={() => router.push("/dashboard/workspaces/create")}
              className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-xl shadow-lg transition-all font-semibold"
            >
              Create Workspace
            </button>
          </div>
        </div>
      </div>
    );
  }

  return <KanbanBoard workspaceId={workspaceId} />;
}

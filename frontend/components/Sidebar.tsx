import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ChevronFirst, ChevronLast, LayoutDashboard, ListTodo, Columns3, ChartBar, Activity, Briefcase, MessageSquare, CreditCard } from 'lucide-react';
import { cn } from '@/lib/utils';

export function Sidebar({ isOpen, setIsOpen }: { isOpen: boolean; setIsOpen: (isOpen: boolean) => void }) {
  const [isMobile, setIsMobile] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const sidebarWidthClass = isMobile ? 'w-64' : (isOpen ? 'w-64' : 'w-20');
  const sidebarTransformClass = isMobile ? (isOpen ? 'translate-x-0' : '-translate-x-full') : 'translate-x-0';
  const sidebarPositionClass = isMobile ? 'fixed inset-y-0 left-0 z-40' : 'relative';

  const isActive = (href: string) => pathname === href;

  const navItems = [
    { href: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { href: '/dashboard/tasks', icon: ListTodo, label: 'Tasks' },
    { href: '/dashboard/kanban', icon: Columns3, label: 'Kanban' },
    { href: '/dashboard/ai-assistant', icon: MessageSquare, label: 'AI Assistant' },
    { href: '/dashboard/analytics', icon: ChartBar, label: 'Analytics' },
    { href: '/dashboard/activity', icon: Activity, label: 'Activity' },
    { href: '/dashboard/billing', icon: CreditCard, label: 'Billing' },
  ];

  return (
    <>
      <div
        className={`flex flex-col h-full bg-gray-800 text-white shadow-lg transition-all duration-300 ease-in-out ${sidebarWidthClass} ${sidebarTransformClass} ${sidebarPositionClass}`}
      >
        {/* Header with Logo */}
        <div className={cn(
            "p-4 border-b border-gray-700 flex items-center justify-between gap-2",
            !isOpen && "justify-center"
        )}>
            {isOpen ? (
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                  <Briefcase className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="text-lg font-bold">TaskFlow</h2>
                  <p className="text-xs text-gray-400">Workspace</p>
                </div>
              </div>
            ) : (
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                <Briefcase className="w-6 h-6 text-white" />
              </div>
            )}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="p-1 rounded-full hover:bg-gray-700 text-white flex-shrink-0"
                aria-label={isOpen ? "Collapse sidebar" : "Expand sidebar"}
            >
                {isOpen ? <ChevronFirst className="w-5 h-5" /> : <ChevronLast className="w-5 h-5" />}
            </button>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 p-4 space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 p-3 rounded-xl transition-all duration-200",
                  isActive(item.href)
                    ? "bg-gradient-to-r from-blue-600 to-purple-600 shadow-lg"
                    : "hover:bg-gray-700",
                  !isOpen && "justify-center"
                )}
                title={!isOpen ? item.label : undefined}
              >
                <Icon className="w-5 h-5 flex-shrink-0" />
                {isOpen && <span className="font-medium">{item.label}</span>}
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-gray-700">
          <div className={cn(
            "text-xs text-gray-400",
            !isOpen && "text-center"
          )}>
            {isOpen ? (
              <>
                <p className="font-semibold text-white mb-1">TaskFlow v1.0</p>
                <p>© 2024 All rights reserved</p>
              </>
            ) : (
              <p className="font-semibold">v1.0</p>
            )}
          </div>
        </div>
      </div>

      {/* Backdrop for mobile overlay */}
      {isMobile && isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-30"
          onClick={() => setIsOpen(false)}
        ></div>
      )}
    </>
  );
}

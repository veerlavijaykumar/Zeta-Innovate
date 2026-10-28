import React from 'react';
import { useAuth } from '@/context/AuthContext';
import { LogOut, User as UserIcon, Bell } from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <header className="h-16 bg-white/90 backdrop-blur-md border-b border-slate-200 sticky top-0 z-10 px-8 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <span className="text-xs uppercase font-bold tracking-wider text-slate-600 bg-slate-100 px-2.5 py-1 rounded-md">
          AI Candidate Workspace
        </span>
      </div>

      <div className="flex items-center gap-4">
        {/* User profile dropdown info */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-xs">
            {user?.full_name?.charAt(0) || <UserIcon className="w-4 h-4" />}
          </div>
          <div className="hidden sm:block text-left">
            <div className="text-xs font-bold text-slate-800 leading-tight">
              {user?.full_name || 'Candidate'}
            </div>
            <div className="text-[11px] text-slate-600 leading-tight">
              {user?.email}
            </div>
          </div>
        </div>

        <button
          onClick={logout}
          className="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors ml-2"
          title="Sign out"
        >
          <LogOut className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};

import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  Compass,
  User,
  Search,
  Sparkles,
  BookOpen,
  FileEdit,
  Send,
  BarChart2,
  Settings,
  Layers,
} from 'lucide-react';

const NAV_ITEMS = [
  { to: '/dashboard', label: 'Dashboard', icon: Compass },
  { to: '/profile', label: 'Career Profile', icon: User },
  { to: '/career', label: 'Career Intel', icon: Sparkles },
  { to: '/jobs', label: 'Job Discovery', icon: Search },
  { to: '/learning', label: 'Learning Roadmap', icon: BookOpen },
  { to: '/documents', label: 'Resume Studio', icon: FileEdit },
  { to: '/applications', label: 'Applications', icon: Send },
  { to: '/analytics', label: 'Career Analytics', icon: BarChart2 },
  { to: '/settings', label: 'Sources & Settings', icon: Settings },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 bg-white border-r border-slate-200 flex flex-col justify-between h-screen sticky top-0 z-20">
      <div>
        {/* Brand Header */}
        <div className="h-16 flex items-center px-6 border-b border-slate-100 gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-indigo-400 flex items-center justify-center text-white shadow-md shadow-indigo-100">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <span className="font-extrabold text-slate-900 tracking-tight text-base block">
              CareerMap <span className="text-indigo-600 font-black">AI</span>
            </span>
            <span className="text-[10px] text-slate-600 tracking-wider font-semibold block uppercase">
              Discovery & Copilot
            </span>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="p-3 space-y-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-indigo-50 text-indigo-700 font-semibold'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`
                }
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Pro Badge / Assistance Notice */}
      <div className="p-4 m-3 rounded-xl bg-slate-50 border border-slate-100 text-xs text-slate-600">
        <div className="font-semibold text-slate-800 mb-1 flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
          <span>Truthful AI Guarantee</span>
        </div>
        <p className="text-[11px] leading-relaxed text-slate-500">
          All resume tailoring and recommendations are strictly grounded in your verified facts.
        </p>
      </div>
    </aside>
  );
};

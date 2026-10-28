import React from 'react';
import { Link } from 'react-router-dom';
import {
  Compass,
  Sparkles,
  Search,
  BookOpen,
  FileCheck,
  Send,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-between">
      {/* Top Header */}
      <header className="h-20 max-w-7xl mx-auto w-full px-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-600 text-white flex items-center justify-center font-black shadow-md shadow-indigo-100">
            <Compass className="w-6 h-6" />
          </div>
          <span className="text-xl font-extrabold text-slate-900 tracking-tight">
            CareerMap <span className="text-indigo-600">AI</span>
          </span>
        </div>

        <div className="flex items-center gap-4">
          <Link
            to="/login"
            className="text-sm font-semibold text-slate-700 hover:text-slate-900 px-4 py-2 transition-colors"
          >
            Sign In
          </Link>
          <Link
            to="/register"
            className="text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 px-5 py-2.5 rounded-xl shadow-sm transition-all shadow-indigo-100"
          >
            Get Started Free
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-6 max-w-5xl mx-auto text-center space-y-6">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-50 border border-indigo-100 text-xs font-semibold text-indigo-700 mb-2">
          <Sparkles className="w-4 h-4 text-indigo-600" />
          <span>AI-Powered Career Discovery & Application Copilot</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold text-slate-900 tracking-tight leading-tight">
          Navigate your engineering career with{' '}
          <span className="text-indigo-600 underline decoration-indigo-200 decoration-wavy">
            evidence-backed AI
          </span>
        </h1>

        <p className="text-lg text-slate-600 max-w-2xl mx-auto leading-relaxed">
          From verified resume skill extraction to transparent job matching, personalized learning roadmaps,
          and truthful ATS resume tailoring. No hallucinations, no generic CRUD.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
          <Link
            to="/register"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-7 py-3.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-base shadow-lg shadow-indigo-100 transition-all"
          >
            <span>Start Free Discovery</span>
            <ArrowRight className="w-5 h-5" />
          </Link>
          <Link
            to="/login"
            className="w-full sm:w-auto inline-flex items-center justify-center px-7 py-3.5 rounded-xl bg-white hover:bg-slate-50 text-slate-800 font-semibold text-base border border-slate-200 shadow-sm transition-all"
          >
            Candidate Portal Login
          </Link>
        </div>

        <div className="pt-8 flex items-center justify-center gap-6 text-xs text-slate-500 font-medium">
          <span className="flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            100% Truthful ATS Resumes
          </span>
          <span className="flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            Explainable Match Scoring
          </span>
          <span className="flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            Multi-Source Aggregation
          </span>
        </div>
      </section>

      {/* Feature Grid */}
      <section className="py-16 px-6 max-w-7xl mx-auto w-full">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white p-7 rounded-2xl border border-slate-200 shadow-sm space-y-3">
            <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold">
              <Search className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-bold text-slate-900">Multi-Source Discovery</h3>
            <p className="text-sm text-slate-600 leading-relaxed">
              Connect to verified public job boards, company career feeds, and aggregator APIs with automatic deduplication and freshness verification.
            </p>
          </div>

          <div className="bg-white p-7 rounded-2xl border border-slate-200 shadow-sm space-y-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold">
              <Sparkles className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-bold text-slate-900">Multi-Stage Matching</h3>
            <p className="text-sm text-slate-600 leading-relaxed">
              Transparent 5-stage ranking: hard eligibility filters, skill taxonomy normalization, semantic retrieval, and concrete resume evidence quotes.
            </p>
          </div>

          <div className="bg-white p-7 rounded-2xl border border-slate-200 shadow-sm space-y-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold">
              <BookOpen className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-bold text-slate-900">Personalized Roadmaps</h3>
            <p className="text-sm text-slate-600 leading-relaxed">
              Target a new role and receive a realistic week-by-week curriculum with verified educational resources, practice projects, and schedule tracking.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="h-16 border-t border-slate-200 max-w-7xl mx-auto w-full px-6 flex items-center justify-between text-xs text-slate-500">
        <div>© 2026 CareerMap AI — AI-Powered Career Discovery & Application Copilot.</div>
        <div className="flex gap-4">
          <span>FastAPI</span>
          <span>•</span>
          <span>PostgreSQL</span>
          <span>•</span>
          <span>React + Vite</span>
          <span>•</span>
          <span>Google Gemini</span>
        </div>
      </footer>
    </div>
  );
};

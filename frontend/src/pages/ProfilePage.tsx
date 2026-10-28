import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/services/api';
import {
  Upload,
  FileText,
  Plus,
  Trash2,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Sparkles,
  ExternalLink,
  Briefcase,
  Code,
  GraduationCap,
} from 'lucide-react';
import { SkillBadge } from '@/components/common/SkillBadge';

export const ProfilePage: React.FC = () => {
  const queryClient = useQueryClient();

  const [uploadStatus, setUploadStatus] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [newSkill, setNewSkill] = useState('');
  const [skillCategory, setSkillCategory] = useState('Technical');
  const [skillLevel, setSkillLevel] = useState('intermediate');

  // Load Profile
  const { data: profile, isLoading } = useQuery({
    queryKey: ['profile'],
    queryFn: () => api.getProfile(),
  });

  // Load Preferences
  const { data: preferences } = useQuery({
    queryKey: ['preferences'],
    queryFn: () => api.getPreferences(),
  });

  // Upload Resume Mutation
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setUploadStatus('Uploading resume...');

    try {
      const uploadRes = await api.uploadResume(file);
      setUploadStatus('Extracting profile data with AI...');
      await api.extractResume(uploadRes.id);
      setUploadStatus('Profile extracted successfully!');
      queryClient.invalidateQueries({ queryKey: ['profile'] });
    } catch (err: any) {
      setUploadStatus(`Extraction failed: ${err.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  // Add Skill Mutation
  const addSkillMutation = useMutation({
    mutationFn: (data: { name: string; category: string; proficiency_level: string }) =>
      api.addSkill(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] });
      setNewSkill('');
    },
  });

  // Delete Skill Mutation
  const deleteSkillMutation = useMutation({
    mutationFn: (skillId: number) => api.deleteSkill(skillId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] });
    },
  });

  const handleAddSkill = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSkill.trim()) return;
    addSkillMutation.mutate({
      name: newSkill.trim(),
      category: skillCategory,
      proficiency_level: skillLevel,
    });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Candidate Profile & Skills</h1>
          <p className="text-xs text-slate-500 mt-1">
            Review and manage your verified skills, experience, and career preferences.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <label className="cursor-pointer inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs shadow-sm transition-colors">
            {isUploading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Upload className="w-4 h-4" />
            )}
            <span>{isUploading ? 'Extracting...' : 'Upload Resume PDF'}</span>
            <input
              type="file"
              accept=".pdf,.docx"
              onChange={handleFileUpload}
              disabled={isUploading}
              className="hidden"
            />
          </label>
        </div>
      </div>

      {/* Upload Notification */}
      {uploadStatus && (
        <div className={`p-4 rounded-xl text-xs flex items-center gap-2 border ${
          uploadStatus.includes('failed')
            ? 'bg-rose-50 border-rose-200 text-rose-700'
            : 'bg-emerald-50 border-emerald-200 text-emerald-800'
        }`}>
          {uploadStatus.includes('failed') ? (
            <AlertCircle className="w-4 h-4 text-rose-500" />
          ) : (
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          )}
          <span>{uploadStatus}</span>
        </div>
      )}

      {/* Profile Overview Card */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-lg font-bold text-slate-900">
              {profile?.current_role || 'Candidate'} {profile?.current_company ? `@ ${profile.current_company}` : ''}
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              {profile?.location || 'Location not set'} • {profile?.total_experience_years || 0} Years Experience
            </p>
          </div>
          <div className="flex items-center gap-2 text-xs bg-slate-100 text-slate-700 px-3 py-1 rounded-full font-semibold">
            <span>Profile Completeness:</span>
            <span className="text-indigo-600">{profile?.profile_completeness || 0}%</span>
          </div>
        </div>

        {profile?.summary ? (
          <p className="text-sm text-slate-700 leading-relaxed bg-slate-50 p-4 rounded-lg border border-slate-100">
            {profile.summary}
          </p>
        ) : (
          <p className="text-xs text-slate-400 italic">
            No summary provided yet. Upload a resume to automatically extract your bio.
          </p>
        )}
      </div>

      {/* Skills Section */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-5">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div>
            <h3 className="text-base font-bold text-slate-900">Verified Technical Skills</h3>
            <p className="text-xs text-slate-500">
              These skills are evaluated directly by the AI matching engine.
            </p>
          </div>
          <span className="text-xs font-semibold text-slate-600 bg-slate-100 px-2.5 py-1 rounded-full">
            {profile?.skills.length || 0} Skills
          </span>
        </div>

        {/* Add Skill Form */}
        <form onSubmit={handleAddSkill} className="flex flex-wrap items-center gap-2 bg-slate-50 p-3 rounded-lg border border-slate-100">
          <input
            type="text"
            placeholder="Skill name (e.g. React, Docker, Python)"
            value={newSkill}
            onChange={(e) => setNewSkill(e.target.value)}
            className="flex-1 min-w-[200px] text-xs px-3 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
          />
          <select
            value={skillCategory}
            onChange={(e) => setSkillCategory(e.target.value)}
            className="text-xs px-3 py-2 rounded-lg border border-slate-300 bg-white"
          >
            <option value="Technical">Technical</option>
            <option value="Frontend">Frontend</option>
            <option value="Backend">Backend</option>
            <option value="Database">Database</option>
            <option value="DevOps">DevOps</option>
            <option value="AI/ML">AI/ML</option>
            <option value="Soft">Soft Skill</option>
          </select>
          <select
            value={skillLevel}
            onChange={(e) => setSkillLevel(e.target.value)}
            className="text-xs px-3 py-2 rounded-lg border border-slate-300 bg-white"
          >
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
            <option value="expert">Expert</option>
          </select>
          <button
            type="submit"
            disabled={addSkillMutation.isPending}
            className="inline-flex items-center gap-1 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs rounded-lg transition-colors"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add Skill</span>
          </button>
        </form>

        {/* Skill Chips */}
        {profile?.skills && profile.skills.length > 0 ? (
          <div className="flex flex-wrap gap-2 pt-2">
            {profile.skills.map((skill) => (
              <div
                key={skill.id}
                className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-slate-50 border border-slate-200 text-xs font-medium text-slate-800 group hover:border-slate-300 transition-colors"
              >
                <span>{skill.name}</span>
                {skill.category && (
                  <span className="text-[10px] text-slate-400">({skill.category})</span>
                )}
                <button
                  onClick={() => deleteSkillMutation.mutate(skill.id)}
                  className="text-slate-400 hover:text-rose-500 transition-colors ml-1"
                  title="Remove skill"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-6 text-xs text-slate-400 italic">
            No skills added yet. Add skills above or upload your resume PDF to extract them automatically.
          </div>
        )}
      </div>

      {/* Experience History */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
        <h3 className="text-base font-bold text-slate-900 border-b border-slate-100 pb-3 flex items-center gap-2">
          <Briefcase className="w-4 h-4 text-indigo-600" />
          <span>Work Experience ({profile?.experiences.length || 0})</span>
        </h3>

        {profile?.experiences && profile.experiences.length > 0 ? (
          <div className="space-y-4">
            {profile.experiences.map((exp) => (
              <div key={exp.id} className="border-l-2 border-indigo-400 pl-4 py-1">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-bold text-slate-900">{exp.title}</h4>
                  <span className="text-xs text-slate-400">
                    {exp.start_date || 'N/A'} - {exp.end_date || 'Present'}
                  </span>
                </div>
                <div className="text-xs text-indigo-600 font-medium">{exp.company}</div>
                {exp.description && (
                  <p className="text-xs text-slate-600 mt-1 leading-relaxed">{exp.description}</p>
                )}
                {exp.technologies && exp.technologies.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {exp.technologies.map((t) => (
                      <span key={t} className="text-[10px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-mono">
                        {t}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs text-slate-400 italic">No work experience listed yet.</p>
        )}
      </div>

      {/* Projects */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
        <h3 className="text-base font-bold text-slate-900 border-b border-slate-100 pb-3 flex items-center gap-2">
          <Code className="w-4 h-4 text-indigo-600" />
          <span>Projects ({profile?.projects.length || 0})</span>
        </h3>

        {profile?.projects && profile.projects.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {profile.projects.map((proj) => (
              <div key={proj.id} className="border border-slate-200 rounded-lg p-4 bg-slate-50/50">
                <div className="font-bold text-sm text-slate-900">{proj.name}</div>
                {proj.description && (
                  <p className="text-xs text-slate-600 mt-1 leading-relaxed">{proj.description}</p>
                )}
                {proj.technologies && proj.technologies.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {proj.technologies.map((t) => (
                      <span key={t} className="text-[10px] bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded font-mono">
                        {t}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs text-slate-400 italic">No projects listed yet.</p>
        )}
      </div>
    </div>
  );
};

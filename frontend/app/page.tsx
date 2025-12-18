'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { getStatus, getNextPost, createRandomPost, type StatusResponse } from '@/utils/api';

export default function Dashboard() {
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [nextPost, setNextPost] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [posting, setPosting] = useState(false);
  const [message, setMessage] = useState<{type: 'success' | 'error', text: string} | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const [statusData, nextPostData] = await Promise.all([
        getStatus(),
        getNextPost()
      ]);
      setStatus(statusData);
      setNextPost(nextPostData);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  }

  async function handleQuickPost() {
    setPosting(true);
    setMessage(null);
    
    try {
      const result = await createRandomPost();
      setMessage({ type: 'success', text: `Post created successfully! ${result.content?.substring(0, 100)}...` });
      loadData(); // Refresh stats
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || 'Failed to create post' });
    } finally {
      setPosting(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <h1 className="text-4xl font-bold text-white mb-2">
          ✨ LinkedIn Automation Dashboard
        </h1>
        <p className="text-purple-200">Manage your automated LinkedIn posting with ease</p>
      </div>

      {/* Message Toast */}
      {message && (
        <div className={`max-w-7xl mx-auto mb-6 p-4 rounded-lg ${
          message.type === 'success' ? 'bg-green-500/20 border border-green-500' : 'bg-red-500/20 border border-red-500'
        }`}>
          <p className="text-white">{message.text}</p>
        </div>
      )}

      {/* Stats Cards */}
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Status Card */}
        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
          <div className="text-purple-200 text-sm mb-2">System Status</div>
          <div className="text-3xl font-bold text-white mb-1">{status?.status === 'healthy' ? '🟢 Active' : '🔴 Offline'}</div>
          <div className="text-purple-300 text-sm">API Connected</div>
        </div>

        {/* Topics Card */}
        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
          <div className="text-purple-200 text-sm mb-2">Available Topics</div>
          <div className="text-3xl font-bold text-white mb-1">{status?.unused_topics || 0}</div>
          <div className="text-purple-300 text-sm">of {status?.total_topics || 0} total</div>
        </div>

        {/* Next Post Card */}
        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
          <div className="text-purple-200 text-sm mb-2">Next Scheduled Post</div>
          <div className="text-lg font-bold text-white mb-1">
            {nextPost?.next_post ? (
              <>
                {nextPost.next_post.date} <span className="text-purple-300">{nextPost.next_post.time}</span>
              </>
            ) : (
              'Not scheduled'
            )}
          </div>
          <div className="text-purple-300 text-sm">{nextPost?.time_until || 'Configure schedule'}</div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Quick Post */}
        <div className="bg-gradient-to-br from-purple-500/20 to-pink-500/20 backdrop-blur-lg rounded-xl p-8 border border-purple-500/30">
          <h2 className="text-2xl font-bold text-white mb-4">🚀 Quick Post</h2>
          <p className="text-purple-200 mb-6">Post a random topic immediately to LinkedIn</p>
          <button
            onClick={handleQuickPost}
            disabled={posting}
            className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold py-3 px-8 rounded-lg transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {posting ? '⏳ Posting...' : '⚡ Post Now'}
          </button>
        </div>

        {/* Custom Post */}
        <div className="bg-gradient-to-br from-blue-500/20 to-cyan-500/20 backdrop-blur-lg rounded-xl p-8 border border-blue-500/30">
          <h2 className="text-2xl font-bold text-white mb-4">✍️ Custom Post</h2>
          <p className="text-blue-200 mb-6">Create a post with your own topic and image</p>
          <Link
            href="/post/new"
            className="inline-block bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white font-semibold py-3 px-8 rounded-lg transition-all transform hover:scale-105"
          >
            📝 Create Post
          </Link>
        </div>

        {/* Schedule Manager */}
        <div className="bg-gradient-to-br from-green-500/20 to-emerald-500/20 backdrop-blur-lg rounded-xl p-8 border border-green-500/30">
          <h2 className="text-2xl font-bold text-white mb-4">📅 Schedule Manager</h2>
          <p className="text-green-200 mb-6">View and manage upcoming scheduled posts</p>
          <Link
            href="/schedule"
            className="inline-block bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white font-semibold py-3 px-8 rounded-lg transition-all transform hover:scale-105"
          >
            📊 View Schedule
          </Link>
        </div>

        {/* Preview Generator */}
        <div className="bg-gradient-to-br from-orange-500/20 to-yellow-500/20 backdrop-blur-lg rounded-xl p-8 border border-orange-500/30">
          <h2 className="text-2xl font-bold text-white mb-4">👁️ Preview Generator</h2>
          <p className="text-orange-200 mb-6">Generate and preview content before posting</p>
          <Link
            href="/preview"
            className="inline-block bg-gradient-to-r from-orange-500 to-yellow-500 hover:from-orange-600 hover:to-yellow-600 text-white font-semibold py-3 px-8 rounded-lg transition-all transform hover:scale-105"
          >
            🔍 Preview Content
          </Link>
        </div>
      </div>

      {/* Footer */}
      <div className="max-w-7xl mx-auto mt-12 text-center text-purple-300 text-sm">
        <p>LinkedIn Automation v2.0 • Powered by AI • Built with ❤️</p>
      </div>
    </div>
  );
}

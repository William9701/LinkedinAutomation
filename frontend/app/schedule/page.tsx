'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { getSchedule, cancelSchedule, type ScheduleItem } from '@/utils/api';

export default function Schedule() {
  const [schedule, setSchedule] = useState<ScheduleItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState<{type: 'success' | 'error', text: string} | null>(null);

  useEffect(() => {
    loadSchedule();
  }, []);

  async function loadSchedule() {
    try {
      const data = await getSchedule();
      setSchedule(data);
    } catch (error) {
      console.error('Failed to load schedule:', error);
      setMessage({ type: 'error', text: 'Failed to load schedule' });
    } finally {
      setLoading(false);
    }
  }

  async function handleCancel(date: string, postType: string) {
    if (!confirm(`Cancel ${postType} post on ${date}?`)) return;

    try {
      await cancelSchedule(date, postType);
      setMessage({ type: 'success', text: `Cancelled ${postType} post on ${date}` });
      loadSchedule(); // Refresh
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || 'Failed to cancel' });
    }
  }

  async function handleCancelToday() {
    const today = new Date().toISOString().split('T')[0];
    if (!confirm('Cancel ALL posts for today?')) return;

    try {
      await cancelSchedule(today, 'all');
      setMessage({ type: 'success', text: 'Cancelled all posts for today' });
      loadSchedule();
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || 'Failed to cancel today\'s posts' });
    }
  }

  async function handleCancelMonth() {
    const year = new Date().getFullYear();
    const month = String(new Date().getMonth() + 1).padStart(2, '0');
    const monthDate = `${year}-${month}`;

    if (!confirm('Cancel ALL posts for this month?')) return;

    try {
      await cancelSchedule(monthDate, 'all');
      setMessage({ type: 'success', text: 'Cancelled all posts for this month' });
      loadSchedule();
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || 'Failed to cancel month\'s posts' });
    }
  }

  function groupByDate(items: ScheduleItem[]) {
    const grouped: Record<string, ScheduleItem[]> = {};
    items.forEach(item => {
      if (!grouped[item.date]) grouped[item.date] = [];
      grouped[item.date].push(item);
    });
    return grouped;
  }

  const groupedSchedule = groupByDate(schedule);
  const dates = Object.keys(groupedSchedule).sort();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <div className="text-white text-xl">Loading schedule...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      {/* Header */}
      <div className="max-w-5xl mx-auto mb-8">
        <Link href="/" className="text-purple-300 hover:text-purple-200 mb-4 inline-block">
          ← Back to Dashboard
        </Link>
        <h1 className="text-4xl font-bold text-white mb-2">
          📅 Schedule Manager
        </h1>
        <p className="text-purple-200">View and manage your upcoming posts</p>
      </div>

      {/* Message Toast */}
      {message && (
        <div className={`max-w-5xl mx-auto mb-6 p-4 rounded-lg ${
          message.type === 'success' ? 'bg-green-500/20 border border-green-500' : 'bg-red-500/20 border border-red-500'
        }`}>
          <p className="text-white">{message.text}</p>
        </div>
      )}

      {/* Quick Actions */}
      <div className="max-w-5xl mx-auto mb-8 flex gap-4">
        <button
          onClick={handleCancelToday}
          className="bg-red-500/20 hover:bg-red-500/30 border border-red-500 text-red-200 font-semibold py-2 px-6 rounded-lg transition-all"
        >
          🚫 Cancel Today
        </button>
        <button
          onClick={handleCancelMonth}
          className="bg-red-500/20 hover:bg-red-500/30 border border-red-500 text-red-200 font-semibold py-2 px-6 rounded-lg transition-all"
        >
          🚫 Cancel This Month
        </button>
      </div>

      {/* Schedule List */}
      <div className="max-w-5xl mx-auto space-y-6">
        {dates.length === 0 ? (
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-12 border border-white/20 text-center">
            <div className="text-6xl mb-4">📭</div>
            <p className="text-white text-xl mb-2">No upcoming posts scheduled</p>
            <p className="text-purple-300">Posts will appear here when scheduled</p>
          </div>
        ) : (
          dates.map(date => (
            <div key={date} className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              {/* Date Header */}
              <div className="flex justify-between items-center mb-4 pb-4 border-b border-white/10">
                <h2 className="text-2xl font-bold text-white">
                  {new Date(date + 'T00:00:00').toLocaleDateString('en-US', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </h2>
                <span className="bg-purple-500/20 text-purple-200 px-3 py-1 rounded-full text-sm">
                  {groupedSchedule[date].length} post{groupedSchedule[date].length > 1 ? 's' : ''}
                </span>
              </div>

              {/* Posts for this date */}
              <div className="space-y-3">
                {groupedSchedule[date].map((item, index) => (
                  <div key={index} className="flex items-center justify-between bg-white/5 rounded-lg p-4 hover:bg-white/10 transition-colors">
                    <div className="flex items-center gap-4">
                      <div className="text-3xl">
                        {item.type === 'morning' ? '🌅' : '🌙'}
                      </div>
                      <div>
                        <div className="text-white font-semibold">
                          {item.type.charAt(0).toUpperCase() + item.type.slice(1)} Post
                        </div>
                        <div className="text-purple-300 text-sm">{item.time}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className={`px-3 py-1 rounded-full text-sm ${
                        item.status === 'scheduled' ? 'bg-green-500/20 text-green-200' :
                        item.status === 'posted' ? 'bg-blue-500/20 text-blue-200' :
                        'bg-gray-500/20 text-gray-200'
                      }`}>
                        {item.status}
                      </span>
                      {item.status === 'scheduled' && (
                        <button
                          onClick={() => handleCancel(date, item.type)}
                          className="text-red-400 hover:text-red-300 font-medium text-sm"
                        >
                          Cancel
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Info Box */}
      <div className="max-w-5xl mx-auto mt-8 bg-blue-500/10 backdrop-blur-lg rounded-xl p-6 border border-blue-500/30">
        <h3 className="text-white font-semibold mb-2">ℹ️ Scheduling Info</h3>
        <ul className="text-blue-200 text-sm space-y-1">
          <li>• Morning posts are scheduled around 9:00 AM UTC (±30 min variance)</li>
          <li>• Evening posts are scheduled around 7:00 PM UTC (±30 min variance)</li>
          <li>• Posts are automatically generated from your 1000+ topic library</li>
          <li>• Cancelled posts won't be rescheduled automatically</li>
        </ul>
      </div>
    </div>
  );
}

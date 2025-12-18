'use client';

import { useState } from 'react';
import Link from 'next/link';
import { generatePreview, createCustomPost, type PreviewResponse, type PostResponse } from '@/utils/api';

export default function Preview() {
  const [topic, setTopic] = useState('');
  const [prompt, setPrompt] = useState('');
  const [category, setCategory] = useState('');
  const [preview, setPreview] = useState<PreviewResponse | null>(null);
  const [editedContent, setEditedContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [posting, setPosting] = useState(false);
  const [message, setMessage] = useState<{type: 'success' | 'error', text: string} | null>(null);

  async function handleGenerate() {
    if (!topic.trim()) {
      setMessage({ type: 'error', text: 'Please enter a topic' });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const result = await generatePreview(topic, prompt || undefined, category || undefined);
      setPreview(result);
      setEditedContent(result.content);
      setMessage({ type: 'success', text: 'Preview generated!' });
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || 'Failed to generate preview' });
    } finally {
      setLoading(false);
    }
  }

  async function handleRegenerate() {
    await handleGenerate();
  }

  async function handlePost() {
    if (!preview) {
      setMessage({ type: 'error', text: 'Generate a preview first' });
      return;
    }

    setPosting(true);
    setMessage(null);

    try {
      const result = await createCustomPost(
        topic,
        prompt || undefined,
        category || undefined
      );
      setMessage({ type: 'success', text: `Posted successfully! URN: ${result.post_urn}` });

      // Reset after successful post
      setTimeout(() => {
        setTopic('');
        setPrompt('');
        setCategory('');
        setPreview(null);
        setEditedContent('');
      }, 3000);
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || 'Failed to post' });
    } finally {
      setPosting(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      {/* Header */}
      <div className="max-w-6xl mx-auto mb-8">
        <Link href="/" className="text-purple-300 hover:text-purple-200 mb-4 inline-block">
          ← Back to Dashboard
        </Link>
        <h1 className="text-4xl font-bold text-white mb-2">
          👁️ Content Preview
        </h1>
        <p className="text-purple-200">Generate and preview content before posting</p>
      </div>

      {/* Message Toast */}
      {message && (
        <div className={`max-w-6xl mx-auto mb-6 p-4 rounded-lg ${
          message.type === 'success' ? 'bg-green-500/20 border border-green-500' : 'bg-red-500/20 border border-red-500'
        }`}>
          <p className="text-white">{message.text}</p>
        </div>
      )}

      <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Side - Input */}
        <div className="space-y-6">
          {/* Topic Input */}
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
            <label className="block text-white font-semibold mb-2">
              Topic Title *
            </label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., Why Microservices Can Be Overkill"
              className="w-full bg-white/5 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-purple-300 focus:outline-none focus:border-purple-500"
            />
            <p className="text-purple-300 text-sm mt-2">Enter a topic to preview</p>
          </div>

          {/* Category Select */}
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
            <label className="block text-white font-semibold mb-2">
              Category (Optional)
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full bg-white/5 border border-white/20 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-purple-500"
            >
              <option value="">Auto-detect</option>
              <option value="Backend Frameworks">Backend Frameworks</option>
              <option value="Database">Database</option>
              <option value="DevOps">DevOps</option>
              <option value="AI/ML">AI/ML</option>
              <option value="Architecture">Architecture</option>
              <option value="Security">Security</option>
              <option value="Performance">Performance</option>
              <option value="Career">Career</option>
            </select>
          </div>

          {/* Custom Instructions */}
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
            <label className="block text-white font-semibold mb-2">
              Custom Instructions (Optional)
            </label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="e.g., Focus on real-world examples, keep it beginner-friendly..."
              rows={4}
              className="w-full bg-white/5 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-purple-300 focus:outline-none focus:border-purple-500 resize-none"
            />
            <p className="text-purple-300 text-sm mt-2">Guide the AI on the angle to take</p>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4">
            <button
              onClick={handleGenerate}
              disabled={loading || !topic.trim()}
              className="flex-1 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold py-3 px-6 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? '⏳ Generating...' : '✨ Generate Preview'}
            </button>
            {preview && (
              <button
                onClick={handleRegenerate}
                disabled={loading}
                className="bg-blue-500/20 hover:bg-blue-500/30 border border-blue-500 text-blue-200 font-semibold py-3 px-6 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                🔄 Regenerate
              </button>
            )}
          </div>

          {/* Quick Tips */}
          <div className="bg-blue-500/10 backdrop-blur-lg rounded-xl p-6 border border-blue-500/30">
            <h3 className="text-white font-semibold mb-3">💡 Quick Tips</h3>
            <ul className="text-blue-200 text-sm space-y-2">
              <li>• Keep topics simple and conversational</li>
              <li>• Add custom instructions for specific angles</li>
              <li>• Preview multiple times to get the perfect version</li>
              <li>• Content is auto-formatted with emojis and headers</li>
            </ul>
          </div>
        </div>

        {/* Right Side - Preview */}
        <div className="space-y-6">
          {preview ? (
            <>
              {/* Content Preview */}
              <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-2xl font-bold text-white">Generated Content</h2>
                  <span className="bg-green-500/20 text-green-200 px-3 py-1 rounded-full text-sm">
                    Ready to post
                  </span>
                </div>

                {/* Editable Content */}
                <div className="bg-white/5 rounded-lg p-4 border border-white/10 mb-4">
                  <textarea
                    value={editedContent}
                    onChange={(e) => setEditedContent(e.target.value)}
                    rows={15}
                    className="w-full bg-transparent text-white resize-none focus:outline-none"
                  />
                </div>

                <p className="text-purple-300 text-xs">
                  You can edit the content above before posting
                </p>
              </div>

              {/* Hashtags */}
              <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
                <h3 className="text-white font-semibold mb-3">Hashtags</h3>
                <div className="flex flex-wrap gap-2">
                  {preview.hashtags.map((tag, index) => (
                    <span key={index} className="bg-purple-500/20 text-purple-200 px-3 py-1 rounded-full text-sm">
                      #{tag}
                    </span>
                  ))}
                </div>
              </div>

              {/* Image Suggestion */}
              {preview.image_prompt && (
                <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
                  <h3 className="text-white font-semibold mb-3">🎨 AI Image Suggestion</h3>
                  <p className="text-purple-200 text-sm">{preview.image_prompt}</p>
                  <p className="text-purple-300 text-xs mt-2">
                    Use this prompt with Midjourney, DALL-E, or other image generators
                  </p>
                </div>
              )}

              {/* Post Button */}
              <button
                onClick={handlePost}
                disabled={posting}
                className="w-full bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white font-semibold py-4 px-6 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {posting ? '⏳ Posting...' : '🚀 Post to LinkedIn Now'}
              </button>
            </>
          ) : (
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20 h-full flex items-center justify-center">
              <div className="text-center text-purple-300">
                <div className="text-6xl mb-4">📝</div>
                <p className="text-lg mb-2">No preview yet</p>
                <p className="text-sm">Enter a topic and click Generate Preview</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

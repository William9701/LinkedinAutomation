'use client';

import { useState } from 'react';
import Link from 'next/link';
import { createCustomPost, generatePreview, type PostResponse, type PreviewResponse } from '@/utils/api';

export default function NewPost() {
  const [topic, setTopic] = useState('');
  const [prompt, setPrompt] = useState('');
  const [category, setCategory] = useState('');
  const [image, setImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string>('');
  const [preview, setPreview] = useState<PreviewResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [posting, setPosting] = useState(false);
  const [message, setMessage] = useState<{type: 'success' | 'error', text: string} | null>(null);

  function handleImageChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) {
      setImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  }

  async function handlePreview() {
    if (!topic.trim()) {
      setMessage({ type: 'error', text: 'Please enter a topic' });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const result = await generatePreview(topic, prompt || undefined, category || undefined);
      setPreview(result);
      setMessage({ type: 'success', text: 'Preview generated!' });
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || 'Failed to generate preview' });
    } finally {
      setLoading(false);
    }
  }

  async function handlePost() {
    if (!topic.trim()) {
      setMessage({ type: 'error', text: 'Please enter a topic' });
      return;
    }

    setPosting(true);
    setMessage(null);

    try {
      const result = await createCustomPost(
        topic,
        prompt || undefined,
        category || undefined,
        image || undefined
      );
      setMessage({ type: 'success', text: `Posted successfully! URN: ${result.post_urn}` });

      // Reset form
      setTopic('');
      setPrompt('');
      setCategory('');
      setImage(null);
      setImagePreview('');
      setPreview(null);
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || 'Failed to create post' });
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
          ✍️ Create Custom Post
        </h1>
        <p className="text-purple-200">Write your own content or let AI help you</p>
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
        {/* Left Side - Form */}
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
            <p className="text-purple-300 text-sm mt-2">Keep it simple and conversational</p>
          </div>

          {/* Category Input */}
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

          {/* Prompt Input */}
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
            <label className="block text-white font-semibold mb-2">
              Custom Instructions (Optional)
            </label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="e.g., Focus on real-world examples, keep it beginner-friendly, include a personal story..."
              rows={4}
              className="w-full bg-white/5 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-purple-300 focus:outline-none focus:border-purple-500 resize-none"
            />
            <p className="text-purple-300 text-sm mt-2">Guide the AI on what angle to take</p>
          </div>

          {/* Image Upload */}
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
            <label className="block text-white font-semibold mb-2">
              Image (Optional)
            </label>
            <div className="border-2 border-dashed border-white/30 rounded-lg p-6 text-center hover:border-purple-500 transition-colors cursor-pointer">
              <input
                type="file"
                accept="image/*"
                onChange={handleImageChange}
                className="hidden"
                id="image-upload"
              />
              <label htmlFor="image-upload" className="cursor-pointer">
                {imagePreview ? (
                  <img src={imagePreview} alt="Preview" className="max-h-48 mx-auto rounded-lg" />
                ) : (
                  <>
                    <div className="text-4xl mb-2">📸</div>
                    <p className="text-purple-200">Click to upload an image</p>
                    <p className="text-purple-300 text-sm mt-1">PNG, JPG, GIF up to 10MB</p>
                  </>
                )}
              </label>
            </div>
            {imagePreview && (
              <button
                onClick={() => { setImage(null); setImagePreview(''); }}
                className="mt-3 text-red-400 hover:text-red-300 text-sm"
              >
                Remove image
              </button>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4">
            <button
              onClick={handlePreview}
              disabled={loading || !topic.trim()}
              className="flex-1 bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white font-semibold py-3 px-6 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? '⏳ Generating...' : '👁️ Preview'}
            </button>
            <button
              onClick={handlePost}
              disabled={posting || !topic.trim()}
              className="flex-1 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold py-3 px-6 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {posting ? '⏳ Posting...' : '🚀 Post to LinkedIn'}
            </button>
          </div>
        </div>

        {/* Right Side - Preview */}
        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
          <h2 className="text-2xl font-bold text-white mb-4">Preview</h2>
          {preview ? (
            <div className="space-y-4">
              {/* Content Preview */}
              <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                <p className="text-white whitespace-pre-wrap">{preview.content}</p>
              </div>

              {/* Hashtags */}
              <div className="flex flex-wrap gap-2">
                {preview.hashtags.map((tag, index) => (
                  <span key={index} className="bg-purple-500/20 text-purple-200 px-3 py-1 rounded-full text-sm">
                    #{tag}
                  </span>
                ))}
              </div>

              {/* Image Preview Prompt */}
              {preview.image_prompt && (
                <div className="bg-blue-500/10 rounded-lg p-4 border border-blue-500/30">
                  <p className="text-blue-200 text-sm font-semibold mb-2">AI Image Suggestion:</p>
                  <p className="text-blue-300 text-sm">{preview.image_prompt}</p>
                </div>
              )}
            </div>
          ) : (
            <div className="h-full flex items-center justify-center text-purple-300 text-center">
              <div>
                <div className="text-6xl mb-4">📝</div>
                <p>Enter a topic and click Preview</p>
                <p className="text-sm mt-2">to see generated content</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

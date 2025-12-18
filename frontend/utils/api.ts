// API client configuration
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface PostResponse {
  success: boolean;
  message: string;
  post_urn?: string;
  content?: string;
  hashtags?: string[];
}

export interface PreviewResponse {
  content: string;
  hashtags: string[];
  image_prompt?: string;
}

export interface ScheduleItem {
  date: string;
  time: string;
  type: string;
  status: string;
}

export interface StatusResponse {
  status: string;
  total_topics: number;
  unused_topics: number;
  next_scheduled_post?: string;
}

// POST: Random post
export async function createRandomPost(): Promise<PostResponse> {
  const response = await fetch(`${API_URL}/api/post/random`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create post');
  }
  
  return response.json();
}

// POST: Custom post with image
export async function createCustomPost(
  topic: string,
  prompt?: string,
  category?: string,
  image?: File
): Promise<PostResponse> {
  const formData = new FormData();
  formData.append('topic', topic);
  if (prompt) formData.append('prompt', prompt);
  if (category) formData.append('category', category);
  if (image) formData.append('image', image);
  
  const response = await fetch(`${API_URL}/api/post/custom`, {
    method: 'POST',
    body: formData
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create custom post');
  }
  
  return response.json();
}

// POST: Generate preview
export async function generatePreview(
  topic: string,
  prompt?: string,
  category?: string
): Promise<PreviewResponse> {
  const response = await fetch(`${API_URL}/api/generate-preview`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic, prompt, category })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to generate preview');
  }
  
  return response.json();
}

// GET: Schedule
export async function getSchedule(): Promise<ScheduleItem[]> {
  const response = await fetch(`${API_URL}/api/schedule`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch schedule');
  }
  
  return response.json();
}

// DELETE: Cancel schedule
export async function cancelSchedule(date: string, postType: string = 'all'): Promise<any> {
  const response = await fetch(`${API_URL}/api/schedule/${date}?post_type=${postType}`, {
    method: 'DELETE'
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to cancel schedule');
  }
  
  return response.json();
}

// GET: Status
export async function getStatus(): Promise<StatusResponse> {
  const response = await fetch(`${API_URL}/api/status`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch status');
  }
  
  return response.json();
}

// GET: Topics
export async function getTopics(): Promise<any> {
  const response = await fetch(`${API_URL}/api/topics`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch topics');
  }
  
  return response.json();
}

// GET: Next post
export async function getNextPost(): Promise<any> {
  const response = await fetch(`${API_URL}/api/schedule/next`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch next post');
  }
  
  return response.json();
}

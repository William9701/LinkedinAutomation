# 🚀 LinkedIn Automation - AI-Powered Content Posting

Fully automated LinkedIn content generation and posting system that creates high-quality, professional technical posts using Google Gemini AI.

## ✨ Features

- 🤖 **AI-Powered Content**: Uses Google Gemini AI (FREE tier) to generate detailed, professional content
- 📅 **Daily Posting**: Automatically posts EVERY DAY - 2 posts per day (morning & evening)
- 🎯 **Dynamic Timing**: Posts at random times (±30 min variance) to look natural
- 📚 **1000+ Topics**: Years of unique content covering backend, AI, DevOps, databases, architecture
- 🏷️ **Smart Hashtags**: Auto-generates 14-15 optimized hashtags per post
- 🎨 **Eye-Catching Headers**: Emojis + ALL CAPS titles for maximum engagement
- 🎉 **Special Day Awareness**: Automatically detects holidays and adds contextual messages
- ☁️ **Cloud Ready**: One-click deployment to Render (FREE tier available)

## 📊 Posting Schedule

- **Frequency**: EVERY DAY (Monday - Sunday)
- **Morning Post**: ~9:00 AM UTC (varies 8:30-9:30 AM)
- **Evening Post**: ~7:00 PM UTC (varies 6:30-7:30 PM)
- **Volume**: 2 posts/day = 730 posts/year

## 🎯 Topic Coverage (1000 Topics)

**Backend Development:**
- Framework comparisons (FastAPI, Flask, Django, Node.js, NestJS)
- API design patterns (REST, GraphQL, gRPC)
- Authentication & security (OAuth, JWT, API security)

**Databases:**
- SQL vs NoSQL comparisons
- Query optimization & indexing
- Database scaling & replication
- Vector databases for AI

**AI/ML Engineering:**
- LLM integration & fine-tuning
- RAG architecture
- Prompt engineering
- AI cost optimization

**DevOps & Infrastructure:**
- Kubernetes, Docker, CI/CD
- Cloud platforms (AWS, GCP, Azure)
- Monitoring & observability
- Performance optimization

**Career & Leadership:**
- Career growth & soft skills
- Technical interviews
- Team management

## 🚀 Quick Start

### 1. Get Your API Keys

**Gemini AI (FREE):**
1. Go to https://makersuite.google.com/app/apikey
2. Create API key
3. Copy it

**LinkedIn Access Token:**
1. Go to https://www.linkedin.com/developers/apps
2. Create an app
3. Add scopes: `openid`, `profile`, `email`, `w_member_social`
4. Run: `python get_token_simple.py`
5. Follow OAuth flow to get token

### 2. Deploy to Render (Recommended)

1. **Fork this repository** on GitHub

2. **Go to Render**: https://render.com

3. **Create New Web Service**:
   - Connect your GitHub repo
   - Render auto-detects `render.yaml`

4. **Add Environment Variables**:
   - `GEMINI_API_KEY`: Your Gemini API key
   - `LINKEDIN_ACCESS_TOKEN`: Your LinkedIn token
   - (Optional) Adjust `TIMEZONE` if needed

5. **Deploy!**
   - Render will build and start automatically
   - Posts begin at scheduled times

### 3. Local Testing (Optional)

```bash
# Install dependencies
pip install -r requirements.txt

# Test single post
python main.py test

# Run scheduler locally
python main.py schedule
```

## 🌍 Timezone Configuration

Default is UTC. Update in render.yaml or .env:

```env
TIMEZONE=America/New_York  # For EST
TIMEZONE=Europe/London     # For GMT
TIMEZONE=Asia/Singapore    # For SGT
```

## 💰 Cost

- **Gemini AI**: FREE (60 requests/min)
- **LinkedIn API**: FREE
- **Render Hosting**: FREE tier available
- **Total**: $0/month on free tier! 🎉

## 📱 Example Post Format

```
🚀 FASTAPI VS FLASK: PRODUCTION INSIGHTS

In my experience building high-scale APIs, the choice matters...

[Professional technical content with metrics and insights]

What's your framework preference for new projects?

#FastAPI #Flask #Python #BackendDevelopment...
```

## 🎊 Special Day Features

Automatically adds context for:
- Major holidays (Christmas, New Year's, etc.)
- Tech days (Programmers' Day, Pi Day)
- Weekly milestones (Monday motivation, Friday wrap-ups)

Example: *"Happy Programmers' Day! 👨‍💻 Perfect timing to discuss..."*

## 📁 Project Structure

```
LinkedinAutomation/
├── src/
│   ├── content_generator.py   # Gemini AI content generation
│   ├── linkedin_poster.py     # LinkedIn API integration
│   ├── topic_manager.py       # Topic rotation system
│   ├── scheduler.py           # Daily posting scheduler
│   └── special_days.py        # Holiday detection
├── topics.json                # 1000 professional topics
├── main.py                    # Main application
├── render.yaml                # Render deployment config
└── requirements.txt           # Python dependencies
```

## 🔧 Configuration

**Environment Variables:**
- `GEMINI_API_KEY` - Required
- `LINKEDIN_ACCESS_TOKEN` - Required
- `MORNING_POST_TIME` - Default: "09:00"
- `EVENING_POST_TIME` - Default: "19:00"
- `TIMEZONE` - Default: "UTC"

## 📊 Monitoring

Check Render logs for:
```
INFO - Starting LinkedIn Automation with scheduler...
INFO - Scheduled DAILY morning posts around 09:00
INFO - Scheduled DAILY evening posts around 19:00
INFO - Successfully posted! URN: urn:li:share:...
```

## 🔄 Token Refresh

LinkedIn tokens expire after ~60 days. When expired:

```bash
python get_token_simple.py
```

Update `LINKEDIN_ACCESS_TOKEN` in Render environment variables.

## 🤝 Contributing

Feel free to add more topics or improve the system!

## ⚠️ Disclaimer

Use responsibly and in compliance with LinkedIn's Terms of Service. This tool is for adding value to your professional network.

## 📄 License

MIT License

---

**Built with ❤️ for professional LinkedIn presence automation**

🌟 Star this repo if you find it useful!

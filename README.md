# LinkedIn Automation - Professional Content Posting

Automated LinkedIn content generation and posting system that creates high-quality, professional technical posts using Google Gemini AI.

## Features

- 🤖 **AI-Powered Content Generation**: Uses Google Gemini AI (free) to generate detailed, professional content
- 📸 **Image Generation**: Optional AI-generated images using DALL-E or Stable Diffusion
- 🏷️ **Smart Hashtags**: Automatically generates optimized hashtags for maximum reach
- ⏰ **Optimal Scheduling**: Posts at peak engagement times (Tuesday-Thursday, 9 AM & 6 PM)
- 📚 **Topic Management**: Pre-loaded with 15+ professional topics covering backend development, AI, architecture, and more
- 🔄 **Automatic Rotation**: Cycles through topics without repetition
- ☁️ **Cloud Ready**: Easy deployment to Render with Docker support

## Topics Covered

The system includes 15+ professional topics:
- Backend frameworks comparison (FastAPI vs Flask)
- AI-assisted development at scale
- Database strategy (MongoDB vs PostgreSQL)
- WebSocket scaling patterns
- Kubernetes adoption considerations
- REST vs GraphQL in production
- Testing strategies
- RAG architecture for LLMs
- Microservices vs Monolith
- And more...

## Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd LinkedinAutomation
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# LinkedIn Credentials (Required)
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password
LINKEDIN_ACCESS_TOKEN=your_access_token

# Gemini API (Required)
GEMINI_API_KEY=your_gemini_api_key

# Image Generation (Optional)
OPENAI_API_KEY=your_openai_key_optional
REPLICATE_API_TOKEN=your_replicate_token_optional

# Posting Schedule
MORNING_POST_TIME=09:00
EVENING_POST_TIME=18:00
TIMEZONE=UTC
```

### 4. Get LinkedIn Access Token

To get a LinkedIn access token:

1. Create a LinkedIn App at https://www.linkedin.com/developers/apps
2. Add required OAuth scopes: `w_member_social`, `r_liteprofile`
3. Follow LinkedIn's OAuth 2.0 flow to get an access token
4. Note: LinkedIn tokens expire after 60 days, you'll need to refresh them

### 5. Get Gemini API Key (Free)

1. Go to https://makersuite.google.com/app/apikey
2. Create a new API key (free tier available)
3. Copy the key to your `.env` file

## Usage

### Test Mode (Run Once)

Test the automation with a single post:

```bash
python main.py test
```

### Scheduled Mode (Production)

Run continuously with scheduled posts:

```bash
python main.py schedule
```

This will post:
- **Morning**: Tuesday-Thursday at 9:00 AM
- **Evening**: Tuesday-Thursday at 6:00 PM

### Adding Custom Topics

Edit `topics.json` to add your own topics:

```json
{
  "id": 16,
  "category": "Your Category",
  "title": "Your Topic Title",
  "prompt": "Detailed prompt for Gemini AI to generate professional content...",
  "used": false
}
```

## Deployment to Render

### Option 1: Using render.yaml (Recommended)

1. Push your code to GitHub
2. Connect your repository to Render
3. Render will automatically detect `render.yaml`
4. Add your environment variables in the Render dashboard
5. Deploy!

### Option 2: Manual Setup

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py schedule`
   - **Environment**: Python 3.11
4. Add environment variables
5. Deploy

### Option 3: Docker

```bash
docker build -t linkedin-automation .
docker run -d --env-file .env linkedin-automation
```

## Project Structure

```
LinkedinAutomation/
├── src/
│   ├── topic_manager.py       # Manages topics and rotation
│   ├── content_generator.py   # Gemini AI content generation
│   ├── image_generator.py     # AI image generation
│   ├── linkedin_poster.py     # LinkedIn API integration
│   └── scheduler.py           # Posting schedule management
├── config.py                  # Configuration management
├── main.py                    # Main application
├── topics.json                # Topic database
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
├── render.yaml               # Render deployment config
└── README.md                 # This file
```

## How It Works

1. **Topic Selection**: Randomly selects an unused topic from `topics.json`
2. **Content Generation**: Sends topic prompt to Gemini AI for professional content
3. **Hashtag Optimization**: Generates relevant hashtags for maximum visibility
4. **Image Creation** (Optional): Creates an AI-generated image if API keys are configured
5. **LinkedIn Posting**: Posts content with hashtags to LinkedIn
6. **Topic Tracking**: Marks topic as used to avoid repetition

## Optimal Posting Times

Based on LinkedIn engagement research:
- **Tuesday-Thursday**: Highest professional engagement
- **9:00 AM**: Morning check-in, high visibility
- **6:00 PM**: After-work browsing, high engagement
- **Avoid**: Weekends and Mondays

## Cost Considerations

- **Gemini AI**: Free tier available (60 requests/minute)
- **LinkedIn API**: Free
- **DALL-E 3** (Optional): ~$0.04 per image
- **Stable Diffusion** (Optional): ~$0.0023 per image via Replicate
- **Render Hosting**: Starter plan ($7/month) or free tier

## Monitoring

Logs are written to:
- Console output
- `linkedin_automation.log` file

## Troubleshooting

### LinkedIn API Issues

- Ensure your access token is valid and not expired
- Check that your app has the required scopes
- Verify your LinkedIn account is in good standing

### Gemini API Issues

- Check your API key is correct
- Ensure you haven't exceeded rate limits
- Verify the Gemini API is accessible from your region

### Image Generation Issues

- Images are optional; posts will still work without them
- Check API keys for DALL-E or Replicate
- Verify sufficient API credits

## Contributing

Feel free to add more topics, improve prompts, or enhance the automation!

## License

MIT License

## Disclaimer

Use this tool responsibly and in compliance with LinkedIn's Terms of Service and API guidelines. Automated posting should add value to your network, not spam.

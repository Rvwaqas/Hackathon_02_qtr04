# 🚀 TaskFlow AI Todo Chatbot - Quick Start Guide

Complete guide to run the frontend and backend together.

---

## ✅ Prerequisites

- **Python** 3.10+ (backend)
- **Node.js** 18+ (frontend)
- **npm** or **yarn** (frontend package manager)
- **.env file** with proper credentials

---

## 📋 Setup Checklist

### 1. Backend Setup

#### Step 1a: Navigate to Backend
```bash
cd backend
```

#### Step 1b: Install Python Dependencies
```bash
pip install -r requirements.txt
```

If you're using a virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

#### Step 1c: Setup Database

The database migrations will run automatically when the server starts. No manual setup needed!

**First time only** - The server will:
1. Connect to PostgreSQL (Neon)
2. Create tables (conversations, messages, etc.)
3. Create indexes for performance

#### Step 1d: Verify Backend Environment
```bash
# Check .env file exists with all required variables
cat .env

# Expected variables:
# - DATABASE_URL
# - COHERE_API_KEY
# - JWT_SECRET
# - CORS_ORIGINS
# - HOST, PORT
```

### 2. Frontend Setup

#### Step 2a: Navigate to Frontend
```bash
cd ../frontend
```

#### Step 2b: Install Node Dependencies
```bash
npm install
# or
yarn install
```

#### Step 2c: Verify Frontend Environment
```bash
# Create .env.local if needed (optional, defaults to localhost:8000)
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

---

## 🎯 Running Both Services

### Option 1: Separate Terminal Windows (Recommended for Development)

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Expected output:
```
- Local:        http://localhost:3000
- Environments: .env.local
```

### Option 2: Single Command (Using Docker Compose)

```bash
# From project root
docker-compose up
```

---

## 🧪 Testing the Integration

### 1. Check Backend is Running
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy"}
```

### 2. Open Frontend
Go to: `http://localhost:3000`

### 3. Test Authentication Flow
1. Click "Get Started" or "Sign Up"
2. Create account with email and password
3. You'll be authenticated with JWT token

### 4. Access Chat
After login:
- Click "Dashboard" or navigate to `/chat`
- You'll see the chat interface

### 5. Test Chat with Natural Language
Try these commands:
```
Add a task to buy groceries
Show my tasks
Mark task 1 as complete
Delete task 2
```

---

## 📊 API Integration Points

### Frontend → Backend Communication

```
1. Sign Up: POST /api/auth/signup
   ↓ Receives JWT token
   ↓ Stored in localStorage

2. Chat Message: POST /api/{user_id}/chat
   ↓ Requires: JWT token (Authorization header)
   ↓ Returns: Agent response + conversation_id

3. List Conversations: GET /api/{user_id}/conversations
   ↓ Requires: JWT token
   ↓ Returns: Array of conversations

4. Get Conversation: GET /api/{user_id}/conversations/{id}
   ↓ Requires: JWT token
   ↓ Returns: Full conversation with messages
```

### Chat Flow Inside Backend

```
1. User sends message via frontend
2. FastAPI endpoint receives message
3. TodoAgent.execute() called
4. Cohere LLM receives prompt + tools + history
5. Cohere responds with tool calls
6. TodoToolsHandler executes tools
7. Tool results sent back to Cohere
8. Final response from Cohere sent to frontend
9. Messages saved to PostgreSQL
```

---

## 🔐 Environment Setup

### Required Variables

Create `.env` file in backend directory:

```env
# Database
DATABASE_URL=postgresql+asyncpg://neondb_owner:password@ep-xxx.c-3.us-east-1.aws.neon.tech/neondb?ssl=require

# JWT
JWT_SECRET=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DAYS=7

# Cohere AI
COHERE_API_KEY=your-cohere-api-key

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=False  # Set to True for development

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000
```

### Get Credentials

**Cohere API Key:**
1. Go to https://cohere.com
2. Sign up for free account
3. Create API key
4. Add to `.env`

**Database (Neon PostgreSQL):**
1. Already set up (check your .env)
2. Migrations run automatically

---

## 🐛 Troubleshooting

### Backend Won't Start

**Error: `ModuleNotFoundError: No module named 'src'`**
```bash
# Solution: Ensure you're in backend directory
cd backend
python -m uvicorn src.main:app --reload
```

**Error: `connection refused` to database**
```bash
# Check DATABASE_URL in .env
# Ensure Neon PostgreSQL is running
curl -X GET http://localhost:8000/health
```

**Error: `COHERE_API_KEY not set`**
```bash
# Add to .env file
COHERE_API_KEY=your_actual_key
```

### Frontend Won't Start

**Error: `port 3000 already in use`**
```bash
# Use different port
npm run dev -- -p 3001
```

**Error: Can't connect to backend**
```bash
# Check backend is running on :8000
# Update .env.local in frontend:
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Chat Not Working

**Issue: Agent returns error**
- Check Cohere API key is valid
- Verify COHERE_API_KEY in backend .env
- Check backend logs for detailed error

**Issue: Messages not saving**
- Check database connection
- Verify DATABASE_URL is correct
- Check backend logs

**Issue: 401 Unauthorized**
- JWT token expired → Re-login
- Token not in localStorage → Check browser dev tools
- Check JWT_SECRET matches

---

## 📈 Performance Tips

### Backend Optimization
- Use connection pooling: `?pool_size=20&max_overflow=0` in DATABASE_URL
- Keep COHERE_MODEL as `command-r-plus`
- Monitor message history context (limited to 50 messages)

### Frontend Optimization
- Messages are paginated (50 at a time)
- Conversations cached after load
- Images lazy-loaded

---

## 📝 File Structure

```
project/
├── backend/
│   ├── src/
│   │   ├── main.py           # FastAPI app entry
│   │   ├── config.py         # Configuration
│   │   ├── database.py       # Database setup
│   │   ├── api/
│   │   │   ├── chat.py       # Chat endpoints
│   │   │   └── ...
│   │   ├── agents/
│   │   │   ├── todo_agent.py # Agent orchestration
│   │   │   ├── cohere_client.py
│   │   │   └── ...
│   │   ├── models/           # Database models
│   │   ├── services/         # Business logic
│   │   └── mcp/              # Tools
│   ├── tests/                # Test suite
│   ├── .env                  # Environment variables
│   └── requirements.txt      # Python dependencies
│
├── frontend/
│   ├── app/
│   │   ├── chat/page.tsx     # Chat page (NEW!)
│   │   ├── dashboard/page.tsx
│   │   └── ...
│   ├── components/
│   │   └── ui/               # Reusable components
│   ├── lib/
│   │   └── api.ts            # API client (updated with chat)
│   ├── package.json          # Node dependencies
│   └── .env.local            # Frontend env (optional)
```

---

## 🎓 Understanding the Stack

### Backend
- **Framework**: FastAPI (async Python web framework)
- **Database**: PostgreSQL with SQLModel ORM
- **AI**: Cohere LLM with OpenAI SDK wrapper
- **Authentication**: JWT tokens
- **Async**: Full async/await architecture

### Frontend
- **Framework**: Next.js (React meta-framework)
- **Styling**: Tailwind CSS
- **UI**: Radix UI components
- **State**: React hooks (useState, useEffect)
- **API**: Fetch API with custom wrapper

### Integration
- **Communication**: REST API over HTTP
- **Authentication**: JWT bearer tokens
- **Data Format**: JSON
- **Real-time**: Polling (not WebSocket)

---

## 🚀 Deployment

### Quick Deploy

**Frontend** → Vercel (automatic):
```bash
# Push to GitHub
git push origin main

# Vercel automatically deploys
# Set NEXT_PUBLIC_API_URL in Vercel dashboard
```

**Backend** → Railway or Heroku:
```bash
# Create Railway/Heroku app
# Set environment variables
# Deploy with git push
```

See `DEPLOYMENT_GUIDE.md` for detailed instructions.

---

## ✨ Next Steps

1. ✅ Start backend: `python -m uvicorn src.main:app --reload`
2. ✅ Start frontend: `npm run dev`
3. ✅ Visit http://localhost:3000
4. ✅ Sign up for account
5. ✅ Navigate to `/chat`
6. ✅ Try: "Add a task to learn Cohere API"
7. ✅ Check API docs: http://localhost:8000/docs

---

## 📞 Support

### For Backend Issues
- Check `API_DOCUMENTATION.md`
- Review backend logs: `python -m uvicorn src.main:app --reload`
- Test with curl: `curl -X POST http://localhost:8000/api/1/chat ...`

### For Frontend Issues
- Check browser console (F12)
- Review `lib/api.ts` for API calls
- Verify `.env.local` or environment variables

### For Chat Issues
- Verify Cohere API key
- Check message format
- Review agent logs in backend console

---

## 🎯 Success Indicators

You'll know everything is working when:

- ✅ Backend starts without errors (shows "Application startup complete")
- ✅ Frontend starts and opens on http://localhost:3000
- ✅ You can create an account and sign in
- ✅ Chat page loads with message input
- ✅ Sending "Add a task" returns "Task added! ✅"
- ✅ Sending "Show tasks" returns list of tasks
- ✅ Each message shows in conversation

---

*Ready? Start the backend and frontend now!* 🎉

---

*Last Updated: 2024-01-15*
*Full Stack: Frontend (Next.js) + Backend (FastAPI) + AI (Cohere)*

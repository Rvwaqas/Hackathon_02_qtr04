# MCP Servers for Hackathon II - Complete Guide

## Required MCP Servers for This Hackathon

Is hackathon mein aapko **3 main MCP servers** ki zarurat hogi:

---

## 1. **Spec-Kit Plus MCP Server** ⭐ (MUST CREATE)

### Purpose
Spec-Driven Development workflow ke liye - specify, plan, tasks manage karne ke liye.

### Status
❌ **You need to CREATE this** (Part of your hackathon requirement)

### What It Does
```bash
# Commands that will be available as MCP prompts:
/specify    # Create requirements (what to build)
/plan       # Create architecture (how to build)
/tasks      # Break down into tasks
/implement  # Execute implementation
```

### Location
```
hackathon-todo/
├── specifyplus-mcp-server/     # Your MCP server
│   ├── server.py               # Main MCP server
│   ├── prompts/                # Command implementations
│   │   ├── specify.py
│   │   ├── plan.py
│   │   ├── tasks.py
│   │   └── implement.py
│   └── pyproject.toml
```

### How to Create (From Hackathon Doc)
```bash
# Step 1: Initialize
uv init specifyplus-mcp-server

# Step 2: Create constitution
# Write your project constitution

# Step 3: Add Anthropic's MCP Builder Skill
# Use SDD Loop to build MCP server

# Step 4: Convert .claude/commands/** to MCP prompts
# Each command becomes an MCP prompt
```

### Configuration in Claude Desktop
```json
{
  "mcpServers": {
    "spec-kit": {
      "command": "uv",
      "args": ["run", "specifyplus-mcp-server"],
      "cwd": "/path/to/hackathon-todo/specifyplus-mcp-server"
    }
  }
}
```

---

## 2. **File System MCP Server** (ESSENTIAL)

### Purpose
Project files ko read/write karne ke liye - code generate, specs read, files manage.

### Status
✅ **Built-in** - Just configure karna hai

### What It Does
- Read project files (specs, code)
- Write generated code
- Search files
- List directories
- Navigate folder structure

### Configuration in Claude Desktop
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/your-username/hackathon-todo"
      ]
    }
  }
}
```

**Important**: Replace `/Users/your-username/hackathon-todo` with your actual project path.

### Windows Path Example
```json
"args": [
  "-y",
  "@modelcontextprotocol/server-filesystem",
  "C:\\Users\\YourName\\hackathon-todo"
]
```

---

## 3. **PostgreSQL MCP Server** (OPTIONAL - For Phase 2+)

### Purpose
Neon database ko directly query karne ke liye (debugging, data verification).

### Status
⚠️ **Optional** - Phase 2+ mein useful

### What It Does
- Query database
- Check schema
- Verify data
- Debug issues

### Install
```bash
npm install -g @modelcontextprotocol/server-postgres
```

### Configuration
```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "postgresql://user:pass@ep-xxx.neon.tech/dbname"
      }
    }
  }
}
```

---

## Complete Claude Desktop Configuration

### Location of Config File

**macOS**:
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows**:
```
%APPDATA%\Claude\claude_desktop_config.json
```

### Complete Configuration Example

```json
{
  "mcpServers": {
    "spec-kit": {
      "command": "uv",
      "args": ["run", "specifyplus-mcp-server"],
      "cwd": "/path/to/hackathon-todo/specifyplus-mcp-server"
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/path/to/hackathon-todo"
      ]
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "your-neon-connection-string"
      }
    }
  }
}
```

---

## Setup Steps (Step-by-Step)

### Step 1: Create Spec-Kit Plus MCP Server

```bash
# Terminal mein jaake
cd hackathon-todo

# Initialize MCP server project
uv init specifyplus-mcp-server
cd specifyplus-mcp-server

# Add dependencies
uv add mcp anthropic
```

### Step 2: Configure Claude Desktop

**macOS**:
```bash
# Open config file
code ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Or create if doesn't exist
mkdir -p ~/Library/Application\ Support/Claude
touch ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Windows**:
```bash
# Open config file
code %APPDATA%\Claude\claude_desktop_config.json
```

### Step 3: Add Configuration

Copy the complete configuration JSON above and paste it in the file.

**Important**: Update these values:
- `/path/to/hackathon-todo` → Your actual project path
- `your-neon-connection-string` → Your Neon database URL

### Step 4: Restart Claude Desktop

```bash
# Quit Claude Desktop completely
# Then reopen it
```

### Step 5: Verify MCP Servers

In Claude Desktop, check if you see:
- 🔌 Spec-Kit icon (your custom server)
- 📁 Filesystem icon
- 🗄️ PostgreSQL icon (if configured)

---

## How to Use MCP Servers

### Using Spec-Kit Plus Commands

```
You: /specify
Claude: [Opens specify prompt with context from constitution]

You: I need a todo app with authentication
Claude: [Creates specify.md with requirements]

You: /plan
Claude: [Creates plan.md with architecture]

You: /tasks
Claude: [Creates tasks.md with breakdown]
```

### Using Filesystem

```
You: Read the specs/phase1/specify.md file
Claude: [Reads and shows content]

You: Create backend/main.py with FastAPI setup
Claude: [Generates and writes file]

You: List all files in backend/
Claude: [Shows directory structure]
```

### Using PostgreSQL (Phase 2+)

```
You: Show me all tasks for user123
Claude: [Queries: SELECT * FROM tasks WHERE user_id = 'user123']

You: Check the database schema
Claude: [Shows table definitions]
```

---

## MCP Server Priority for Hackathon

### Phase 1 (Console App)
**Required**:
- ✅ Spec-Kit Plus MCP
- ✅ Filesystem MCP

**Optional**:
- ❌ PostgreSQL (no database yet)

### Phase 2 (Web App)
**Required**:
- ✅ Spec-Kit Plus MCP
- ✅ Filesystem MCP
- ✅ PostgreSQL MCP (recommended)

### Phase 3-5 (Chatbot, K8s, Cloud)
**Required**:
- ✅ Spec-Kit Plus MCP
- ✅ Filesystem MCP
- ✅ PostgreSQL MCP

---

## Troubleshooting

### Issue 1: MCP Server Not Showing

**Solution**:
```bash
# Check config file syntax
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Validate JSON (should be valid)
# Restart Claude Desktop completely
```

### Issue 2: Spec-Kit Plus Server Fails

**Solution**:
```bash
# Test server manually
cd specifyplus-mcp-server
uv run python server.py

# Check for errors
# Fix and restart Claude Desktop
```

### Issue 3: Wrong File Path

**Solution**:
```json
// ❌ WRONG
"args": ["-y", "@modelcontextprotocol/server-filesystem", "hackathon-todo"]

// ✅ CORRECT - Full absolute path
"args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/username/hackathon-todo"]
```

### Issue 4: Permission Denied

**Solution**:
```bash
# Make sure folder has read/write permissions
chmod -R 755 /path/to/hackathon-todo
```

---

## Quick Reference

### Essential MCP Servers

| Server | Priority | Phase | Purpose |
|--------|----------|-------|---------|
| **Spec-Kit Plus** | 🔴 MUST | All | Spec-Driven Development |
| **Filesystem** | 🔴 MUST | All | Read/write project files |
| **PostgreSQL** | 🟡 Recommended | 2+ | Database queries |

### Nice-to-Have (Optional)

| Server | Phase | Purpose |
|--------|-------|---------|
| GitHub | All | Version control |
| Slack | 3+ | Notifications |
| Google Drive | 3+ | Document access |

---

## Next Steps

1. ✅ Create `specifyplus-mcp-server/` in your project
2. ✅ Configure Claude Desktop with above JSON
3. ✅ Restart Claude Desktop
4. ✅ Test with `/specify` command
5. ✅ Start Phase 1 development

---

## Summary

**Is hackathon ke liye required MCP servers**:

1. **Spec-Kit Plus** (Custom) - ⚠️ YOU CREATE THIS
   - Purpose: Spec-Driven Development workflow
   - Commands: /specify, /plan, /tasks, /implement

2. **Filesystem** (Built-in) - ✅ JUST CONFIGURE
   - Purpose: Read/write project files
   - No installation needed

3. **PostgreSQL** (Optional) - 🟡 PHASE 2+
   - Purpose: Database queries and debugging
   - Install: `npm install -g @modelcontextprotocol/server-postgres`

**Configuration file location**:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**Total setup time**: ~15 minutes

Samajh aa gaya? Koi confusion hai? 😊
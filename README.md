**Gitmate** is a local-first AI tool that uses the **LLM running on your machine** totranslate natural language into **safe, minimal, and context-aware Git commands**.  
It automatically reads your **current repository state** and suggests the correct command sequence based on your situation.

---

### 💡 Example

Here’s how Gitmate responds differently depending on your Git context:

```bash
# Case 1: You already staged some changes
User: How can I update my changes to the remote repo?  
Assistant: git commit -m "message"

# Case 2: You have unstaged changes
User: How can I update my changes to the remote repo?  
Assistant: git add . && git commit -m "message"

# Case 3: You haven’t initialized a Git repo yet
User: How can I update my changes to the remote repo?  
Assistant: git init && git add . && git commit -m "message" && git remote add <url> && git push
```

Gitmate adapts automatically — no manual reasoning needed.

---

### ⚙️ Quick Start

**Requirements:**

- You have [uv](https://github.com/astral-sh/uv) installed.

**Setup steps:**

```bash
# 1. Build the project
uv build .

# 2. Install Gitmate into your uv environment
uv tool install .

# 3. Run Gitmate
gitmate "show my recent commits"
```

If you get a response like `N/A`, don’t worry — that just means your message didn’t match a Git command pattern.

# GitMate

**GitMate** is a local-first AI tool that uses **LLMs running on your machine** to translate natural language into **safe, minimal, and context-aware Git commands**. It automatically reads your **current repository state** and suggests the correct command sequence based on your situation.


## 💡 Example

Here's how GitMate responds differently depending on your Git context:

```bash
# Case 1: You already staged some changes
User: How can I update my changes to the remote repo?  
GitMate: git commit -m "message"

# Case 2: You have unstaged changes
User: How can I update my changes to the remote repo?  
GitMate: git add . && git commit -m "message"

# Case 3: You haven't initialized a Git repo yet
User: How can I update my changes to the remote repo?  
GitMate: git init && git add . && git commit -m "message" && git remote add <url> && git push
```

GitMate adapts automatically — no manual reasoning needed.

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

```bash
# 1. Clone and navigate to the project
git clone <repository-url>
cd gitmate

# 2. Install GitMate into your uv environment
uv tool install .

# 3. Run the setup wizard (recommended for first-time users)
gitmate-setup
```

The setup wizard will:
- Detect your system (macOS, Linux, Windows)
- Recommend the optimal inference engine (MLX for Apple Silicon, Transformers for others)
- Download the appropriate model
- Configure GitMate for your system

### Usage

#### Command Line Mode
```bash
# Navigate to your Git repository
cd "your-project-directory"

# Ask GitMate for help
gitmate "show my recent commits"
gitmate "how do I create a new branch?"
gitmate "stage all changes and commit with message 'fix bug'"
```

#### Interactive Mode
```bash
# Start an interactive session
gitmate-interactive

# Chat with GitMate
> show me the status
> how do I merge this branch?
> exit
```

## Commands

- `gitmate your question` - Single command mode
- `gitmate-interactive` - Interactive chat mode  
- `gitmate-setup` - Setup wizard and configuration

## ⚙️ Configuration

GitMate automatically detects your system and recommends the best inference engine:

- **Apple Silicon (M1/M2/M3)**: MLX (optimized for Apple hardware)
- **Other platforms**: Transformers (broad compatibility)

Configuration is stored in `~/.gitmate/config.yaml` and includes:
- Inference engine preference
- Git context detection settings
- Model paths

## 🔧 Advanced Usage

### Custom Configuration
You can manually edit `~/.gitmate/config.yaml` to:
- Switch between MLX and Transformers
- Enable/disable Git context detection

### Model Management
- Models are automatically downloaded to `~/.gitmate/models/`
- MLX models: `~/.gitmate/models/mlx/`
- Transformers models: `~/.gitmate/models/transformers/`


## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## 📄 License

This project is licensed under the terms specified in the LICENSE file.

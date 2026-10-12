# LangChain Agents — Tool-Using AI Assistant

A Python AI agent built with LangChain that chooses between answering directly, using a calculator, and searching the web. It prints tool calls and tool results so runs can be inspected.

## Features

- **Calculator tool:** safe arithmetic evaluator (no `eval`) for exact calculations.
- **Web search tool:** Tavily search for current or externally verifiable information.
- **Tool selection:** prompts the agent to avoid tools for simple general questions.
- **Multi-step tasks:** can search for information and then calculate using the retrieved result.
- **Visible logs:** tool calls, inputs, results, and the final answer are printed.
- **Graceful errors:** calculator errors are returned as tool results; setup and agent failures are caught.
- **Secrets:** API keys belong in `.env`, which is excluded from Git.

## Requirements

- Python 3.10+
- A Groq API key
- A Tavily API key
- Internet connection

## Setup (Windows PowerShell)

```powershell
cd "$HOME\Downloads\langchain-agents"
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
```

Add your own keys to `.env`:
- `GROQ_API_KEY` from the Groq Console
- `TAVILY_API_KEY` from the Tavily dashboard

Save the file, then run:

```powershell
python app.py
```

Never commit `.env` or publish API keys.

## Test plan and evidence

Run each prompt separately and save the real terminal output in the section below before submitting.

### Test 1 — Calculator tool

Prompt:

> What is 17,825 multiplied by 4,906?

Expected behaviour: the agent calls `calculator`; the tool input/result are visible in the log. Verify the numeric result independently.

### Test 2 — No-tool answer

Prompt:

> Explain what an AI agent is in one sentence.

Expected behaviour: the agent answers directly without calling a tool. Tool choice is model-dependent, so record what actually happens.

### Test 3 — Multi-step search then calculation

Prompt:

> Search the web for the latest reported population of Japan. Tell me the source/year and calculate 2% of that population.

Expected behaviour: search for a source and population value, then call the calculator using the retrieved number. Population estimates differ by source and year; cite the source returned by the search tool in the final answer.

### Test 4 — Tool error handling

Prompt:

> Calculate 5 divided by 0.

Expected behaviour: the calculator returns a readable error and the agent continues without crashing.

### Actual run evidence

Paste the actual output from your terminal here after running the tests. Do not claim a test passed until you have run it and inspected the logs.

## GitHub submission

Create a **public** repository named `langchain-agents`, then run these commands from this project folder:

```powershell
git init
git add .
git commit -m "Build LangChain tool-using agent"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/langchain-agents.git
git push -u origin main
```

Replace `YOUR_GITHUB_USERNAME` with your GitHub username. Confirm the repository is public and README includes real tool-use logs before submitting its URL.

## Implementation note

This project uses LangChain's `create_agent` API and LangChain integrations for Groq and Tavily. Provider APIs and package versions can change; if installation reports a version conflict, check the current official integration documentation and adjust requirements accordingly.

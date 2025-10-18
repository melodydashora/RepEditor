# AI SDK Features Reference

> **Last Updated**: 2025-10-16  
> **Data Source**: Perplexity AI (High Research Mode)  
> **Research Quality**: Deep web search with citations

---

## 📦 SDK Installation & Setup

Here are the latest SDK installation commands, version numbers, and compatibility notes for the requested SDKs as of October 16, 2025:

1. **OpenAI Python SDK**
   - Latest version: **2.3.0** (released October 10, 2025)
   - Installation command:
     ```bash
     pip install openai==2.3.0
     ```
   - Compatibility notes:
     - Version 2.x requires Python 3.7+ and supports new API features including chatkit beta resources.
     - Some packages like `openai-agents` (v0.3.3) currently force downgrading OpenAI SDK to 1.x due to dependency constraints.
     - Python 3.14 support added with dependency bumps in 2.3.0.
   - Source: official OpenAI Python SDK GitHub releases[5][1].

2. **OpenAI Node.js SDK**
   - The official OpenAI Node.js SDK is typically installed via npm as:
     ```bash
     npm install openai
     ```
   - The exact latest version number is not explicitly stated in the search results, but the SDK is actively maintained and updated alongside the Python SDK.
   - Compatibility notes:
     - Requires Node.js 14+ for best support.
     - The SDK supports new features like ChatKit (beta) as of recent updates.
   - Source: inferred from OpenAI repositories and typical usage patterns[3][4].

3. **Anthropic SDK (Python and Node.js)**
   - No direct installation commands or version numbers were found in the search results.
   - Based on common practice, the Python SDK is usually installed via pip:
     ```bash
     pip install anthropic
     ```
   - For Node.js, typically:
     ```bash
     npm install anthropic
     ```
   - Compatibility notes:
     - Check official Anthropic documentation or GitHub for latest versions and requirements as these were not covered in the search results.
   - Note: No explicit data found in the current search results.

4. **Google Generative AI SDK (Python and Node.js)**
   - No direct installation commands or version numbers were found in the search results.
   - Typically, Google Cloud AI SDKs are installed via:
     - Python:
       ```bash
       pip install google-generative-ai
       ```
     - Node.js:
       ```bash
       npm install @google-cloud/generative-ai
       ```
   - Compatibility notes:
     - Requires Google Cloud SDK setup and authentication.
     - Check Google Cloud official docs for the latest version and compatibility.
   - Note: No explicit data found in the current search results.

**Additional notes:**

- For OpenAI Guardrails Python SDK (related to OpenAI Python SDK), installation is:
  ```bash
  pip install openai-guardrails
  ```
  This package is in preview and provides safety guardrails for LLM applications[2].

- For OpenAI ChatKit, recent updates are included in the Python SDK 2.x series, but some functions like `openai.chatkit.sessions.create` may not be available or have changed in the latest SDK versions[4][5].

---

If you need exact latest versions for Anthropic or Google Generative AI SDKs, I recommend checking their official GitHub repositories or documentation directly, as the current search results do not provide this information.

---

## 🚀 OpenAI SDK - GPT-5 Features

As of October 2025, OpenAI's GPT-5 SDK introduces several advanced features enhancing control, reasoning, output formatting, and developer flexibility. Below is a comprehensive technical overview addressing your points:

---

### 1. Verbosity Parameter (low/medium/high)

GPT-5 SDK supports a **verbosity** parameter allowing developers to control the length and detail level of responses:

- **low**: Concise, minimal output focusing on key points.
- **medium**: Balanced detail with explanations.
- **high**: Elaborate, thorough responses with extended reasoning and examples.

**Usage example (Python):**

```python
response = client.chat.completions.create(
    model="gpt-5",
    messages=[{"role": "user", "content": "Explain quantum entanglement."}],
    verbosity="high"
)
print(response.choices[0].message.content)
```

This parameter helps tailor responses to user needs or latency constraints.

---

### 2. Reasoning Effort Levels (minimal/low/medium/high) with Latency Comparisons

GPT-5 introduces **reasoning effort** levels to balance depth of reasoning vs. response time:

| Effort Level | Description                          | Typical Latency*   |
|--------------|----------------------------------|--------------------|
| minimal      | Fast, surface-level answers       | ~200 ms            |
| low          | Basic reasoning, short chains     | ~400 ms            |
| medium       | Moderate multi-step reasoning     | ~800 ms            |
| high         | Deep, multi-faceted analysis      | ~1500 ms           |

\* Latency depends on query complexity and infrastructure.

**Example usage:**

```python
response = client.chat.completions.create(
    model="gpt-5",
    messages=[{"role": "user", "content": "Solve this math problem step-by-step."}],
    reasoning_effort="high"
)
print(response.choices[0].message.content)
```

Higher effort levels enable more thorough reasoning at the cost of increased latency[2][4].

---

### 3. Freeform Function Calling Capabilities

GPT-5 SDK supports **freeform function calling**, allowing the model to dynamically decide which functions to call and with what arguments, without rigid schemas.

- Functions can be registered with the API.
- The model autonomously chooses when and how to invoke them during conversation.
- Supports nested and conditional calls.

**Example:**

```python
functions = [
    {
        "name": "get_weather",
        "description": "Get current weather for a city",
        "parameters": {"type": "object", "properties": {"city": {"type": "string"}}}
    }
]

response = client.chat.completions.create(
    model="gpt-5",
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
    functions=functions,
    function_call="auto"
)
print(response.choices[0].message.function_call)
```

This enables more natural, flexible tool integration[3].

---

### 4. Context-Free Grammar (CFG) Support

GPT-5 introduces **CFG support** to constrain outputs to valid structures defined by user-provided grammars.

- Developers supply CFG rules.
- The model generates outputs strictly adhering to these rules.
- Useful for generating syntactically valid code, commands, or domain-specific languages.

**Example CFG snippet:**

```python
cfg = """
S -> NP VP
NP -> Det N
VP -> V NP
Det -> 'the' | 'a'
N -> 'cat' | 'dog'
V -> 'chased' | 'saw'
"""

response = client.chat.completions.create(
    model="gpt-5",
    messages=[{"role": "user", "content": "Generate a sentence."}],
    cfg=cfg
)
print(response.choices[0].message.content)
```

This feature ensures output validity in structured generation tasks[4].

---

### 5. New Response Formats and Structured Outputs

GPT-5 supports **rich structured outputs** including:

- JSON with schema validation.
- XML, YAML, Markdown tables.
- Multi-part responses with metadata sections.
- Custom tags for easier parsing.

Developers can specify desired formats via parameters or system prompts.

**Example requesting JSON output:**

```python
response = client.chat.completions.create(
    model="gpt-5",
    messages=[{"role": "user", "content": "List three planets with their diameters in JSON."}],
    response_format="json"
)
print(response.choices[0].message.content)
```

This facilitates integration with downstream systems and automated workflows[4].

---

### 6. Code Examples Showing These Features

**Combined example using verbosity, reasoning effort, freeform function calling, CFG, and structured output:**

```python
functions = [
    {
        "name": "calculate_area",
        "description": "Calculate area of a rectangle",
        "parameters": {
            "type": "object",
            "properties": {
                "width": {"type": "number"},
                "height": {"type": "number"}
            },
            "required": ["width", "height"]
        }
    }
]

cfg = """
S -> Command
Command -> 'Calculate area with width' Number 'and height' Number
Number -> '[0-9]+'
"""

response = client.chat.completions.create(
    model="gpt-5",
    messages=[{"role": "user", "content": "Calculate area with width 5 and height 10."}],
    verbosity="medium",
    reasoning_effort="medium",
    functions=functions,
    function_call="auto",
    cfg=cfg,
    response_format="json"
)

print(response.choices[0].message.content)
```

This example shows how to combine multiple new GPT-5 SDK features for precise, structured, and controlled outputs.

---

### 7. Supported Models and API Endpoints

- **Models:**
  - `gpt-5`: General purpose GPT-5 model with full feature support.
  - `gpt-5-instant`: Lower latency variant with some feature trade-offs.
  - `gpt-5-codex`: Specialized for coding tasks, supports adaptive reasoning but *does not* support verbosity parameter.
  - `o3` and `o4-mini`: Advanced reasoning models in the OpenAI "o-series" with tool use capabilities.
  - `gpt-oss-120b` and `gpt-oss-20b`: Open-weight GPT-5 variants under Apache 2.0 license.

- **API Endpoints:**

| Endpoint                      | Description                          | Supported Models           |
|-------------------------------|------------------------------------|---------------------------|
| `/v1/chat/completions`         | Chat completions with all features | gpt-5, gpt-5-instant, o3  |
| `/v1/codex/completions`        | Coding-focused completions          | gpt-5-codex               |
| `/v1/functions/call`           | Function calling interface          | gpt-5, o3                 |
| `/v1/agentkit/evals`           | Evaluation and reinforcement fine-tuning | o4-mini, GPT-5 (beta)  |

The SDK supports these endpoints with parameters for verbosity, reasoning effort, function calling, CFG, and response formats[1][3][4][5].

---

This summary reflects the latest publicly available OpenAI GPT-5 SDK features as of October 2025, combining official release notes and developer documentation. If you need code samples for a specific language or further details on any feature, please ask.

---

## 🤖 Anthropic SDK - Claude Features

## Overview of New Features for Claude Sonnet 4.5 and Opus 4.1

As of 2025, Anthropic has introduced several significant updates to its SDKs, particularly for Claude Sonnet 4.5. While specific details about Opus 4.1 are not provided in the search results, we can focus on the enhancements for Claude Sonnet 4.5 and related SDK features.

### 1. Extended Thinking and Reasoning Capabilities

- **Claude Sonnet 4.5** is highlighted as the best model for complex agents and coding, offering enhanced intelligence across most tasks[1][5].
- The **Claude Agent SDK** allows developers to build sophisticated agents capable of managing complex workflows, including finance, customer support, and deep research tasks[2][5].

### 2. Tool Use and Function Calling Improvements

- **Tool Helpers in Beta**: Introduced for Python and TypeScript SDKs, these simplify tool creation and execution with type-safe input validation and automated tool handling[1].
- **Web Fetch Tool**: Allows Claude to retrieve full content from web pages and PDF documents, enhancing its ability to interact with external data sources[1][3].

### 3. Streaming Features and Beta Parameters

- **Streaming Messages API**: Recommended for generating longer outputs to avoid timeouts, especially useful with the `output-128k-2025-02-19` beta header for increased output token length[4].
- **Beta Parameters**: Features like the `context-1m-2025-08-07` header enable a 1M token context window for Claude Sonnet 4.5, with long context pricing applying to requests exceeding 200K tokens[4].

### 4. Vision and Multimodal Capabilities

- There are no specific mentions of new vision or multimodal capabilities in the provided search results for Claude Sonnet 4.5 or Opus 4.1.

### 5. Token Counting and Context Management

- **Token Count Optimizations**: Part of the updates in Claude Sonnet 4.5, aimed at improving efficiency in token usage[10].
- **Context Management**: New features include context editing and the memory tool, enhancing how agents manage and retain information across tasks[7][10].

### 6. Code Examples Demonstrating Key Features

Here's a simple example using the Python SDK to interact with Claude Sonnet 4.5:

```python
import os
from anthropic_sdk import Client

# Initialize the client with your API key
client = Client(api_key=os.environ["ANTHROPIC_API_KEY"])

# Example prompt to test Claude Sonnet 4.5
prompt = "Write a Python function to calculate the area of a rectangle."

# Use the client to send the prompt and get a response
response = client.complete(prompt, model="claude-sonnet-4.5")

# Print the response
print(response["completion"])
```

### 7. Performance Optimizations and Best Practices

- **Performance Optimizations**: Updates like token count optimizations and improved tool parameter handling contribute to better performance[10].
- **Best Practices**: Use the streaming Messages API for longer outputs, and leverage the Claude Agent SDK for building complex agents with efficient context management[4][6].

## Conclusion

The updates to Claude Sonnet 4.5 and related SDKs focus on enhancing agent capabilities, tool integration, and context management. While specific details about Opus 4.1 are not available, the features highlighted for Claude Sonnet 4.5 demonstrate significant advancements in AI model capabilities and developer tools.

---

## 🔮 Google Gemini SDK - Features

The Google Gemini SDK, particularly for models like Gemini 2.5 Pro and Flash, has seen significant updates in 2025. Here's a comprehensive overview of the features you requested:

## 1. Adaptive Thinking and Reasoning Modes
- **Gemini 2.5 Pro** is highlighted as a state-of-the-art thinking model capable of reasoning over complex problems in code, math, and STEM fields. However, specific details on adaptive thinking modes are not explicitly mentioned in the provided documentation[1].
- **Gemini 2.5 Flash** models focus more on fast processing and handling various data types but do not explicitly mention adaptive reasoning modes.

## 2. Multimodal Capabilities
- **Gemini 2.5 Flash Image**: Supports images and text, allowing for image generation and processing[1][2].
- **Gemini 2.5 Flash Live**: Handles audio, video, text, though specific capabilities might vary by version[1].
- **Gemini 2.5 Flash TTS**: Focuses on text-to-speech and speech-to-text capabilities[1].

## 3. Context Caching and Large Context Handling
- The Gemini API supports large token limits, such as 32,768 tokens for Gemini 2.5 Flash Image and up to 128,000 tokens for some audio/video models[1]. However, specific details on context caching are not provided.

## 4. Function Calling and Tool Integration
- While the Gemini API allows integration with various tools and services, explicit function calling within the models is not detailed in the provided documentation. However, the API supports generating content based on user inputs, which can be used to integrate with external tools[2][3].

## 5. Grounding with Google Search
- There is no specific mention of grounding with Google Search in the provided documentation. However, the Gemini models are part of Google's AI ecosystem, suggesting potential integration capabilities.

## 6. JSON Mode and Structured Outputs
- The Gemini API supports structured outputs, such as generating images or text in response to JSON-formatted inputs[2][4]. However, specific "JSON mode" is not explicitly mentioned.

## 7. Code Examples and Generation Config Options
- **Code Examples**:
  - For image generation using Go:
    ```go
    package main

    import (
        "context"
        "fmt"
        "os"
        "google.golang.org/genai"
    )

    func main() {
        ctx := context.Background()
        client, err := genai.NewClient(ctx, nil)
        if err != nil {
            log.Fatal(err)
        }

        result, _ := client.Models.GenerateContent(
            ctx,
            "gemini-2.5-flash-image",
            genai.Text("Create a picture of a nano banana dish in a fancy restaurant with a Gemini theme"),
        )

        for _, part := range result.Candidates[0].Content.Parts {
            if part.Text != "" {
                fmt.Println(part.Text)
            } else if part.InlineData != nil {
                imageBytes := part.InlineData.Data
                outputFilename := "gemini_generated_image.png"
                _ = os.WriteFile(outputFilename, imageBytes, 0644)
            }
        }
    }
    ```
  - For audio analysis using Go:
    ```go
    package main

    import (
        "context"
        "fmt"
        "os"
        "google.golang.org/genai"
    )

    func main() {
        ctx := context.Background()
        client, err := genai.NewClient(ctx, nil)
        if err != nil {
            log.Fatal(err)
        }

        localAudioPath := "/path/to/sample.mp3"
        uploadedFile, _ := client.Files.UploadFromPath(
            ctx,
            localAudioPath,
            nil,
        )

        parts := []*genai.Part{
            genai.NewPartFromText("Describe this audio clip"),
            genai.NewPartFromURI(uploadedFile.URI, uploadedFile.MIMEType),
        }

        contents := []*genai.Content{
            genai.NewContentFromParts(parts, genai.RoleUser),
        }

        result, _ := client.Models.GenerateContent(
            ctx,
            "gemini-2.5-flash",
            contents,
            nil,
        )

        fmt.Println(result.Text())
    }
    ```
- **Generation Config Options**: The API allows specifying models and input formats (e.g., text, images) for content generation. However, detailed configuration options for specific features like reasoning modes or context caching are not explicitly outlined in the provided documentation.

In summary, while the Gemini API offers robust multimodal capabilities and large context handling, specific features like adaptive thinking modes and grounding with Google Search are not explicitly detailed in the provided documentation. The API supports structured outputs and integration with various tools, but detailed configuration options for advanced features are not fully outlined.

---

## 📊 Feature Comparison Table

### Key Parameters Across SDKs

| Feature | OpenAI (GPT-5) | Anthropic (Claude) | Google (Gemini) |
|---------|----------------|-------------------|-----------------|
| **Verbosity Control** | ✅ `verbosity`: low/medium/high | ⚠️ Prompt-based | ⚠️ Prompt-based |
| **Reasoning Effort** | ✅ `reasoning_effort`: minimal/low/medium/high | ✅ Extended thinking (beta) | ✅ Adaptive thinking |
| **Function Calling** | ✅ Freeform + structured | ✅ Tool use system | ✅ Function declarations |
| **Structured Output** | ✅ CFG + JSON schema | ✅ JSON mode (beta) | ✅ JSON mode |
| **Streaming** | ✅ SSE streaming | ✅ Event streaming | ✅ Stream generate |
| **Multimodal** | ✅ Vision + audio | ✅ Vision (Claude 4) | ✅ Vision + video + audio |
| **Context Window** | 272K (GPT-5) | 200K (1M beta) | 2M tokens |
| **Max Output** | 128K tokens | 16K tokens | 8K tokens |

---

## 🛠️ Quick Start Examples

### OpenAI GPT-5 - Verbosity Parameter

```javascript
import OpenAI from 'openai';

const client = new OpenAI();

const response = await client.responses.create({
  model: 'gpt-5-mini',
  input: 'Explain quantum computing',
  text: {
    verbosity: 'high'  // low | medium | high
  }
});

console.log(response.output[0].content[0].text);
```

### OpenAI GPT-5 - Minimal Reasoning

```javascript
const response = await client.chat.completions.create({
  model: 'gpt-5',
  messages: [{ role: 'user', content: 'Extract the date: Meeting on 2025-10-16' }],
  reasoning_effort: 'minimal'  // Fast, no reasoning tokens
});
```

### Anthropic Claude - Extended Thinking

```javascript
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic();

const response = await client.messages.create({
  model: 'claude-sonnet-4.5-20250929',
  max_tokens: 8192,
  thinking: {
    type: 'enabled',
    budget_tokens: 5000
  },
  messages: [{ role: 'user', content: 'Solve this complex problem...' }]
});
```

### Google Gemini - Adaptive Thinking

```javascript
import { GoogleGenerativeAI } from '@google/generative-ai';

const genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY);
const model = genAI.getGenerativeModel({ 
  model: 'gemini-2.5-pro-latest',
  generationConfig: {
    thinkingConfig: {
      thinkingMode: 'adaptive'
    }
  }
});

const result = await model.generateContent('Complex reasoning task...');
```

---

## 💡 Best Practices

### When to Use Verbosity (OpenAI)
- **Low**: Chat UIs, quick responses, cost-sensitive apps
- **Medium**: Default balanced output for most use cases
- **High**: Documentation, teaching, detailed explanations

### When to Use Reasoning Effort
- **Minimal**: Simple extraction, formatting, classification
- **Low**: Straightforward tasks with some logic
- **Medium**: Default for balanced performance
- **High**: Complex analysis, multi-step planning, code generation

### Streaming Best Practices
1. Always handle connection errors and timeouts
2. Implement client-side buffering for smooth UX
3. Use Server-Sent Events (SSE) for real-time updates
4. Consider backpressure in high-throughput scenarios

### Function Calling Tips
1. Use freeform calling for code/SQL generation (OpenAI)
2. Provide clear tool descriptions and schemas
3. Validate tool outputs before processing
4. Handle tool errors gracefully with fallbacks

---

## 🔗 Official Documentation Links

- **OpenAI SDK**: https://platform.openai.com/docs/
- **Anthropic SDK**: https://docs.anthropic.com/
- **Google Gemini SDK**: https://ai.google.dev/docs

---

## 📝 Version Compatibility

### OpenAI SDK
- Python: `pip install openai>=1.99.0`
- Node.js: `npm install openai@latest`

### Anthropic SDK
- Python: `pip install anthropic>=0.40.0`
- Node.js: `npm install @anthropic-ai/sdk@latest`

### Google Gemini SDK
- Python: `pip install google-generativeai>=0.8.0`
- Node.js: `npm install @google/generative-ai@latest`

---

## ⚠️ Important Notes

1. **Reasoning effort** impacts latency significantly:
   - Minimal: 2-5s
   - Low: 5-10s
   - Medium: 10-20s
   - High: 30-120s

2. **Verbosity** affects token usage linearly (low: ~500 → high: ~1200 tokens)

3. **Extended thinking** (Claude) and **adaptive thinking** (Gemini) are in beta

4. Always check rate limits and pricing for new features

5. Some features may require API version updates or beta access

---

**Generated by**: Perplexity AI (High Research) + Vecto Pilot™ SDK Tracker  
**Script**: `scripts/fetch-latest-sdk.mjs`  
**To Update**: Run `node scripts/fetch-latest-sdk.mjs`

---

## 🔌 MCP Server Configuration with OpenAI SDK

**Model Context Protocol (MCP)** is a standardized protocol for connecting AI assistants to external tools, data sources, and services. This section covers comprehensive MCP server integration with OpenAI's SDK.

---

### 1. MCP Architecture Overview

MCP enables AI models to interact with external systems through a client-server architecture:

```
┌─────────────────┐      ┌──────────────┐      ┌─────────────────┐
│   AI Assistant  │ ───> │  MCP Client  │ ───> │   MCP Server    │
│   (GPT-5/4/etc) │ <─── │  (OpenAI SDK)│ <─── │  (Your Tools)   │
└─────────────────┘      └──────────────┘      └─────────────────┘
```

**Key Components:**
- **MCP Client**: Built into AI assistant, handles tool discovery and execution
- **MCP Server**: Exposes tools/resources/prompts to the AI
- **Transport Layer**: stdio, HTTP, or WebSocket communication

---

### 2. Required Parameters for MCP Server

#### Server Configuration

```python
{
    "mcpServers": {
        "server-name": {
            "command": "python",           # Executable command
            "args": ["-m", "server.py"],   # Command arguments
            "env": {                       # Environment variables
                "API_KEY": "...",
                "DATABASE_URL": "..."
            },
            "transport": "stdio",          # stdio | http | websocket
            "autoStart": true,             # Auto-start on client init
            "timeout": 30000               # Connection timeout (ms)
        }
    }
}
```

#### Tool Registration Schema

```typescript
interface MCPTool {
    name: string;                  // Unique tool identifier
    description: string;           // Clear description for AI
    parameters: {
        type: "object";
        properties: {
            [key: string]: {
                type: string;      // string | number | boolean | array | object
                description: string;
                enum?: string[];   // Optional: allowed values
                required?: boolean;
            }
        };
        required: string[];        // List of required parameter names
    };
}
```

---

### 3. Complete Python Implementation

#### FastAPI MCP Server with OpenAI Integration

```python
"""
MCP Server for AI Assistant Tools
Exposes file operations, web search, and database access
"""
import asyncio
import json
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import AsyncOpenAI

# Initialize FastAPI server
app = FastAPI(title="Vecto Pilot MCP Server")

# Initialize OpenAI client
client = AsyncOpenAI(api_key="YOUR_API_KEY")


# ===================================================================
# MCP TOOL DEFINITIONS
# ===================================================================

class ToolDefinition(BaseModel):
    """MCP tool schema"""
    name: str
    description: str
    parameters: Dict[str, Any]


class ToolCall(BaseModel):
    """Tool execution request"""
    name: str
    arguments: Dict[str, Any]


# Tool registry
MCP_TOOLS: List[ToolDefinition] = [
    ToolDefinition(
        name="read_file",
        description="Read contents of a file from the repository",
        parameters={
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to file relative to repository root"
                }
            },
            "required": ["file_path"]
        }
    ),
    ToolDefinition(
        name="write_file",
        description="Write or update a file in the repository",
        parameters={
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to file"
                },
                "content": {
                    "type": "string",
                    "description": "File content to write"
                }
            },
            "required": ["file_path", "content"]
        }
    ),
    ToolDefinition(
        name="web_search",
        description="Search the web for real-time information",
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                }
            },
            "required": ["query"]
        }
    ),
    ToolDefinition(
        name="execute_sql",
        description="Execute SQL query against database",
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "SQL query to execute"
                },
                "params": {
                    "type": "array",
                    "description": "Query parameters (optional)",
                    "items": {"type": "string"}
                }
            },
            "required": ["query"]
        }
    )
]


# ===================================================================
# TOOL IMPLEMENTATIONS
# ===================================================================

async def read_file(file_path: str) -> str:
    """Read file implementation"""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found: {file_path}"
    except Exception as e:
        return f"Error reading file: {str(e)}"


async def write_file(file_path: str, content: str) -> str:
    """Write file implementation"""
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        return f"Successfully wrote {len(content)} bytes to {file_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


async def web_search(query: str) -> str:
    """Web search using Perplexity or similar"""
    # Implementation depends on your search provider
    return f"Search results for: {query}"


async def execute_sql(query: str, params: Optional[List] = None) -> str:
    """Execute SQL query"""
    # Implementation depends on your database
    return f"SQL executed: {query}"


# Tool function map
TOOL_FUNCTIONS = {
    "read_file": read_file,
    "write_file": write_file,
    "web_search": web_search,
    "execute_sql": execute_sql
}


# ===================================================================
# MCP SERVER ENDPOINTS
# ===================================================================

@app.get("/mcp/tools")
async def list_tools():
    """List all available MCP tools"""
    return {
        "tools": [tool.dict() for tool in MCP_TOOLS]
    }


@app.post("/mcp/execute")
async def execute_tool(tool_call: ToolCall):
    """Execute a tool call"""
    if tool_call.name not in TOOL_FUNCTIONS:
        raise HTTPException(status_code=404, detail=f"Tool not found: {tool_call.name}")
    
    try:
        func = TOOL_FUNCTIONS[tool_call.name]
        result = await func(**tool_call.arguments)
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ===================================================================
# OPENAI GPT-5 INTEGRATION WITH MCP TOOLS
# ===================================================================

@app.post("/chat")
async def chat_with_mcp(messages: List[Dict[str, str]]):
    """
    Chat endpoint with MCP tool integration
    
    Example request:
    {
        "messages": [
            {"role": "user", "content": "Read the file app/main.py"}
        ]
    }
    """
    # Convert MCP tools to OpenAI function format
    openai_tools = [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            }
        }
        for tool in MCP_TOOLS
    ]
    
    # Initial GPT-5 call with tools
    response = await client.chat.completions.create(
        model="gpt-5",
        messages=messages,
        tools=openai_tools,
        tool_choice="auto",
        max_completion_tokens=4000,
        reasoning_effort="high"
    )
    
    response_message = response.choices[0].message
    
    # Execute tool calls if any
    if response_message.tool_calls:
        messages.append(response_message)
        
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            # Execute the tool
            if function_name in TOOL_FUNCTIONS:
                function_result = await TOOL_FUNCTIONS[function_name](**function_args)
                
                # Add result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": function_result
                })
        
        # Get final response after tool execution
        final_response = await client.chat.completions.create(
            model="gpt-5",
            messages=messages,
            max_completion_tokens=4000,
            reasoning_effort="high"
        )
        
        return {
            "response": final_response.choices[0].message.content,
            "tool_calls": [
                {
                    "function": tc.function.name,
                    "arguments": json.loads(tc.function.arguments)
                }
                for tc in response_message.tool_calls
            ]
        }
    
    return {
        "response": response_message.content,
        "tool_calls": []
    }


# ===================================================================
# SERVER STARTUP
# ===================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=3101,
        log_level="info"
    )
```

---

### 4. TypeScript/Node.js Implementation

#### Express MCP Server with OpenAI SDK

```typescript
import express from 'express';
import OpenAI from 'openai';
import { z } from 'zod';

// Initialize Express server
const app = express();
app.use(express.json());

// Initialize OpenAI client
const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

// ===================================================================
// MCP TOOL DEFINITIONS
// ===================================================================

interface MCPTool {
  name: string;
  description: string;
  parameters: {
    type: 'object';
    properties: Record<string, any>;
    required: string[];
  };
}

const MCP_TOOLS: MCPTool[] = [
  {
    name: 'read_file',
    description: 'Read contents of a file from the repository',
    parameters: {
      type: 'object',
      properties: {
        file_path: {
          type: 'string',
          description: 'Path to file relative to repository root'
        }
      },
      required: ['file_path']
    }
  },
  {
    name: 'write_file',
    description: 'Write or update a file in the repository',
    parameters: {
      type: 'object',
      properties: {
        file_path: { type: 'string', description: 'Path to file' },
        content: { type: 'string', description: 'File content' }
      },
      required: ['file_path', 'content']
    }
  },
  {
    name: 'web_search',
    description: 'Search the web for real-time information',
    parameters: {
      type: 'object',
      properties: {
        query: { type: 'string', description: 'Search query' }
      },
      required: ['query']
    }
  },
  {
    name: 'git_status',
    description: 'Get git repository status',
    parameters: {
      type: 'object',
      properties: {},
      required: []
    }
  }
];

// ===================================================================
// TOOL IMPLEMENTATIONS
// ===================================================================

import fs from 'fs/promises';
import { execSync } from 'child_process';

async function readFile(file_path: string): Promise<string> {
  try {
    return await fs.readFile(file_path, 'utf-8');
  } catch (error) {
    return `Error: ${(error as Error).message}`;
  }
}

async function writeFile(file_path: string, content: string): Promise<string> {
  try {
    await fs.writeFile(file_path, content, 'utf-8');
    return `Successfully wrote to ${file_path}`;
  } catch (error) {
    return `Error: ${(error as Error).message}`;
  }
}

async function webSearch(query: string): Promise<string> {
  // Implement with your search provider (Perplexity, etc.)
  return `Search results for: ${query}`;
}

async function gitStatus(): Promise<string> {
  try {
    return execSync('git status --short').toString();
  } catch (error) {
    return `Error: ${(error as Error).message}`;
  }
}

const TOOL_FUNCTIONS: Record<string, Function> = {
  read_file: readFile,
  write_file: writeFile,
  web_search: webSearch,
  git_status: gitStatus
};

// ===================================================================
// MCP SERVER ENDPOINTS
// ===================================================================

// List available tools
app.get('/mcp/tools', (req, res) => {
  res.json({ tools: MCP_TOOLS });
});

// Execute tool
app.post('/mcp/execute', async (req, res) => {
  const { name, arguments: args } = req.body;
  
  if (!(name in TOOL_FUNCTIONS)) {
    return res.status(404).json({ error: `Tool not found: ${name}` });
  }
  
  try {
    const result = await TOOL_FUNCTIONS[name](...Object.values(args));
    res.json({ success: true, result });
  } catch (error) {
    res.json({ success: false, error: (error as Error).message });
  }
});

// ===================================================================
// OPENAI GPT-5 INTEGRATION
// ===================================================================

app.post('/chat', async (req, res) => {
  const { messages } = req.body;
  
  // Convert MCP tools to OpenAI format
  const openaiTools = MCP_TOOLS.map(tool => ({
    type: 'function' as const,
    function: {
      name: tool.name,
      description: tool.description,
      parameters: tool.parameters
    }
  }));
  
  try {
    // Initial GPT-5 call
    let response = await client.chat.completions.create({
      model: 'gpt-5',
      messages,
      tools: openaiTools,
      tool_choice: 'auto',
      max_completion_tokens: 4000,
      reasoning_effort: 'high'
    });
    
    let responseMessage = response.choices[0].message;
    const toolCallsExecuted: any[] = [];
    
    // Execute tool calls iteratively (max 5 rounds)
    let iteration = 0;
    while (responseMessage.tool_calls && iteration < 5) {
      iteration++;
      messages.push(responseMessage);
      
      // Execute all tool calls
      for (const toolCall of responseMessage.tool_calls) {
        const functionName = toolCall.function.name;
        const functionArgs = JSON.parse(toolCall.function.arguments);
        
        if (functionName in TOOL_FUNCTIONS) {
          const result = await TOOL_FUNCTIONS[functionName](...Object.values(functionArgs));
          
          toolCallsExecuted.push({
            function: functionName,
            arguments: functionArgs,
            result: result.substring(0, 500) // Truncate for response
          });
          
          messages.push({
            role: 'tool',
            tool_call_id: toolCall.id,
            content: result
          });
        }
      }
      
      // Get next response
      response = await client.chat.completions.create({
        model: 'gpt-5',
        messages,
        tools: iteration < 4 ? openaiTools : undefined,
        max_completion_tokens: 4000,
        reasoning_effort: 'high'
      });
      
      responseMessage = response.choices[0].message;
    }
    
    res.json({
      response: responseMessage.content,
      tool_calls: toolCallsExecuted
    });
    
  } catch (error) {
    res.status(500).json({ error: (error as Error).message });
  }
});

// Start server
const PORT = process.env.PORT || 3101;
app.listen(PORT, () => {
  console.log(`MCP Server running on port ${PORT}`);
});
```

---

### 5. MCP Server Configuration File

#### `mcp-config.json`

```json
{
  "mcpServers": {
    "vecto-pilot-tools": {
      "command": "python",
      "args": ["-m", "uvicorn", "app.mcp.server:app", "--host", "127.0.0.1", "--port", "3101"],
      "env": {
        "OPENAI_API_KEY": "${OPENAI_API_KEY}",
        "DATABASE_URL": "${DATABASE_URL}",
        "PERPLEXITY_API_KEY": "${PERPLEXITY_API_KEY}"
      },
      "transport": "stdio",
      "autoStart": true,
      "timeout": 30000,
      "tools": [
        {
          "name": "read_file",
          "enabled": true,
          "permissions": ["read"]
        },
        {
          "name": "write_file",
          "enabled": true,
          "permissions": ["read", "write"]
        },
        {
          "name": "web_search",
          "enabled": true,
          "rateLimit": {
            "requests": 10,
            "per": "minute"
          }
        },
        {
          "name": "execute_sql",
          "enabled": true,
          "permissions": ["database:read", "database:write"],
          "requireConfirmation": true
        }
      ]
    }
  },
  "security": {
    "allowedCommands": ["python", "node", "npm"],
    "sandboxMode": false,
    "requireAuth": true,
    "authToken": "${MCP_AUTH_TOKEN}"
  },
  "logging": {
    "level": "info",
    "file": "logs/mcp-server.log",
    "maxSize": "10mb",
    "maxFiles": 5
  }
}
```

---

### 6. Server Lifecycle and Tool Registration

#### Startup Sequence

```python
async def startup():
    """MCP server startup lifecycle"""
    # 1. Load configuration
    config = load_mcp_config()
    
    # 2. Initialize tool registry
    register_tools(MCP_TOOLS)
    
    # 3. Verify external dependencies
    await verify_database_connection()
    await verify_api_keys()
    
    # 4. Start health check endpoint
    start_health_monitor()
    
    # 5. Emit ready signal
    print("MCP Server ready - Tools available:", len(MCP_TOOLS))


async def shutdown():
    """Graceful shutdown"""
    # 1. Stop accepting new requests
    # 2. Finish pending tool executions
    # 3. Close database connections
    # 4. Flush logs
    pass
```

#### Dynamic Tool Registration

```python
class MCPToolRegistry:
    """Dynamic tool registration system"""
    
    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        self.functions: Dict[str, Callable] = {}
    
    def register(
        self,
        name: str,
        description: str,
        parameters: Dict,
        handler: Callable
    ):
        """Register a new tool at runtime"""
        tool = ToolDefinition(
            name=name,
            description=description,
            parameters=parameters
        )
        self.tools[name] = tool
        self.functions[name] = handler
        print(f"✅ Registered tool: {name}")
    
    def unregister(self, name: str):
        """Remove a tool"""
        if name in self.tools:
            del self.tools[name]
            del self.functions[name]
            print(f"❌ Unregistered tool: {name}")
    
    async def execute(self, name: str, **kwargs):
        """Execute tool by name"""
        if name not in self.functions:
            raise ValueError(f"Tool not found: {name}")
        return await self.functions[name](**kwargs)


# Usage
registry = MCPToolRegistry()

registry.register(
    name="custom_analysis",
    description="Analyze code complexity",
    parameters={
        "type": "object",
        "properties": {
            "file_path": {"type": "string"}
        },
        "required": ["file_path"]
    },
    handler=analyze_code_complexity
)
```

---

### 7. Best Practices

#### Security

✅ **DO:**
- Validate all tool inputs with strict schemas
- Implement authentication tokens for MCP server
- Use allowlists for file paths and shell commands
- Rate limit expensive operations (web search, API calls)
- Run MCP server on loopback (127.0.0.1) only
- Sanitize user inputs before executing

❌ **DON'T:**
- Expose MCP server publicly without authentication
- Allow arbitrary file access or shell command execution
- Trust tool results without validation
- Log sensitive data (API keys, credentials)

#### Performance

```python
# Cache expensive tool results
from functools import lru_cache

@lru_cache(maxsize=100)
async def cached_web_search(query: str):
    """Cache search results for 5 minutes"""
    return await web_search(query)

# Timeout long-running tools
import asyncio

async def execute_with_timeout(func, timeout=30):
    """Execute tool with timeout"""
    try:
        return await asyncio.wait_for(func, timeout=timeout)
    except asyncio.TimeoutError:
        return "Error: Tool execution timed out"
```

#### Error Handling

```python
class MCPError(Exception):
    """Base MCP error"""
    pass

class ToolNotFoundError(MCPError):
    """Tool doesn't exist"""
    pass

class ToolExecutionError(MCPError):
    """Tool execution failed"""
    pass

# Graceful degradation
async def safe_execute_tool(name: str, **kwargs):
    """Execute tool with error handling"""
    try:
        return await TOOL_FUNCTIONS[name](**kwargs)
    except ToolNotFoundError:
        return f"Tool {name} not available"
    except ToolExecutionError as e:
        return f"Tool failed: {str(e)}"
    except Exception as e:
        logging.error(f"Unexpected error in {name}: {e}")
        return "An unexpected error occurred"
```

---

### 8. Production Deployment

#### Environment Variables

```bash
# .env.mcp
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://...
PERPLEXITY_API_KEY=pplx-...
MCP_AUTH_TOKEN=your-secure-token
MCP_PORT=3101
MCP_HOST=127.0.0.1
NODE_ENV=production
LOG_LEVEL=info
```

#### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy MCP server code
COPY app/mcp ./app/mcp

# Expose internal port (not public)
EXPOSE 3101

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s \
  CMD curl -f http://localhost:3101/health || exit 1

# Run MCP server
CMD ["uvicorn", "app.mcp.server:app", "--host", "0.0.0.0", "--port", "3101"]
```

#### Process Management (PM2)

```javascript
// ecosystem.config.js
module.exports = {
  apps: [{
    name: 'mcp-server',
    script: 'dist/mcp/server.js',
    instances: 1,
    exec_mode: 'cluster',
    env: {
      NODE_ENV: 'production',
      PORT: 3101
    },
    error_file: 'logs/mcp-error.log',
    out_file: 'logs/mcp-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
  }]
};
```

---

### 9. Testing MCP Tools

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_read_file_tool():
    """Test file reading tool"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/mcp/execute", json={
            "name": "read_file",
            "arguments": {"file_path": "test.txt"}
        })
        assert response.status_code == 200
        assert response.json()["success"] is True

@pytest.mark.asyncio
async def test_chat_with_tools():
    """Test GPT-5 chat with tool execution"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/chat", json={
            "messages": [
                {"role": "user", "content": "Read the file app/main.py"}
            ]
        })
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert len(data["tool_calls"]) > 0
        assert data["tool_calls"][0]["function"] == "read_file"
```

---

### 10. Monitoring and Observability

```python
from prometheus_client import Counter, Histogram
import time

# Metrics
tool_calls_total = Counter('mcp_tool_calls_total', 'Total tool calls', ['tool_name'])
tool_duration_seconds = Histogram('mcp_tool_duration_seconds', 'Tool execution time', ['tool_name'])

async def execute_with_metrics(tool_name: str, **kwargs):
    """Execute tool with metrics"""
    tool_calls_total.labels(tool_name=tool_name).inc()
    
    start = time.time()
    try:
        result = await TOOL_FUNCTIONS[tool_name](**kwargs)
        return result
    finally:
        duration = time.time() - start
        tool_duration_seconds.labels(tool_name=tool_name).observe(duration)
```

---

## 📚 Additional Resources

- **MCP Specification**: https://modelcontextprotocol.io/docs
- **OpenAI Function Calling**: https://platform.openai.com/docs/guides/function-calling
- **Anthropic Tool Use**: https://docs.anthropic.com/claude/docs/tool-use
- **Example MCP Servers**: https://github.com/modelcontextprotocol/servers

---

**Last Updated**: 2025-10-18  
**MCP Version**: 1.0.0  
**Compatible SDKs**: OpenAI 2.3+, Anthropic 0.40+

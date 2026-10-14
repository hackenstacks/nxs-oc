# OpenCharacters Custom API Endpoints - User Manual

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Step-by-Step Configuration](#step-by-step-configuration)
4. [Configuration Examples](#configuration-examples)
5. [Troubleshooting](#troubleshooting)
6. [Advanced Usage](#advanced-usage)
7. [Frequently Asked Questions](#frequently-asked-questions)

## Introduction

OpenCharacters now supports any OpenAI-compatible API endpoint, allowing you to use:
- Local AI models (Ollama, LM Studio, etc.)
- Alternative cloud providers (OpenRouter, Together AI, Anyscale, etc.)
- Self-hosted models
- Custom AI deployments

This manual will guide you through setting up these custom endpoints.

## Getting Started

### What You'll Need
- OpenCharacters application (`play.html` file)
- A web browser
- An OpenAI-compatible API endpoint
- API credentials (if required)

### Supported API Types
- **Chat Completion**: `/v1/chat/completions` (GPT-style models)
- **Text Completion**: `/v1/completions` (older completion models)
- **Text Embedding**: `/v1/embeddings` (for embedding models)

## Step-by-Step Configuration

### Step 1: Open OpenCharacters
1. Open your web browser
2. Navigate to and open the `play.html` file
3. Wait for the application to load completely

### Step 2: Access Settings
1. Look for the **Settings** button in the interface
   - Usually located in the top navigation or hamburger menu
2. Click on **Settings** to open the settings dialog

### Step 3: Show Advanced Settings
1. In the settings dialog, look for text that says **"show advanced settings"**
2. Click on this link to reveal additional configuration options
3. The dialog will expand to show more fields

### Step 4: Find Custom Model Configs
1. Scroll down to find the **"Custom model configs"** field
2. This is a large text area with a monospace font
3. You'll see placeholder text with examples

### Step 5: Enter Your Configuration
1. Click in the text area
2. Each line should contain one complete model configuration
3. Use JSON5 format (see examples below)
4. You can add multiple models, one per line

### Step 6: Save and Test
1. Click **Save** or **OK** to save your settings
2. The dialog will close
3. Your custom models should now appear in model selection dropdowns
4. Create a new conversation and select your custom model to test

## Configuration Examples

### Basic Template
```json5
{
  name: "unique-model-name",
  shortLabel: "Display Name in UI",
  endpointUrl: "https://api.example.com/v1/chat/completions",
  apiKey: "your-api-key-here",
  maxSequenceLength: 4096,
  type: "chat-completion",
  tokenPricing: { prompt: 0.001, completion: 0.002 }
}
```

### Local Ollama Server
```json5
{
  name: "llama2-ollama",
  shortLabel: "Llama 2 (Local Ollama)",
  endpointUrl: "http://localhost:11434/v1/chat/completions",
  apiKey: "ollama",
  maxSequenceLength: 4096,
  type: "chat-completion",
  tokenPricing: { prompt: 0, completion: 0 }
}
```

### OpenRouter
```json5
{
  name: "openrouter-claude",
  shortLabel: "Claude 3 via OpenRouter",
  endpointUrl: "https://openrouter.ai/api/v1/chat/completions",
  apiKey: "sk-or-v1-your-key-here",
  maxSequenceLength: 200000,
  type: "chat-completion",
  tokenPricing: { prompt: 0.008, completion: 0.024 }
}
```

### Together AI
```json5
{
  name: "together-mistral",
  shortLabel: "Mistral 7B via Together",
  endpointUrl: "https://api.together.xyz/v1/chat/completions",
  apiKey: "your-together-key",
  maxSequenceLength: 8192,
  type: "chat-completion",
  tokenPricing: { prompt: 0.0002, completion: 0.0002 }
}
```

### LM Studio (Local)
```json5
{
  name: "lmstudio-local",
  shortLabel: "Local LM Studio Model",
  endpointUrl: "http://localhost:1234/v1/chat/completions",
  apiKey: "lm-studio",
  maxSequenceLength: 4096,
  type: "chat-completion",
  tokenPricing: { prompt: 0, completion: 0 }
}
```

### Custom Embedding Model
```json5
{
  name: "custom-embeddings",
  shortLabel: "Custom Embedding API",
  endpointUrl: "https://api.yourservice.com/v1/embeddings",
  apiKey: "your-embedding-key",
  maxSequenceLength: 512,
  type: "text-embedding",
  tokenPricing: { prompt: 0.0001, completion: 0.0001 }
}
```

### Multiple Models Example
```json5
{ name: "ollama-llama", shortLabel: "Llama 2 Local", endpointUrl: "http://localhost:11434/v1/chat/completions", apiKey: "ollama", maxSequenceLength: 4096, type: "chat-completion", tokenPricing: { prompt: 0, completion: 0 } }
{ name: "openrouter-gpt4", shortLabel: "GPT-4 via OpenRouter", endpointUrl: "https://openrouter.ai/api/v1/chat/completions", apiKey: "sk-or-v1-xxx", maxSequenceLength: 8192, type: "chat-completion", tokenPricing: { prompt: 0.03, completion: 0.06 } }
{ name: "together-codellama", shortLabel: "CodeLlama via Together", endpointUrl: "https://api.together.xyz/v1/chat/completions", apiKey: "together-key", maxSequenceLength: 16384, type: "chat-completion", tokenPricing: { prompt: 0.0002, completion: 0.0002 } }
```

## Field Descriptions

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| `name` | ✅ | Unique identifier (no spaces) | `"gpt4-local"` |
| `shortLabel` | ❌ | Display name in UI | `"GPT-4 Local"` |
| `endpointUrl` | ✅ | Full API endpoint URL | `"https://api.openai.com/v1/chat/completions"` |
| `apiKey` | ❌ | API authentication key | `"sk-xxx"` or `null` |
| `maxSequenceLength` | ✅ | Maximum context length | `4096` |
| `type` | ✅ | API type | `"chat-completion"`, `"completion"`, or `"text-embedding"` |
| `tokenPricing` | ✅ | Cost per 1K tokens | `{ prompt: 0.001, completion: 0.002 }` |
| `modelUrl` | ❌ | Usually `null` for OpenAI-compatible | `null` |

## Troubleshooting

### Model Not Appearing
- **Check JSON5 syntax**: Ensure proper formatting and no syntax errors
- **Refresh page**: Sometimes a page refresh is needed after saving
- **Check name uniqueness**: Each model must have a unique `name` field
- **Verify required fields**: Ensure all required fields are present

### Connection Errors
- **Check endpoint URL**: Verify the URL is correct and accessible
- **Test API separately**: Use curl or Postman to test the endpoint
- **Check CORS**: Local servers may need CORS headers enabled
- **Verify API key**: Ensure the API key is valid and has proper permissions

### Authentication Issues
- **API key format**: Different services use different key formats
- **Check authentication method**: The system auto-detects based on URL
- **Azure endpoints**: Automatically use `api-key` header instead of Bearer token

### Local Server Issues
- **Server running**: Ensure your local AI server is running
- **Port accessibility**: Check that the port is open and accessible
- **CORS enabled**: Most local servers need CORS enabled for web access

### Common Error Messages
- `Model "xyz" not found`: The model name doesn't exist in configurations
- `Error getting text embeddings`: Usually indicates API endpoint or authentication issues
- `JSON5 parse error`: Syntax error in your configuration format

## Advanced Usage

### Environment-Specific Configurations
You can set up different configurations for different environments:

**Development (Local)**
```json5
{ name: "dev-llama", endpointUrl: "http://localhost:11434/v1/chat/completions", apiKey: "ollama" }
```

**Production (Cloud)**
```json5
{ name: "prod-gpt4", endpointUrl: "https://api.openai.com/v1/chat/completions", apiKey: "sk-prod-key" }
```

### Cost Optimization
Set accurate `tokenPricing` to track costs:
- Use `{ prompt: 0, completion: 0 }` for free/local models
- Check provider pricing pages for accurate rates
- Prices are per 1,000 tokens

### Security Best Practices
- **Don't share configurations**: API keys should be kept private
- **Use environment variables**: For production deployments
- **Rotate keys regularly**: Change API keys periodically
- **Limit key permissions**: Use keys with minimal required permissions

## Frequently Asked Questions

### Q: Can I use any AI model?
A: Any model that provides an OpenAI-compatible API endpoint can be used.

### Q: Do I need to pay for API access?
A: It depends on the service. Local models (Ollama, LM Studio) are free, while cloud services typically charge per token.

### Q: Can I use multiple providers simultaneously?
A: Yes! You can configure multiple models from different providers and switch between them.

### Q: What if my API doesn't use Bearer token authentication?
A: The system auto-detects Azure-style authentication. For other methods, you may need an API proxy.

### Q: Can I use this with Hugging Face models?
A: If Hugging Face provides an OpenAI-compatible endpoint, yes. Otherwise, you'll need a compatibility layer.

### Q: How do I remove a custom model?
A: Simply delete the configuration line from the "Custom model configs" field and save.

### Q: Can I use local models without internet?
A: Yes! Local models (Ollama, LM Studio) work completely offline once configured.

### Q: What's the difference between chat-completion and completion?
A: 
- `chat-completion`: Modern format with conversation history (recommended)
- `completion`: Legacy format for simple text completion
- `text-embedding`: For creating vector embeddings of text

### Q: How do I find my API endpoint URL?
A: Check your AI service provider's documentation. Common patterns:
- OpenAI: `https://api.openai.com/v1/chat/completions`
- Ollama: `http://localhost:11434/v1/chat/completions`
- Most services: `https://api.service.com/v1/chat/completions`

## Support and Resources

For additional help:
1. Check the service provider's API documentation
2. Test endpoints with tools like curl or Postman
3. Verify JSON5 syntax with online validators
4. Check browser developer console for error messages

---

*This manual covers the configuration of custom API endpoints in OpenCharacters. The system has been updated to support any OpenAI-compatible API endpoint, making it flexible and provider-agnostic.*
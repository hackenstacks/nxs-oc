# Configuring Custom OpenAI-Compatible Endpoints

OpenCharacters now supports any OpenAI-compatible API endpoint through the custom model configuration system.

## How to Add Custom Endpoints

1. Open the application (play.html)
2. Go to Settings 
3. Click "show advanced settings"
4. Find the "Custom model configs" field
5. Add your custom model configuration in JSON5 format

## Example Configurations

### Local Ollama Server
```json5
{
  name: "llama2-local",
  shortLabel: "Local Llama 2 via Ollama",
  endpointUrl: "http://localhost:11434/v1/chat/completions",
  modelUrl: null,
  apiKey: "ollama",
  maxSequenceLength: 4096,
  type: "chat-completion",
  tokenPricing: { prompt: 0, completion: 0 }
}
```

### Custom OpenAI-Compatible Server
```json5
{
  name: "custom-gpt",
  shortLabel: "Custom GPT Server",
  endpointUrl: "https://your-server.com/v1/chat/completions",
  modelUrl: null,
  apiKey: "your-api-key-here",
  maxSequenceLength: 8192,
  type: "chat-completion",
  tokenPricing: { prompt: 0.002, completion: 0.002 }
}
```

### Text Embedding Model
```json5
{
  name: "custom-embedding",
  shortLabel: "Custom Embedding Model",
  endpointUrl: "https://your-server.com/v1/embeddings",
  modelUrl: null,
  apiKey: "your-api-key-here",
  maxSequenceLength: 512,
  type: "text-embedding",
  tokenPricing: { prompt: 0.0001, completion: 0.0001 }
}
```

### Multiple Configurations
You can add multiple models by putting each configuration on a separate line:

```json5
{ name: "model1", endpointUrl: "https://api1.com/v1/chat/completions", apiKey: "key1", maxSequenceLength: 4096, type: "chat-completion", tokenPricing: { prompt: 0.001, completion: 0.002 } }
{ name: "model2", endpointUrl: "https://api2.com/v1/chat/completions", apiKey: "key2", maxSequenceLength: 8192, type: "chat-completion", tokenPricing: { prompt: 0.003, completion: 0.004 } }
```

## Configuration Fields

- **name**: Unique identifier for the model (required)
- **shortLabel**: Display name shown in the UI (optional)
- **endpointUrl**: Full URL to the API endpoint (required)
- **modelUrl**: Usually null for OpenAI-compatible APIs (optional)
- **apiKey**: API key for authentication (optional)
- **maxSequenceLength**: Maximum context length in tokens (required)
- **type**: Either "chat-completion", "completion", or "text-embedding" (required)
- **tokenPricing**: Cost per 1000 tokens for prompt and completion (required)

## Supported API Types

### Chat Completion
For models that support the `/v1/chat/completions` endpoint (like GPT-3.5/4, Claude via proxy, etc.)

### Text Completion  
For models that support the `/v1/completions` endpoint (legacy OpenAI models)

### Text Embedding
For models that support the `/v1/embeddings` endpoint

## Authentication

The system supports:
- Bearer token authentication (`Authorization: Bearer {apiKey}`)
- Azure-style API key headers (automatically detected for Azure endpoints)
- No authentication (set `apiKey` to null or empty string)

## Notes

- All endpoints must be OpenAI API compatible
- The system will automatically handle different authentication methods based on the endpoint URL
- Pricing is used for cost estimation in the UI
- Models will appear in the model selection dropdown after configuration
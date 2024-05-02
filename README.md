# FastAPI Application with Azure OpenAI

## Overview

This FastAPI application integrates Azure OpenAI to provide text generation based on conversation histories.

## API Usage

### Start the backend Server

Navigate to the backend directory and start the API server with the following commands:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

## Endpoint Documentation

### Generate Text

- **URL**: `/generate-text`
- **Method**: `POST`
- **Description**: Generates text based on the provided conversation history.
- **Request Body**:
  - `system`: A brief description about the system's context.
  - `history`: A list of messages including sender and content.
  - `temperature`: Adjusts the randomness of the response.
  - `max_tokens`: Limits the length of the generated response.
  - `top_p`: Controls nucleus sampling.
  - `frequency_penalty`: Reduces the likelihood of token repetition.
  - `presence_penalty`: Encourages the introduction of new topics.
- **Response**: JSON with generated text and configuration or error message.

### Start the frontend Server

Navigate to the frontend directory and start the server with:

```bash
uvicorn app:app --host 0.0.0.0 --port 8001
```
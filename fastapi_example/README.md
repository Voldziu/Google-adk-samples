Przykładowe wywołanie:



localhost:8080/deploy



Body:


{
  "basic_service_name": "adk-demo-llm-auditor",
  "image": "europe-west3-docker.pkg.dev/acn-daipl/demo/adk-demo-llm_auditor:latest",
  "project_id": "NAZWA",
  "region": "REGION",
  "env_vars": {
    "GOOGLE_GENAI_USE_VERTEXAI": "1",
    "GOOGLE_CLOUD_PROJECT": "NAZWA",
    "GOOGLE_CLOUD_LOCATION": "REGION",
    "MODEL": "gemini-2.5-flash"
  },
  "timeout": 300,
  "memory": "1Gi"
}


/test-run-sse


{
  "agent_url": "https://adk-demo-llm-auditor-1761122677-253000858657.europe-west3.run.app",
  "runsse_body":{
  "appName": "llm_auditor",
  "userId": "user",
  "sessionId": "ace8d67d-59f3-48cc-8995-2f966dbdbdfa",
  "newMessage": {
    "role": "user",
    "parts": [{"text": "Who was in Paris? Accoring to Kanye West"}]
  },
  "streaming": false,
  "stateDelta": null
},
  "timeout": 30
}
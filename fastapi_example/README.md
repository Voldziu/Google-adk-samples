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
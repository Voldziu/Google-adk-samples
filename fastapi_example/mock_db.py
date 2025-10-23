DB = {
    ("email", "agent_name"): "agent_url",
    ("user@example.com", "agent_1"): "https://agent1.example.com",
    (
        "mock_email",
        "llm_auditor",
    ): "https://adk-demo-llm-auditor-1761122677-253000858657.europe-west3.run.app",
    ("local", "llm_auditor"): "http://localhost:8001",
}

DB_ENV_VARS = {  # To be moved to a real database
    "llm-auditor": {
        "GOOGLE_GENAI_USE_VERTEXAI": "1",
        "GOOGLE_CLOUD_PROJECT": "acn-daipl",
        "GOOGLE_CLOUD_LOCATION": "europe-west3",
        "MODEL": "gemini-2.5-flash",
    },
}

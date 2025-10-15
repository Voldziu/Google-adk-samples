# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""website_create_agent: for creating beautiful web site"""

from google.adk import Agent
from google.adk.tools import ToolContext, load_artifacts
from google.genai import types
from pathlib import Path
from dotenv import load_dotenv
import os

from . import prompt

load_dotenv()
MODEL = os.getenv("MODEL", "gemini-2.5-flash")


async def save_website_file(filename: str, content: str, tool_context: "ToolContext"):
    """Saves a website file (HTML, CSS, JS) as an artifact."""

    print(
        f"save_website_file called with filename: {filename}, content length: {len(content)}"
    )

    mime_types = {
        ".html": "text/html",
        ".css": "text/css",
        ".js": "application/javascript",
    }

    ext = Path(filename).suffix
    mime_type = mime_types.get(ext, "text/plain")

    # Convert string to bytes - this might be the issue
    content_bytes = content.encode("utf-8")

    await tool_context.save_artifact(
        filename,
        types.Part.from_bytes(data=content_bytes, mime_type=mime_type),
    )

    return {
        "status": "success",
        "detail": f"{filename} saved successfully",
        "filename": filename,
    }


website_create_agent = Agent(
    model=MODEL,
    name="website_create_agent",
    instruction=prompt.WEBSITE_CREATE_PROMPT,
    output_key="website_create_output",
    tools=[save_website_file, load_artifacts],
)

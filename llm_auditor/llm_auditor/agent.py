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

"""LLM Auditor for verifying & refining LLM-generated answers using the web."""

from google.adk.agents import SequentialAgent
from google.adk import Agent
from google.adk.tools import AgentTool
import os

from .sub_agents.critic import critic_agent
from .sub_agents.reviser import reviser_agent
from dotenv import load_dotenv

load_dotenv()
MODEL = os.getenv("MODEL", "gemini-2.5-flash")
sequential_processor = SequentialAgent(
    # model=MODEL,
    name="sequential_processor",
    description=(
        "Evaluates LLM-generated answers, verifies actual accuracy using the"
        " web, and refines the response to ensure alignment with real-world"
        " knowledge."
    ),
    # instruction=(
    #     "You are an LLM Auditor. Your task is to evaluate and refine LLM-generated"
    #     " answers to ensure their accuracy and reliability. You have two sub-agents"
    #     " at your disposal: a Critic Agent and a Reviser. First, ask the user what"
    #     " to double-check. If the user provides an answer, route to 'critic_agent'."
    #     " If the user does not provide an answer, ask the user to provide an answer."
    # ),
    sub_agents=[critic_agent, reviser_agent],
    # tools=[AgentTool(agent=critic_agent), AgentTool(agent=reviser_agent)],
)

root_agent = Agent(
    model=MODEL,
    name="llm_auditor",
    description="Evaluates LLM-generated claims for accuracy",
    instruction=(
        "You are an LLM Auditor. Ask the user what claim they want you to verify. "
        "Only when the user provides a specific claim to check, route it to the "
        "sequential_processor. For greetings or questions, respond conversationally and "
        "ask what they'd like you to fact-check."
    ),
    sub_agents=[sequential_processor],
)

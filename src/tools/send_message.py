from typing import Optional, Type, Dict
from langchain_core.callbacks import CallbackManagerForToolRun
from langsmith import traceable
from pydantic import BaseModel
from langchain.tools import BaseTool
from src.agents.base import Agent


class SendMessage(BaseTool):
    name: str = "SendMessage"
    description: str = "Use this to send a message to one of your sub-agents"
    args_schema: Type[BaseModel]
    agent_mapping: Dict[str, "Agent"] = None 

    def send_message(self, recipient: str, message: str) -> str:
        agent = self.agent_mapping.get(recipient)
        if agent:
            response = agent.invoke({"messages": [("human", message)]})
            return response["messages"][-1].content
        else:
            return f"Invalid recipient: {recipient}"

    @traceable(run_type="tool", name="SendMessage")
    def _run(
        self,
        recipient: str,
        message: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        return self.send_message(recipient, message)
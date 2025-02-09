from pydantic import Field, create_model
from .agent import Agent
from src.tools.send_message import SendMessage

class AgentsOrchestrator:
    def __init__(self, main_agent: Agent, agents: list[Agent]):
        self.main_agent = main_agent
        self.agents = agents
        self.agent_mapping = {}

        # Set up the communication framework
        self._populate_agent_mapping()
        self._add_send_message_tool()
        
    def invoke(self, message, **kwargs):
        messages = {"messages": [("human", message)]}
        response = self.main_agent.invoke(messages, **kwargs)
        return response["messages"][-1].content

    def stream(self, message, **kwargs):
        messages = {"messages": [("human", message)]}
        for chunk in self.main_agent.stream(messages, **kwargs):
            yield chunk

    def _populate_agent_mapping(self):
        """
        Populates the agent mapping with agent names as keys and agent objects as values.
        """
        for agent in self.agents:
            self.agent_mapping[agent.name] = agent

    def _create_dynamic_send_message_tool(self, agent: "Agent") -> "SendMessage":
        """
        Creates a dynamic send message tool for agents with sub-agents.
        """
        # Generate a description for the recipients
        recipients_description = "\n".join(
            f"{sub_agent.name}: {sub_agent.description}"
            for sub_agent in agent.sub_agents
            if sub_agent.description
        )

        # Create a dynamic input schema
        DynamicSendMessageInput = create_model(
            f"{agent.name}SendMessageInput",
            recipient=(str, Field(..., description=recipients_description)),
            message=(str, Field(..., description="Message to send to sub-agent.")),
        )

        # Create the SendMessage tool instance
        send_message_tool = SendMessage(args_schema=DynamicSendMessageInput)
        send_message_tool.agent_mapping = self.agent_mapping  # Dynamically bind agent_mapping
        return send_message_tool

    def _add_send_message_tool(self):
        """
        Adds the send message tool to agents with sub-agents.
        """
        for agent in self.agents:
            if hasattr(agent, "sub_agents") and agent.sub_agents:
                send_message_tool = self._create_dynamic_send_message_tool(agent)
                agent.tools.append(send_message_tool)

                # Bind the new tool to the agent's LLM model
                agent.initiat_agent()

    def get_agent(self, name: str) -> "Agent":
        """
        Retrieves an agent from the mapping by name.
        """
        return self.agent_mapping.get(name)

from langgraph.checkpoint.sqlite import SqliteSaver
from src.agents.base import Agent, AgentsOrchestrator
from src.prompts import (
    EMAIL_AGENT_PROMPT,
    CALENDAR_AGENT_PROMPT,
    NOTION_AGENT_PROMPT,
    SLACK_AGENT_PROMPT,
    RESEARCHER_AGENT_PROMPT,
    RAG_AGENT_PROMPT
)
from src.tools.calendar import *
from src.tools.email import *
from src.tools.notion import *
from src.tools.slack import *
from src.tools.research import *
from src.tools.rag.query_knowledge import query_knowledge
from src.utils import get_current_date_time
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

class PersonalAssistant:
    def __init__(self, db_connection):
        # Create sqlite checkpointer for managing manager memory
        self.checkpointer = SqliteSaver(db_connection)
        
        # Initialize individual agents (after other agents but before manager)
        self.rag_agent = Agent(
            name="rag_agent",
            description="RAG agent can answer questions using the knowledge base",
            model="openai/gpt-4o-mini",
            system_prompt=RAG_AGENT_PROMPT.format(date_time=get_current_date_time()),
            tools=[query_knowledge],
            sub_agents=[],
            temperature=0.1
        )

        # Initialize individual agents
        self.email_agent = Agent(
            name="email_agent",
            description="Email agent can manage GMAIL inbox including read and send emails",
            model="openai/gpt-4o-mini",
            system_prompt=EMAIL_AGENT_PROMPT.format(date_time=get_current_date_time()),
            tools=[read_emails, send_email, find_contact_email],
            sub_agents=[],
            temperature=0.1
        )

        self.calendar_agent = Agent(
            name="calendar_agent",
            description="Calendar agent can manage Google Calendar including get events and create events",
            model="openai/gpt-4o-mini",
            system_prompt=CALENDAR_AGENT_PROMPT.format(date_time=get_current_date_time()),
            tools=[get_calendar_events, add_event_to_calendar, find_contact_email],
            sub_agents=[],
            temperature=0.1
        )

        self.notion_agent = Agent(
            name="notion_agent",
            description="Notion agent can manage Notion including get my todo list and add task in todo list",
            model="openai/gpt-4o-mini",
            system_prompt=NOTION_AGENT_PROMPT.format(date_time=get_current_date_time()),
            tools=[get_my_todo_list, add_task_in_todo_list],
            sub_agents=[],
            temperature=0.1
        )

        self.slack_agent = Agent(
            name="slack_agent",
            description="Slack agent can read and send messages through Slack",
            model="openai/gpt-4o-mini",
            system_prompt=SLACK_AGENT_PROMPT.format(date_time=get_current_date_time()),
            tools=[get_slack_messages, send_slack_message],
            sub_agents=[],
            temperature=0.1
        )

        self.researcher_agent = Agent(
            name="researcher_agent",
            description="Researcher agent can search the web, scrape websites or LinkedIn profiles",
            model="openai/gpt-4o-mini",
            system_prompt=RESEARCHER_AGENT_PROMPT.format(date_time=get_current_date_time()),
            tools=[search_web, scrape_website_to_markdown, search_linkedin_tool],
            sub_agents=[],
            temperature=0.1
        )

        # Update manager agent with more comprehensive prompt
        self.manager_agent = Agent(
            name="manager_agent",
            description="Manager agent that delegates tasks and coordinates all services",
            model="openai/gpt-4o",
            system_prompt="""You are an intelligent AI assistant manager that coordinates multiple specialized agents.

For ALL interactions, especially first messages or greetings, ALWAYS introduce your full range of capabilities:

"Hello! 👋 I'm your AI assistant with multiple capabilities:

1. 📧 Email Management
   - Read and send emails
   - Check important messages

2. 📅 Calendar Organization
   - Schedule events
   - Check appointments

3. ✅ Notion Task Management
   - Manage to-do lists
   - Track tasks

4. 💬 Slack Communication
   - Read channel messages
   - Send messages

5. 🔍 Research Assistant
   - Web searches
   - LinkedIn research
   - Company information

6. 📚 Knowledge Base Search
   - Search your documents
   - Answer questions from files
   - Find info in reports/images

How can I assist you today?"

Remember to:
- ALWAYS start with this comprehensive introduction for new conversations
- Be proactive in mentioning all available services
- Maintain a helpful and friendly tone
- Delegate tasks to appropriate specialized agents

Current date/time: {date_time}""",
            tools=[],
            sub_agents=[
                self.email_agent,
                self.calendar_agent,
                self.notion_agent,
                self.slack_agent,
                self.researcher_agent,
                self.rag_agent
            ],
            temperature=0.1,
            memory=self.checkpointer
        )

        # Initialize the orchestrator with all agents
        self.assistant_orchestrator = AgentsOrchestrator(
            main_agent=self.manager_agent,
            agents=[
                self.manager_agent,
                self.email_agent,
                self.calendar_agent,
                self.notion_agent,
                self.slack_agent,
                self.researcher_agent,
                self.rag_agent
            ]
        )

        self.conn = db_connection
        self.tools = [
            get_calendar_events,
            read_emails,
            query_knowledge
        ]
        
        # Update prompt to include required agent_scratchpad
        template = """You are a helpful AI assistant that can:
        1. Check calendar events
        2. Read emails
        3. Answer questions using the knowledge base
        
        When asked about documents or information, use the QueryKnowledge tool to search the knowledge base.
        
        Human: {input}
        Assistant: Let me help you with that.
        
        {agent_scratchpad}
        """
        
        prompt = ChatPromptTemplate.from_template(template)
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        self.agent = create_openai_tools_agent(llm, self.tools, prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools)

    def __getattr__(self, name):
        return getattr(self.assistant_orchestrator, name)

    def invoke(self, message, config=None):
        # Check if it's a greeting or first message
        greeting_keywords = ["hi", "hello", "hey", "greetings"]
        is_greeting = any(keyword in message.lower() for keyword in greeting_keywords)
        
        if is_greeting:
            # Force comprehensive introduction
            message = "INTRODUCE_ALL_CAPABILITIES"
            
        response = self.agent_executor.invoke({"input": message})
        return response["output"]

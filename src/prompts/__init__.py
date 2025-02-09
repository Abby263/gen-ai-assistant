from .manager_agent import ASSISTANT_MANAGER_PROMPT
from .email_agent import EMAIL_AGENT_PROMPT
from .notion_agent import NOTION_AGENT_PROMPT
from .calendar_agent import CALENDAR_AGENT_PROMPT
from .slack_agent import SLACK_AGENT_PROMPT
from .researcher_agent import RESEARCHER_AGENT_PROMPT
from .rag_agent import RAG_AGENT_PROMPT

__all__ = [
    'ASSISTANT_MANAGER_PROMPT',
    'CALENDAR_AGENT_PROMPT', 
    'EMAIL_AGENT_PROMPT', 
    'NOTION_AGENT_PROMPT', 
    'RESEARCHER_AGENT_PROMPT',
    'SLACK_AGENT_PROMPT',
    'RAG_AGENT_PROMPT' 
]

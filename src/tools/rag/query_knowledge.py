from typing import Optional
from langsmith import traceable
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from pathlib import Path
from src.processors.data_processor import DataProcessor

class QueryKnowledgeInput(BaseModel):
    query: str = Field(description="The question to ask about the knowledge base")
    context: Optional[str] = Field(description="Additional context or constraints for the query")

@tool("QueryKnowledge", args_schema=QueryKnowledgeInput)
@traceable(run_type="tool", name="QueryKnowledge")
def query_knowledge(query: str, context: Optional[str] = None):
    """Use this to query the knowledge base for answers"""
    try:
        # Initialize data processor
        processor = DataProcessor()
        
        # Process data directory
        data_dir = Path(__file__).parent.parent.parent.parent / 'data'
        vectorstore = processor.process_directory(str(data_dir))
        
        # Search for relevant documents
        docs = vectorstore.similarity_search(query, k=3)
        
        # Format response
        response = "Here's what I found:\n\n"
        for i, doc in enumerate(docs, 1):
            response += f"Source {i}:\n{doc.page_content}\n\n"
        
        return response
        
    except Exception as e:
        return f"Error querying knowledge base: {e}" 
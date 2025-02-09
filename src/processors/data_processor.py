from typing import List, Dict
from pathlib import Path
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    CSVLoader,
    UnstructuredImageLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

class DataProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.embeddings = OpenAIEmbeddings()
        self.supported_formats = {
            '.pdf': PyPDFLoader,
            '.docx': Docx2txtLoader,
            '.txt': TextLoader,
            '.csv': CSVLoader,
            '.jpg': UnstructuredImageLoader,
            '.png': UnstructuredImageLoader,
            '.jpeg': UnstructuredImageLoader
        }
        
    def process_file(self, file_path: Path) -> List[Dict]:
        """Process a single file and return chunks"""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        file_extension = file_path.suffix.lower()
        if file_extension not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_extension}")
            
        loader = self.supported_formats[file_extension](str(file_path))
        documents = loader.load()
        chunks = self.text_splitter.split_documents(documents)
        return chunks
        
    def process_directory(self, dir_path: str) -> Chroma:
        """Process all supported files in a directory and create a vector store"""
        dir_path = Path(dir_path)
        if not dir_path.exists():
            raise NotADirectoryError(f"Directory not found: {dir_path}")
            
        all_chunks = []
        for file_path in dir_path.rglob('*'):
            if file_path.suffix.lower() in self.supported_formats:
                try:
                    chunks = self.process_file(file_path)
                    all_chunks.extend(chunks)
                    print(f"Processed: {file_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
        
        if not all_chunks:
            raise ValueError("No supported files found in directory")
            
        vectorstore = Chroma.from_documents(
            documents=all_chunks,
            embedding=self.embeddings,
            persist_directory=str(dir_path / '.vectorstore')
        )
        return vectorstore 
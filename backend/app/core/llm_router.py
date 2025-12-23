import os
import logging
from typing import Optional, Any
from langchain_core.language_models import BaseChatModel
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

logger = logging.getLogger(__name__)

class LLMRouter:
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.huggingface_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

    def get_llm(self, temp: float = 0.0) -> BaseChatModel:
        """
        Returns the best available LLM client based on priority and availability.
        Priority: Groq -> OpenRouter -> Hugging Face -> OpenAI
        """
        
        # 1. Groq (Fastest)
        if self.groq_api_key:
            try:
                logger.info("Using Groq (llama-3.3-70b-versatile)")
                return ChatGroq(
                    temperature=temp,
                    model_name="llama-3.3-70b-versatile",
                    api_key=self.groq_api_key
                )
            except Exception as e:
                logger.warning(f"Groq failed initialization: {e}")

        # 2. OpenRouter (Flexible)
        if self.openrouter_api_key:
            try:
                logger.info("Using OpenRouter (anthropic/claude-3-haiku)")
                return ChatOpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=self.openrouter_api_key,
                    model="anthropic/claude-3-haiku",
                    temperature=temp
                )
            except Exception as e:
                logger.warning(f"OpenRouter failed initialization: {e}")

        # 3. Hugging Face (Open Source fallback)
        if self.huggingface_token:
            try:
                logger.info("Using Hugging Face (mistralai/Mistral-7B-Instruct-v0.2)")
                llm = HuggingFaceEndpoint(
                    repo_id="mistralai/Mistral-7B-Instruct-v0.2",
                    task="text-generation",
                    max_new_tokens=512,
                    do_sample=False,
                    repetition_penalty=1.03,
                    huggingfacehub_api_token=self.huggingface_token
                )
                return ChatHuggingFace(llm=llm)
            except Exception as e:
                logger.warning(f"Hugging Face failed initialization: {e}")

        # 4. OpenAI (Ultimate fallback)
        if self.openai_api_key:
            try:
                logger.info("Using OpenAI (gpt-3.5-turbo)")
                return ChatOpenAI(
                    model="gpt-3.5-turbo",
                    temperature=temp
                )
            except Exception as e:
                logger.warning(f"OpenAI failed initialization: {e}")

        raise ValueError("No viable LLM provider found. Please check environment variables.")

llm_router = LLMRouter()

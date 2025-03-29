# Standard library imports
import json
import os

# Third-party imports
import openai
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI

# Local imports
from backend.prompts import (
    BROAD_PLAN_DRAFT_TEMPLATE,
    CRITIQUE_TEMPLATE,
    REVISE_SELECTED_TEMPLATE,
    PRECISE_REVISION_TEMPLATE,
    QUIZ_GENERATION_TEMPLATE,
    CODE_PRACTICE_GENERATION_TEMPLATE,
    SLIDES_GENERATION_TEMPLATE
)

# Define public API
__all__ = [
    'get_llm',
    'get_openrouter_llm',
    'create_broad_plan_draft_chain',
    'create_revise_selected_plan_chain',
    'create_precise_revision_chain',
    'create_artifact_chain'
]

def get_llm(model_name="gpt-4o", temperature=0.5):
    """Return a ChatOpenAI LLM."""
    return ChatOpenAI(model_name=model_name, temperature=temperature)

def get_openrouter_llm(model_name="openai/gpt-4o", temperature=0):
    """
    Return a ChatOpenAI LLM for OpenRouter.
    """
    return ChatOpenAI(
        openai_api_base="https://openrouter.ai/api/v1",  
        openai_api_key=os.getenv("OPEN_ROUTER_API_KEY"),  
        model_name=model_name,
        # model_name='deepseek/deepseek-r1:free',
        temperature=temperature
    )

def create_broad_plan_draft_chain(llm):
    """
    Create a single chain for drafting a broad plan.
    No critique/revise is needed here.
    """
    return LLMChain(
        llm=llm,
        prompt=BROAD_PLAN_DRAFT_TEMPLATE,
        output_key="broad_plan_draft"
    )

def create_revise_selected_plan_chain(llm):
    """
    Create a chain for revising a broad plan based on user-selected critique points.
    
    Args:
        llm: Language model for revision
        
    Returns:
        LLMChain: The revise chain that can be used to improve plans based on selected critique points
    """
    # Create revision chain for selected critique points
    revise_selected_chain = LLMChain(
        llm=llm,
        prompt=REVISE_SELECTED_TEMPLATE,
        output_key="revised_plan"
    )
    
    return revise_selected_chain

def create_precise_revision_chain(llm):
    """
    Create a chain for making precise, targeted revisions to a lesson plan.
    This chain ensures that only the specific changes requested by the user are applied,
    preserving all other content exactly as it was.
    
    Args:
        llm: Language model for revision
        
    Returns:
        LLMChain: The chain for precise revision
    """
    return LLMChain(
        llm=llm,
        prompt=PRECISE_REVISION_TEMPLATE,
        output_key="precisely_revised_plan"
    )

def create_artifact_chain(llm, artifact_type: str):
    """Create a chain for generating specific type of artifact
    
    Args:
        llm: The language model to use
        artifact_type: Type of artifact to generate ('quiz', 'code_practice', or 'slides')
        
    Returns:
        LLMChain for the specified artifact type
    """
    if artifact_type == "quiz":
        return LLMChain(
            llm=llm,
            prompt=QUIZ_GENERATION_TEMPLATE,
            output_key="quiz"
        )
    elif artifact_type == "code_practice":
        return LLMChain(
            llm=llm,
            prompt=CODE_PRACTICE_GENERATION_TEMPLATE,
            output_key="code_practice"
        )
    elif artifact_type == "slides":
        return LLMChain(
            llm=llm,
            prompt=SLIDES_GENERATION_TEMPLATE,
            output_key="slides"
        )
    else:
        raise ValueError(f"Unsupported artifact type: {artifact_type}")
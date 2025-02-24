# Third-party imports
import os
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
import json

# Local application imports
from .prompts import (
    BROAD_PLAN_DRAFT_TEMPLATE,
    FULL_PLAN_DRAFT_TEMPLATE,
    FULL_PLAN_CRITIQUE_TEMPLATE,
    FULL_PLAN_REVISE_TEMPLATE,
    QUIZ_GENERATION_TEMPLATE,
    CODE_PRACTICE_GENERATION_TEMPLATE
)

# Define public API
__all__ = [
    'get_llm',
    'get_openrouter_llm',
    'create_broad_plan_draft_chain',
    'create_full_plan_chains',
    'create_artifact_chain'
]

def get_llm(model_name="gpt-4o", temperature=0.7):
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

def create_full_plan_chains(llm_draft, llm_critique, llm_revise):
    """
    Create chains for: 
      - Drafting the full plan,
      - Critiquing the full plan,
      - Revising the full plan.
    """
    draft_chain = LLMChain(
        llm=llm_draft,
        prompt=FULL_PLAN_DRAFT_TEMPLATE,
        output_key="full_plan_draft"
    )
    critique_chain = LLMChain(
        llm=llm_critique,
        prompt=FULL_PLAN_CRITIQUE_TEMPLATE,
        output_key="critique"
    )
    revise_chain = LLMChain(
        llm=llm_revise,
        prompt=FULL_PLAN_REVISE_TEMPLATE,
        output_key="revised_plan"
    )
    return draft_chain, critique_chain, revise_chain

def create_artifact_chain(llm, artifact_type: str):
    """Create a chain for generating specific type of artifact
    
    Args:
        llm: The language model to use
        artifact_type: Type of artifact to generate ('quiz' or 'code_practice')
        
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
    else:
        raise ValueError(f"Unsupported artifact type: {artifact_type}")
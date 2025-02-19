import os
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from .prompts import (
    BROAD_PLAN_DRAFT_TEMPLATE,
    FULL_PLAN_DRAFT_TEMPLATE,
    FULL_PLAN_CRITIQUE_TEMPLATE,
    FULL_PLAN_REVISE_TEMPLATE
)

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
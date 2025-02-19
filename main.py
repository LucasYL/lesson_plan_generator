import os
import json
from dotenv import load_dotenv
from chains import (
    get_llm,
    get_openrouter_llm,
    create_broad_plan_draft_chain,
    create_full_plan_chains
)
from prompts import default_example


def strip_markdown(text):
    """
    Remove markdown code fences if present.
    """
    if text.startswith("```") and text.endswith("```"):
        return "\n".join(text.splitlines()[1:-1])
    return text

def parse_nested_json(value):
    """
    Recursively parse any string that looks like JSON into a Python object.
    Also replace escaped newline characters with real newlines.
    """
    if isinstance(value, str):
        # Remove markdown if present
        value = strip_markdown(value)
        stripped = value.strip()
        # Check if the string is a JSON object or array
        if (stripped.startswith("{") and stripped.endswith("}")) or \
           (stripped.startswith("[") and stripped.endswith("]")):
            try:
                parsed = json.loads(stripped)
                # Recursively process the parsed object in case it contains nested JSON strings
                return parse_nested_json(parsed)
            except json.JSONDecodeError:
                # If JSON decoding fails, simply replace escaped newlines
                return value.replace("\\n", "\n")
        else:
            return value.replace("\\n", "\n")
    elif isinstance(value, dict):
        return {k: parse_nested_json(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [parse_nested_json(item) for item in value]
    else:
        return value

def pretty_print_full(result):
    """
    Recursively parse the result (if it contains nested JSON strings) and print it in a pretty format.
    """
    parsed_result = parse_nested_json(result)
    print(json.dumps(parsed_result, indent=2, ensure_ascii=False))


# ---------------------
# Main execution logic
# ---------------------
def main():
    # Load environment variables (e.g., OPENAI_API_KEY)
    load_dotenv()
    
    # Initialize the LLM (using GPT-4 as an example)
    llm = get_llm(model_name="gpt-4o-mini", temperature=0.7)
    llm_openrouter1 = get_openrouter_llm(model_name="anthropic/claude-3.5-sonnet", temperature=0)
    llm_openrouter2 = get_openrouter_llm(model_name="deepseek/deepseek-r1:free", temperature=0)

    
    # Create chain objects for broad and full plan generation
    broad_plan_draft_chain = create_broad_plan_draft_chain(llm)
    full_draft_chain, full_critique_chain, full_revise_chain = create_full_plan_chains(llm, llm, llm)
    # # -----------------------------------------
    # # Example 1: Climate Change and Renewable Energy
    # # -----------------------------------------
    # print("\n=== Example 1: Climate Change and Renewable Energy ===\n")
    
    # # Define input parameters
    # grade_level_1 = "Undergraduate"
    # topic_1 = "Climate Change and Renewable Energy"
    # duration_1 = "40 minutes"  
    # style_1 = "Interactive and Discussion-based"
    # learning_objectives_1 = [
    #     "Understand the causes and effects of climate change",
    #     "Explore renewable energy sources and their benefits",
    #     "Analyze the impact of human activities on the environment",
    #     "Discuss sustainable energy solutions"
    # ]
    # example_broad_1 = "" 
    # external_feedback_broad_1 = "Focus on real-world data and case studies."
    
    # broad_result_1 = broad_plan_draft_chain.invoke({
    #     "grade_level": grade_level_1,
    #     "topic": topic_1,
    #     "duration": duration_1,
    #     "style": style_1,
    #     "learning_objectives": json.dumps(learning_objectives_1, ensure_ascii=False),
    #     "example": example_broad_1,
    #     "external_feedback": external_feedback_broad_1
    # })
    # print("[Draft Broad Plan - Example 1]")
    # pretty_print_full(broad_result_1)
    
    # # Assume the teacher approves the broad plan as-is
    # user_edited_broad_plan_1 = broad_result_1
    
    # # Generate the full lesson plan draft based on the approved broad plan
    # user_feedback_for_full_1 = "Include more recent statistics and detailed case studies on renewable energy."
    # full_draft_result_1 = full_draft_chain.invoke({
    #     "broad_plan_json": user_edited_broad_plan_1,
    #     "external_feedback": user_feedback_for_full_1
    # })
    # print("\n[Draft Full Plan - Example 1]")
    # pretty_print_full(full_draft_result_1)
    
    # # Get critique for the full plan
    # critique_result_1 = full_critique_chain.invoke({"full_plan_json": full_draft_result_1})
    # print("\n[Full Plan Critique - Example 1]")
    # print(critique_result_1)
    
    # # Revise the full plan based on the critique
    # revised_full_result_1 = full_revise_chain.invoke({
    #     "full_plan_json": full_draft_result_1,
    #     "critique_text": critique_result_1
    # })
    # print("\n[Revised Full Plan - Example 1]")
    # pretty_print_full(revised_full_result_1)


    print("\n=== Example 2: Using C Language to Implement Merge Sort and Quick Sort ===\n")
    
    # Define input parameters for Example 2
    grade_level_2 = "Graduate"
    topic_2 = "Using C Language to Implement Merge Sort and Quick Sort"
    duration_2 = "110 minutes"
    style_2 = "Interactive and Hands-on"
    
    learning_objectives_2 = [
        "Understand the fundamentals of merge sort and quick sort algorithms",
        "Learn to implement merge sort and quick sort in C language",
        "Analyze the time and space complexity of both algorithms",
        "Apply sorting algorithms to solve practical programming problems"
    ]
    
    # Define lesson structure requirements (must-have elements)
    requirements_2 = [
        "Hands-on coding exercises",
        "Live coding demonstrations",
        "Need group activity",
        "No quizzes"
    ]
    
    # Broad plan feedback is empty
    broad_plan_feedback_2 = ""

    # Generate the broad lesson plan draft for Example 2
    broad_result_2 = broad_plan_draft_chain.invoke({
        "grade_level": grade_level_2,
        "topic": topic_2,
        "duration": duration_2,
        "style": style_2,
        "learning_objectives": json.dumps(learning_objectives_2, ensure_ascii=False),
        "requirements": json.dumps(requirements_2, ensure_ascii=False),
        "broad_plan_feedback": broad_plan_feedback_2
    })

    print("\n[Draft Broad Plan - Example 2]")
    pretty_print_full(broad_result_2)

    
    # Example content: Use default_example if empty
    example_full_2 = ""
    if example_full_2.strip() == "":
        example_full_2 = default_example

    # Generate the full lesson plan draft for Example 2
    full_draft_result_2 = full_draft_chain.invoke({
        "broad_plan_json": json.dumps(broad_result_2, ensure_ascii=False),
        "example": example_full_2
    })

    print("\n[Draft Full Plan - Example 2]")
    pretty_print_full(full_draft_result_2)
    
    # Get critique for the full plan (Example 2)
    critique_result_2 = full_critique_chain.invoke({
        "full_plan_json": full_draft_result_2
    })

    print("\n[Full Plan Critique - Example 2]")
    print(critique_result_2)
    
    # Revise the full plan based on the critique (Example 2)
    revised_full_result_2 = full_revise_chain.invoke({
        "full_plan_json": full_draft_result_2,
        "critique_text": critique_result_2
    })

    print("\n[Revised Full Plan - Example 2]")
    pretty_print_full(revised_full_result_2)

if __name__ == "__main__":
    main()
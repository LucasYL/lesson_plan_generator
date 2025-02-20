import streamlit as st
import sys
import os
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from backend.chains import (
    get_llm,
    get_openrouter_llm,
    create_broad_plan_draft_chain,
    create_full_plan_chains
)

# UI text constants
UI_TEXT = {
    "title": "AI Lesson Plan Generator",
    "grade_level": "Education Level",
    "duration": "Duration (minutes)",
    "topic": "Topic",
    "teaching_style": "Teaching Style",
    "learning_objectives": "Learning Objectives (one per line)",
    "requirements": "Requirements (one per line)",
    "generate_button": "Generate Plan",
    "error_missing_fields": "Please fill in the topic and learning objectives",
    "generating_message": "Generating lesson plan, please wait...",
    "error_prefix": "Error occurred: ",
    "plan_title": "Lesson Plan",
    "objectives_title": "Learning Objectives",
    "phases_title": "Teaching Phases",
    "purpose_label": "Purpose: ",
    "method_label": "Method: ",
    "requirements_label": "Requirements: "
}

GRADE_LEVELS = [
    "Elementary School",
    "Middle School",
    "High School",
    "Undergraduate",
    "Graduate"
]

TEACHING_STYLES = [
    "Lecture-based",
    "Interactive",
    "Practice-oriented",
    "Blended"
]

def init_session_state():
    """Initialize session state variables"""
    if 'current_step' not in st.session_state:
        st.session_state.current_step = "input"
    if 'broad_plan' not in st.session_state:
        st.session_state.broad_plan = None
    if 'full_plan' not in st.session_state:
        st.session_state.full_plan = None
    if 'critique' not in st.session_state:
        st.session_state.critique = None
    if 'final_plan' not in st.session_state:
        st.session_state.final_plan = None
    if 'show_buttons' not in st.session_state:
        st.session_state.show_buttons = False
    # Store form inputs
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {
            "grade_level": None,
            "topic": None,
            "duration": None,
            "style": None,
            "objectives": None,
            "requirements": None,
            "example": None
        }

def render_input_form():
    """Render the lesson plan input form"""
    st.header(UI_TEXT["title"])
    
    # Store LLM instance in session state
    if 'llm' not in st.session_state:
        st.session_state.llm = get_llm(model_name="gpt-4o-mini", temperature=0)
    if 'broad_chain' not in st.session_state:
        st.session_state.broad_chain = create_broad_plan_draft_chain(st.session_state.llm)
    
    # 创建左右两列布局
    left_col, right_col = st.columns([2, 1])
    
    with left_col:
        with st.form("lesson_plan_input"):
            col1, col2 = st.columns(2)
            
            with col1:
                grade_level = st.selectbox(
                    UI_TEXT["grade_level"],
                    GRADE_LEVELS,
                    index=GRADE_LEVELS.index(st.session_state.form_data["grade_level"]) if st.session_state.form_data["grade_level"] else 0
                )
                duration = st.text_input(UI_TEXT["duration"], 
                    value=st.session_state.form_data["duration"] if st.session_state.form_data["duration"] else "40"
                )
                
            with col2:
                topic = st.text_input(UI_TEXT["topic"],
                    value=st.session_state.form_data["topic"] if st.session_state.form_data["topic"] else ""
                )
                style = st.selectbox(
                    UI_TEXT["teaching_style"],
                    TEACHING_STYLES,
                    index=TEACHING_STYLES.index(st.session_state.form_data["style"]) if st.session_state.form_data["style"] else 0
                )
            
            # 添加example输入区域，使用expander使界面更整洁    
            with st.expander("Reference Example (Optional)", expanded=False):
                example = st.text_area(
                    "Provide a reference lesson plan example",
                    height=150,
                    value=st.session_state.form_data["example"] if st.session_state.form_data["example"] else "",
                    placeholder="You can provide a reference lesson plan example here. If left empty, default examples will be used."
                )
                
            learning_objectives = st.text_area(
                UI_TEXT["learning_objectives"],
                height=100,
                value="\n".join(st.session_state.form_data["objectives"]) if st.session_state.form_data["objectives"] else "",
                placeholder="Example:\n1. Understand core concepts\n2. Master key skills\n3. Apply independently"
            )
            
            requirements = st.text_area(
                UI_TEXT["requirements"],
                height=100,
                value="\n".join(st.session_state.form_data["requirements"]) if st.session_state.form_data["requirements"] else "",
                placeholder="Example:\n1. Group discussion required\n2. Include practical exercises\n3. Include assessment"
            )
            
            submitted = st.form_submit_button(UI_TEXT["generate_button"])
    
    # Display broad plan and buttons if available
    if st.session_state.broad_plan:
        with left_col:
            display_broad_plan(st.session_state.broad_plan)
            
            # 创建反馈区域的布局
            st.write("### Feedback")
            feedback = st.text_area(
                "Provide feedback to improve the plan",
                placeholder="Enter your suggestions for improvement...",
                key="broad_plan_feedback",
                label_visibility="collapsed"
            )
            
            # 创建按钮区域
            if feedback.strip():
                if st.button("Revise Broad Plan", type="primary"):
                    with st.spinner("Revising plan..."):
                        revised_broad_result = st.session_state.broad_chain.invoke({
                            "grade_level": st.session_state.form_data["grade_level"],
                            "topic": st.session_state.form_data["topic"],
                            "duration": st.session_state.form_data["duration"],
                            "style": st.session_state.form_data["style"],
                            "learning_objectives": json.dumps(st.session_state.form_data["objectives"], ensure_ascii=False),
                            "requirements": json.dumps(st.session_state.form_data["requirements"], ensure_ascii=False),
                            "broad_plan_feedback": feedback
                        })
                        st.session_state.broad_plan = revised_broad_result
                        st.rerun()
            
            # 显示生成按钮
            if st.session_state.show_buttons:
                if st.button("Generate Full Plan", key="full_plan_btn"):
                    generate_full_plan()
                if st.button("Generate Enhanced Plan", key="enhanced_plan_btn"):
                    generate_enhanced_plan()
    
    if submitted:
        if not topic:
            st.error("Please fill in the topic")
            return
        
        # Store form data in session state
        objectives_list = [obj.strip() for obj in learning_objectives.split('\n') if obj.strip()] if learning_objectives else []
        requirements_list = [req.strip() for req in requirements.split('\n') if req.strip()] if requirements else []
        
        st.session_state.form_data.update({
            "grade_level": grade_level,
            "topic": topic,
            "duration": duration,
            "style": style,
            "objectives": objectives_list,
            "requirements": requirements_list,
            "example": example.strip() if example else ""
        })
        
        # Reset the display state
        st.session_state.show_buttons = False
        st.session_state.full_plan = None
            
        generate_lesson_plan(
            grade_level,
            topic,
            duration,
            style,
            objectives_list,
            requirements_list
        )

def generate_lesson_plan(grade_level, topic, duration, style, objectives, requirements):
    """Generate the lesson plan"""
    with st.spinner(UI_TEXT["generating_message"]):
        try:
            # Initialize LLM and chains
            llm = get_llm(model_name="gpt-4o-mini", temperature=0)
            llm2 = get_openrouter_llm(model_name="anthropic/claude-3.5-sonnet", temperature=0)
            broad_chain = create_broad_plan_draft_chain(llm)
            
            # Generate broad plan
            broad_result = broad_chain.invoke({
                "grade_level": grade_level,
                "topic": topic,
                "duration": duration,
                "style": style,
                "learning_objectives": json.dumps(objectives, ensure_ascii=False),
                "requirements": json.dumps(requirements, ensure_ascii=False),
                "broad_plan_feedback": ""
            })
            
            # Store the result and update step
            st.session_state.broad_plan = broad_result
            st.session_state.current_step = "broad_plan"
            st.session_state.show_buttons = True
            st.rerun()
            
        except Exception as e:
            st.error(f"{UI_TEXT['error_prefix']}{str(e)}")

def display_simple_full_plan(plan):
    """Display the simple full lesson plan without critique and revision"""
    try:
        # Parse the plan if it's a string
        if isinstance(plan, str):
            plan = json.loads(plan)
        
        # Extract the actual plan content through multiple levels if needed
        if isinstance(plan, dict):
            # Extract the full_plan part if it exists
            if "full_plan" in plan:
                plan = plan["full_plan"]
            
            # Now get the content
            if "content" in plan:
                content = plan["content"]
            else:
                content = plan
        elif isinstance(plan, list):
            content = plan
        else:
            content = None
        
        # Create container to display plan
        with st.container():
            st.subheader("Full Lesson Plan")
            
            # Display the content if it exists
            if content:
                for phase in content:
                    with st.expander(f"{phase['phase']} ({phase.get('duration', 'N/A')})", expanded=True):
                        for activity in phase.get("activities", []):
                            st.markdown(f"#### {activity['type'].title()}")
                            
                            st.markdown("##### Instructions")
                            st.markdown(activity["instructions"])
                            
                            if activity.get("notes"):
                                st.markdown("##### Notes")
                                st.markdown(f"_{activity['notes']}_")
                            
                            if activity.get("success_criteria"):
                                st.markdown("##### Success Criteria")
                                st.markdown(activity["success_criteria"])
                            
                            st.markdown("---")
            else:
                st.error("Unable to display lesson plan. Please check the plan format.")
                st.write("Raw plan data:")
                st.write(plan)
            
    except Exception as e:
        st.error(f"Error displaying plan: {str(e)}")
        st.write("Raw plan data:")
        st.write(plan)

def generate_full_plan():
    """Generate the full lesson plan"""
    if not st.session_state.broad_plan:
        st.error("Please generate a broad plan first")
        return
        
    with st.spinner("Generating full plan..."):
        try:
            # Initialize LLMs and chains
            llm1 = get_llm(model_name="gpt-4o-mini", temperature=0)
            llm2 = get_openrouter_llm(model_name="anthropic/claude-3.5-sonnet", temperature=0)
            full_draft_chain, _, _ = create_full_plan_chains(llm1, llm1, llm1)
            
            # Extract broad plan information
            broad_plan = st.session_state.broad_plan
            if isinstance(broad_plan, str):
                broad_plan = json.loads(broad_plan)
            if isinstance(broad_plan.get("broad_plan_draft"), str):
                broad_plan = json.loads(broad_plan.get("broad_plan_draft"))
            
            # Generate full plan
            with st.spinner("Drafting full lesson plan..."):
                full_plan_input = {
                    "broad_plan_json": json.dumps(broad_plan, ensure_ascii=False)
                }
                
                full_result = full_draft_chain.invoke(full_plan_input)
                
                # 处理full_result
                if isinstance(full_result, dict) and "full_plan_draft" in full_result:
                    try:
                        # 提取 full_plan_draft 字段
                        full_plan_draft = full_result["full_plan_draft"]
                        
                        # 如果是字符串，需要解析
                        if isinstance(full_plan_draft, str):
                            # 如果包含```json标记，需要提取JSON内容
                            if "```json" in full_plan_draft:
                                json_content = full_plan_draft.split("```json")[1].split("```")[0].strip()
                                full_plan_draft = json.loads(json_content)
                            # 如果是JSON字符串，直接解析
                            else:
                                full_plan_draft = json.loads(full_plan_draft)
                        
                        # 现在 full_plan_draft 应该是一个字典
                        if isinstance(full_plan_draft, dict) and "full_plan" in full_plan_draft:
                            content = full_plan_draft["full_plan"]["content"]
                        else:
                            st.error("Invalid plan format in full_plan_draft")
                            st.write("Parsed full_plan_draft:")
                            st.write(full_plan_draft)
                            return
                            
                    except json.JSONDecodeError as e:
                        st.error(f"Error parsing JSON in full_plan_draft: {str(e)}")
                        st.write("Raw full_plan_draft:")
                        st.write(full_result["full_plan_draft"])
                        return
                    except Exception as e:
                        st.error(f"Error processing full_plan_draft: {str(e)}")
                        st.write("Raw full_result:")
                        st.write(full_result)
                        return
                else:
                    st.error("Invalid result format: missing full_plan_draft")
                    st.write("Raw result:")
                    st.write(full_result)
                    return
                
                st.session_state.full_plan = content
                
                # Display simple full plan
                with st.container():
                    display_simple_full_plan(content)
            
        except Exception as e:
            st.error(f"Error generating full plan: {str(e)}")
            import traceback
            st.error(f"Detailed error: {traceback.format_exc()}")

def generate_enhanced_plan():
    """Generate an enhanced lesson plan with critique and revision"""
    if not st.session_state.broad_plan:
        st.error("Please generate a broad plan first")
        return
        
    with st.spinner("Generating enhanced lesson plan..."):
        try:
            # Initialize LLMs and chains
            llm1 = get_llm(model_name="gpt-4o-mini", temperature=0)
            llm2 = get_openrouter_llm(model_name="anthropic/claude-3.5-sonnet", temperature=0)
            full_draft_chain, critique_chain, revise_chain = create_full_plan_chains(llm1, llm1, llm1)
            
            # Extract broad plan information
            broad_plan = st.session_state.broad_plan
            if isinstance(broad_plan, str):
                broad_plan = json.loads(broad_plan)
            if isinstance(broad_plan.get("broad_plan_draft"), str):
                broad_plan = json.loads(broad_plan.get("broad_plan_draft"))
            
            # Generate initial full plan
            with st.spinner("Creating initial plan..."):
                full_plan_input = {
                    "broad_plan_json": json.dumps(broad_plan, ensure_ascii=False)
                }
                
                try:
                    full_result = full_draft_chain.invoke(full_plan_input)
                    
                    # 处理 full_result
                    if isinstance(full_result, str):
                        if "```json" in full_result:
                            json_content = full_result.split("```json")[1].split("```")[0].strip()
                            full_result = json.loads(json_content)
                        else:
                            full_result = json.loads(full_result)
                except Exception as e:
                    st.error(f"Error generating initial plan: {str(e)}")
                    return
            
            # Generate critique
            with st.spinner("Analyzing plan quality..."):
                try:
                    critique_result = critique_chain.invoke({
                        "full_plan_json": json.dumps(full_result, ensure_ascii=False)
                    })
                    
                    # 处理 critique_result
                    if isinstance(critique_result, str):
                        if "```json" in critique_result:
                            json_content = critique_result.split("```json")[1].split("```")[0].strip()
                            critique_result = json.loads(json_content)
                        else:
                            critique_result = json.loads(critique_result)
                except Exception as e:
                    st.error(f"Error generating critique: {str(e)}")
                    return
            
            # Generate revised plan
            with st.spinner("Improving plan based on analysis..."):
                try:
                    revised_result = revise_chain.invoke({
                        "full_plan_json": json.dumps(full_result, ensure_ascii=False),
                        "critique_text": json.dumps(critique_result, ensure_ascii=False)
                    })
                    
                    # 处理 revised_result
                    if isinstance(revised_result, str):
                        # 如果包含```json标记，需要提取JSON内容
                        if "```json" in revised_result:
                            json_content = revised_result.split("```json")[1].split("```")[0].strip()
                            revised_result = json.loads(json_content)
                        # 如果是JSON字符串，直接解析
                        elif revised_result.startswith('{"'):
                            revised_result = json.loads(revised_result)
                        
                        # 如果有revised_plan字段，提取其内容
                        if isinstance(revised_result, dict):
                            if "revised_plan" in revised_result:
                                if isinstance(revised_result["revised_plan"], str):
                                    revised_result = json.loads(revised_result["revised_plan"])
                                else:
                                    revised_result = revised_result["revised_plan"]
                            elif "full_plan" in revised_result:
                                revised_result = revised_result["full_plan"]
                    
                    # 确保结果是正确的格式
                    if not isinstance(revised_result, dict):
                        st.error("Invalid revised plan format")
                        st.write("Raw revised result:")
                        st.write(revised_result)
                        return
                    
                    st.session_state.full_plan = revised_result
                    
                    # Display the final plan
                    with st.container():
                        display_full_plan(revised_result)
                        
                except json.JSONDecodeError as e:
                    st.error(f"Error parsing revised plan JSON: {str(e)}")
                    st.write("Raw revised result:")
                    st.write(revised_result)
                    return
                except Exception as e:
                    st.error(f"Error processing revised plan: {str(e)}")
                    import traceback
                    st.error(f"Detailed error: {traceback.format_exc()}")
                    return
            
        except Exception as e:
            st.error(f"Error generating enhanced plan: {str(e)}")
            import traceback
            st.error(f"Detailed error: {traceback.format_exc()}")

def display_broad_plan(plan):
    """Display the lesson outline"""
    try:
        # Parse the plan if it's a string
        if isinstance(plan, str):
            plan = json.loads(plan)
        
        # Extract the broad plan draft
        if isinstance(plan.get("broad_plan_draft"), str):
            plan = json.loads(plan.get("broad_plan_draft"))
        
        # Create a container for the plan display
        with st.container():
            st.subheader(UI_TEXT["plan_title"])
            
            # Display input summary
            st.write("### Summary")
            summary = plan.get("input_summary", {})
            if summary:
                st.write(f"**Core Focus:**")
                st.write(summary.get("core_focus", ""))
                
                st.write("**Key Constraints:**")
                for constraint in summary.get("key_constraints", []):
                    st.write(f"- {constraint}")
                
                st.write("**Main Objectives:**")
                for obj in summary.get("main_objectives", []):
                    st.write(f"- {obj}")
            
            # Display objectives
            broad_plan = plan.get("broad_plan", {})
            if broad_plan:
                st.write(f"### {UI_TEXT['objectives_title']}")
                for obj in broad_plan.get("objectives", []):
                    st.write(f"- {obj}")
            
                # Display phases
                st.write(f"### {UI_TEXT['phases_title']}")
                for phase in broad_plan.get("outline", []):
                    with st.expander(f"{phase['phase']} ({phase['duration']} minutes)"):
                        if phase.get("purpose"):
                            st.write(f"**Purpose:**")
                            st.write(phase.get("purpose"))
                            
                        if phase.get("approach"):
                            st.write(f"**Teaching Method:**")
                            st.write(phase.get("approach"))
                            
                        if phase.get("required_elements"):
                            st.write(f"**Required Elements:**")
                            for elem in phase["required_elements"]:
                                st.write(f"- {elem}")
            
            # If we don't have proper structure, show raw data for debugging
            if not summary and not broad_plan:
                st.warning("Plan structure is not as expected. Raw data:")
                st.write(plan)
                
    except Exception as e:
        st.error(f"Error displaying plan: {str(e)}")
        st.write("Raw plan data:")
        st.write(plan)

def display_full_plan(plan):
    """Display the full lesson plan"""
    try:
        # 添加初始验证
        if plan is None:
            st.error("No plan data received")
            return
            
        # Parse the plan if it's a string
        if isinstance(plan, str):
            try:
                plan = json.loads(plan)
            except json.JSONDecodeError as e:
                st.error(f"Error parsing plan JSON: {str(e)}")
                st.write("Raw plan string:")
                st.write(plan)
                return
        
        # Extract the actual plan content through multiple levels if needed
        if isinstance(plan, dict):
            # 记录处理过程
            processing_steps = []
            
            # If we have revised_plan as a string, parse it
            if "revised_plan" in plan:
                processing_steps.append("Found revised_plan field")
                if isinstance(plan["revised_plan"], str):
                    try:
                        plan = json.loads(plan["revised_plan"])
                        processing_steps.append("Parsed revised_plan string")
                    except json.JSONDecodeError as e:
                        st.error(f"Error parsing revised_plan JSON: {str(e)}")
                        st.write("Raw revised_plan:")
                        st.write(plan["revised_plan"])
                        return
                else:
                    plan = plan["revised_plan"]
                    processing_steps.append("Used revised_plan object")
            
            # Now extract the full_plan part if it exists
            full_plan = None
            slides = None
            
            if "full_plan" in plan:
                processing_steps.append("Found full_plan field")
                if isinstance(plan["full_plan"], dict):
                    full_plan = plan["full_plan"]
                elif isinstance(plan["full_plan"], str):
                    try:
                        full_plan = json.loads(plan["full_plan"])
                        processing_steps.append("Parsed full_plan string")
                    except json.JSONDecodeError as e:
                        st.error(f"Error parsing full_plan JSON: {str(e)}")
                        st.write("Raw full_plan:")
                        st.write(plan["full_plan"])
                        return
            
            if "slides" in plan:
                processing_steps.append("Found slides field")
                slides = plan["slides"]
            
            # 如果没有找到必要的数据，尝试直接使用plan
            if not full_plan and "content" in plan:
                processing_steps.append("Using plan as full_plan")
                full_plan = plan
        
            # Debug information if needed
            if not full_plan and not slides:
                st.error("Could not find plan content")
                st.write("Processing steps:", processing_steps)
                st.write("Available fields:", list(plan.keys()))
                st.write("Raw plan structure:")
                st.write(plan)
                return
        
        # Create container to display plan
        with st.container():
            # Display the full plan content
            if full_plan and isinstance(full_plan, dict):
                content = full_plan.get("content")
                if not content:
                    st.error("No content found in full plan")
                    st.write("Full plan structure:")
                    st.write(full_plan)
                    return
                    
                st.subheader("Full Lesson Plan")
                for phase in content:
                    if not isinstance(phase, dict):
                        continue
                        
                    with st.expander(f"{phase.get('phase', 'Unnamed Phase')} ({phase.get('duration', 'N/A')})", expanded=True):
                        for activity in phase.get("activities", []):
                            if not isinstance(activity, dict):
                                continue
                                
                            st.markdown(f"#### {activity.get('type', 'Activity').title()}")
                            
                            if activity.get("instructions"):
                                st.markdown("##### Instructions")
                                st.markdown(activity["instructions"])
                            
                            if activity.get("notes"):
                                st.markdown("##### Notes")
                                st.markdown(f"_{activity['notes']}_")
                            
                            if activity.get("success_criteria"):
                                st.markdown("##### Success Criteria")
                                st.markdown(activity["success_criteria"])
                            
                            st.markdown("---")
            
            # Display the slides if they exist
            if slides:
                st.subheader("Presentation Slides")
                for slide in slides:
                    if not isinstance(slide, dict):
                        continue
                        
                    with st.expander(f"Slide {slide.get('number', '?')}: {slide.get('title', 'Untitled')}", expanded=False):
                        if slide.get("phase"):
                            st.markdown(f"**Phase:** {slide['phase']}")
                        
                        if slide.get("bullet_points"):
                            st.markdown("##### Key Points")
                            for point in slide["bullet_points"]:
                                st.markdown(f"- {point}")
                        
                        if slide.get("speaker_notes"):
                            st.markdown("##### Speaker Notes")
                            st.markdown(f"_{slide['speaker_notes']}_")
                        
                        st.markdown("---")
            
            # Show error if neither full plan nor slides are available
            if not full_plan and not slides:
                st.error("Unable to display lesson plan. Please check the plan format.")
            
    except Exception as e:
        st.error(f"Error displaying lesson plan: {str(e)}")
        st.write("Raw plan data:")
        st.write(plan)
        import traceback
        st.error(f"Detailed error: {traceback.format_exc()}")

def main():
    """Main application entry point"""
    st.set_page_config(
        page_title=UI_TEXT["title"],
        page_icon="📚",
        layout="wide"
    )
    
    # Load custom CSS
    with open(Path(__file__).parent / "styles/main.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    init_session_state()
    render_input_form()

if __name__ == "__main__":
    main() 
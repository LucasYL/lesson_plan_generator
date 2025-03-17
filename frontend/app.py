# Standard library imports
import sys
import os
import json
from pathlib import Path

# Third-party imports
import streamlit as st

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Local application imports
from backend.chains import get_llm, get_openrouter_llm
from backend.chains import create_broad_plan_draft_chain, create_revise_plan_chain
from backend.chains import create_artifact_chain

# UI text constants
UI_TEXT = {
    "title": "AI Lesson Plan Generator",
    "grade_level": "🏫 Education Level",
    "duration": "⏱️ Duration (minutes)",
    "topic": "📝 Topic",
    "teaching_style": "📖 Teaching Style",
    "learning_objectives": "🎯 Learning Objectives (Optional)",
    "requirements": "📋 Requirements (Optional)",
    "generate_button": "🚀 Generate Plan",
    "error_missing_fields": "Please fill in the topic and learning objectives",
    "generating_message": "Generating lesson plan, please wait...",
    "error_prefix": "Error occurred: ",
    "plan_title": "📚 Lesson Plan",
    "objectives_title": "🎯 Learning Objectives",
    "phases_title": "📊 Teaching Phases",
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
    {"name": "Lecture-based", "description": "Traditional approach where the instructor presents information to students. Effective for delivering structured content and theoretical knowledge to large groups."},
    {"name": "Interactive", "description": "Engages students through discussions, Q&A sessions, and collaborative activities. Promotes active participation and deeper understanding through dialogue."},
    {"name": "Practice-oriented", "description": "Focuses on hands-on application of concepts through exercises, projects, and problem-solving. Helps develop practical skills and reinforces theoretical knowledge."},
    {"name": "Blended", "description": "Combines online and in-person learning experiences. Offers flexibility while maintaining personal interaction and guidance from the instructor."},
    {"name": "Inquiry-based", "description": "Students explore topics through questions, investigations, and discoveries. Develops critical thinking and research skills by encouraging students to find answers independently."}
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
            "example": None,
            "reference_files": None,
            "reference_text": None
        }
    # Add phase editing tracking
    if 'phase_edits' not in st.session_state:
        st.session_state.phase_edits = {
            'changes': [],  # Store phase modifications
            'original_plan': None,  # Original plan for reference
            'has_changes': False  # Track if there are unsaved changes
        }
    if 'editing_phase' not in st.session_state:
        st.session_state.editing_phase = None  # Track which phase is being edited
    # Revision dialog state
    if 'show_revision_dialog' not in st.session_state:
        st.session_state.show_revision_dialog = False
    if 'revision_data' not in st.session_state:
        st.session_state.revision_data = {
            'phases': [],
            'feedback': ""
        }
    # 教学风格详情对话框状态
    if 'show_style_info' not in st.session_state:
        st.session_state.show_style_info = False
    if 'selected_style_info' not in st.session_state:
        st.session_state.selected_style_info = None

def render_input_form():
    """Render the lesson plan input form"""
    st.header(UI_TEXT["title"])
    
    # Store LLM instance in session state
    if 'llm' not in st.session_state:
        st.session_state.llm = get_llm(model_name="gpt-4o", temperature=0)
    if 'broad_chain' not in st.session_state:
        st.session_state.broad_chain = create_broad_plan_draft_chain(st.session_state.llm)
    
    # Create two-column layout
    left_col, right_col = st.columns([2, 1])
    
    # 存储当前选择的教学风格
    current_style = st.session_state.form_data["style"] if st.session_state.form_data["style"] else TEACHING_STYLES[0]["name"]
    
    with left_col:
        # 在表单外部先显示教学风格选择
        st.markdown(f"""
        <div style="margin-bottom: 10px; background-color: #f8f9fa; padding: 0.5rem; border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.08);">
            <span style="font-size: 0.9rem; font-weight: 500; color: #31333F; margin-left: 18px;">
                {UI_TEXT["teaching_style"]}
            </span>
            <div style="margin-top: 4px;">
        """, unsafe_allow_html=True)
        
        # 使用Streamlit的radio组件来选择教学风格
        style_names = [style["name"] for style in TEACHING_STYLES]
        selected_style = st.radio(
            label="选择教学风格",
            options=style_names,
            index=style_names.index(current_style) if current_style in style_names else 0,
            horizontal=True,
            label_visibility="collapsed"
        )
        
        st.markdown("""
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 如果选择了新的风格，更新session state
        if selected_style != current_style:
            st.session_state.form_data["style"] = selected_style
            # 找到对应的风格对象
            for style_obj in TEACHING_STYLES:
                if style_obj["name"] == selected_style:
                    st.session_state.selected_style_info = style_obj
                    st.session_state.show_style_info = True
                    break
            st.rerun()
        
        # 开始表单
        with st.form(key="lesson_plan_input"):
            # 隐藏字段，用于传递选中的教学风格
            style = selected_style
            
            # 第一排：Education Level 和 Duration
            col1, col2 = st.columns(2)
            
            with col1:
                grade_level = st.selectbox(
                    UI_TEXT["grade_level"],
                    GRADE_LEVELS,
                    index=GRADE_LEVELS.index(st.session_state.form_data["grade_level"]) if st.session_state.form_data["grade_level"] else 4,

                )
            
            with col2:
                duration = st.text_input(
                    UI_TEXT["duration"], 
                    value=st.session_state.form_data["duration"] if st.session_state.form_data["duration"] else "40",
                )
            
            # 第二排：Topic 占整行
            topic = st.text_input(
                UI_TEXT["topic"],
                value=st.session_state.form_data["topic"] if st.session_state.form_data["topic"] else "",
            )
            
            # Add file upload component
            from components.FileUpload import FileUpload
            file_uploader = FileUpload()
            st.write("📄 Upload Reference Materials (Optional) - Support uploading up to 2 PDF files, each file not exceeding 10MB")
            
            # File upload component
            uploaded_files = st.file_uploader(
                "Choose files",
                type=["pdf"],
                accept_multiple_files=True
            )
            
            if uploaded_files:
                # Save and process files
                from backend.file_processor import FileProcessor
                file_paths = file_uploader.save_uploaded_files(uploaded_files)
                processed_files = FileProcessor.process_files(file_paths)
                
                # Merge all file texts
                reference_text = "\n\n".join(processed_files.values())
                st.session_state.form_data["reference_text"] = reference_text
                st.session_state.form_data["reference_files"] = [f.name for f in uploaded_files]
                
                # Display processing results
                st.success(f"Successfully processed {len(processed_files)} reference files")
            
            # Add example lesson plan input area with expander
            with st.expander("Example Lesson Plan (Optional)", expanded=False):
                example = st.text_area(
                    "Provide a reference lesson plan example",
                    height=150,
                    value=st.session_state.form_data["example"] if st.session_state.form_data["example"] else "",
                    placeholder="You can provide a reference lesson plan example here. If left empty, default examples will be used."
                )
            
            # Add learning objectives with expander    
            with st.expander("Learning Objectives (Optional)", expanded=False):
                learning_objectives = st.text_area(
                    "Enter learning objectives",
                    height=100,
                    value="\n".join(st.session_state.form_data["objectives"]) if st.session_state.form_data["objectives"] else "",
                    placeholder="Example:\n1. Understand core concepts\n2. Master key skills\n3. Apply independently"
                )
            
            # Add requirements with expander
            with st.expander("Requirements (Optional)", expanded=False):
                requirements = st.text_area(
                    "Enter requirements",
                    height=100,
                    value="\n".join(st.session_state.form_data["requirements"]) if st.session_state.form_data["requirements"] else "",
                    placeholder="Example:\n1. Group discussion required\n2. Include practical exercises\n3. Include assessment"
                )
            
            # 确保提交按钮正确显示
            submitted = st.form_submit_button(label=UI_TEXT["generate_button"])
    
    # 显示教学风格详情对话框
    if st.session_state.show_style_info and st.session_state.selected_style_info:
        with st.sidebar:
            st.subheader(f"About {st.session_state.selected_style_info['name']} Teaching Style")
            st.write(st.session_state.selected_style_info["description"])
            if st.button("❌ Close"):
                st.session_state.show_style_info = False
                st.session_state.selected_style_info = None
                st.rerun()
    
    # Display broad plan and buttons if available
    if st.session_state.broad_plan:
        with left_col:
            # Check if this is a critique_and_improve result
            if isinstance(st.session_state.broad_plan, dict) and all(k in st.session_state.broad_plan for k in ["broad_plan_json", "critique_text", "revised_plan"]):
                # Use specialized function to display improved plan
                display_revised_plan(st.session_state.broad_plan)
            else:
                # Use original function to display regular plan
                display_broad_plan(st.session_state.broad_plan)
    
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
            llm = get_llm(model_name="gpt-4o", temperature=0)
            llm2 = get_openrouter_llm(model_name="anthropic/claude-3.5-sonnet", temperature=0)
            broad_chain = create_broad_plan_draft_chain(llm)
            
            # Prepare reference document content
            reference_text = st.session_state.form_data.get("reference_text", "")
            
            # Format objectives and requirements as proper JSON arrays
            objectives_json = json.dumps(objectives) if isinstance(objectives, list) else objectives
            requirements_json = json.dumps(requirements) if isinstance(requirements, list) else requirements
            
            # Generate broad plan
            broad_result = broad_chain.invoke({
                "grade_level": grade_level,
                "topic": topic,
                "duration": duration,
                "style": style,
                "learning_objectives": objectives_json,
                "requirements": requirements_json,
                "broad_plan_feedback": "",
                "reference_context": reference_text
            })
            
            # Ensure the result is proper JSON
            if isinstance(broad_result, str):
                try:
                    # Try to parse if it's a JSON string
                    broad_result = json.loads(broad_result)
                except json.JSONDecodeError:
                    # If it contains markdown code blocks, extract the JSON
                    if "```json" in broad_result:
                        json_content = broad_result.split("```json")[1].split("```")[0].strip()
                        broad_result = json.loads(json_content)
            
            # Store the result and update step
            st.session_state.broad_plan = broad_result
            st.session_state.current_step = "broad_plan"
            st.session_state.show_buttons = True
            st.rerun()
            
        except Exception as e:
            st.error(f"{UI_TEXT['error_prefix']}{str(e)}")
            import traceback
            st.error(f"Detailed error: {traceback.format_exc()}")
            # Display the raw result for debugging
            st.write("Raw result:")
            st.write(broad_result)

def export_learning_materials_to_markdown(plan_data):
    """Convert learning materials to markdown format
    
    Args:
        plan_data: The lesson plan data containing learning materials
        
    Returns:
        str: Markdown formatted learning materials
    """
    if not plan_data or not plan_data.get("outline"):
        return "No learning materials available."
        
    markdown_content = "# Learning Materials\n\n"
    
    has_materials = False
    for phase in plan_data.get("outline", []):
        if not phase.get("artifacts"):
            continue
            
        has_materials = True
        markdown_content += f"## {phase['phase']}\n\n"
        
        for artifact in phase["artifacts"]:
            markdown_content += f"### {artifact['type'].title()}\n\n"
            
            if artifact['type'] == "quiz":
                # Handle quiz content
                try:
                    quiz_content = artifact["content"]
                    quiz_data = json.loads(quiz_content) if isinstance(quiz_content, str) else quiz_content
                    
                    markdown_content += f"#### {quiz_data['phase_name']} - Quiz\n\n"
                    
                    # Questions section
                    markdown_content += "##### Questions\n\n"
                    for question in quiz_data["quiz_data"]["questions"]:
                        markdown_content += f"**Question {question['id']}**\n\n"
                        markdown_content += f"{question['question']}\n\n"
                        markdown_content += "**Options:**\n\n"
                        for opt_key, opt_value in question["options"].items():
                            markdown_content += f"- {opt_key}) {opt_value}\n"
                        markdown_content += "\n"
                    
                    # Answers section
                    markdown_content += "##### Answers & Explanations\n\n"
                    for answer in quiz_data["quiz_data"]["answers"]:
                        markdown_content += f"**Question {answer['id']}**\n\n"
                        markdown_content += f"Correct Answer: {answer['correct_answer']}\n\n"
                        markdown_content += "Explanation:\n\n"
                        markdown_content += f"{answer['explanation']}\n\n"
                        
                except Exception as e:
                    markdown_content += f"Error formatting quiz: {str(e)}\n\n"
                    markdown_content += f"```\n{artifact['content']}\n```\n\n"
            else:
                # Handle other content types (code_practice, slides)
                markdown_content += f"{artifact['content']}\n\n"
                
            markdown_content += "---\n\n"
    
    if not has_materials:
        return "No learning materials have been generated yet."
        
    return markdown_content

def display_learning_materials(broad_plan):
    """Display all learning materials for the course
    
    Args:
        broad_plan: Teaching plan containing learning materials
    """
    if not broad_plan or not broad_plan.get("outline"):
        return
        
    st.markdown("---")
    st.markdown("## 📚 Learning Materials")
    
    def display_quiz(quiz_content):
        """Display quiz content"""
        try:
            # Parse quiz data
            quiz_data = json.loads(quiz_content) if isinstance(quiz_content, str) else quiz_content
                
            # Display quiz title
            st.markdown(f"### {quiz_data['phase_name']} - Quiz")
            
            # Create questions and answers tabs
            questions_tab, answers_tab = st.tabs(["Questions", "Answers & Explanations"])
            
            # Display questions
            with questions_tab:
                for question in quiz_data["quiz_data"]["questions"]:
                    st.markdown(f"#### Question {question['id']}")
                    st.markdown(question["question"])
                    st.markdown("**Options:**")
                    for opt_key, opt_value in question["options"].items():
                        st.markdown(f"{opt_key}) {opt_value}")
                    st.markdown("---")
                
            # Display answers and explanations
            with answers_tab:
                for answer in quiz_data["quiz_data"]["answers"]:
                    st.markdown(f"#### Question {answer['id']}")
                    st.markdown(f"**Correct Answer:** {answer['correct_answer']}")
                    st.markdown("**Explanation:**")
                    st.markdown(answer["explanation"])
                    st.markdown("---")
                    
        except Exception as e:
            st.error(f"Error displaying quiz: {str(e)}")
            st.markdown(quiz_content)
    
    def display_code_practice(content):
        """Display coding practice content"""
        st.markdown(content)
    
    def display_slides(content):
        """Display slides content"""
        st.markdown(content)
    
    # Iterate through all phases to display materials
    has_materials = False
    for phase in broad_plan.get("outline", []):
        if not phase.get("artifacts"):
            continue
            
        has_materials = True
        st.markdown(f"### {phase['phase']}")
        
        # Use tabs if multiple materials exist
        if len(phase["artifacts"]) > 1:
            tabs = st.tabs([f"{artifact['type'].title()}" for artifact in phase["artifacts"]])
            for tab, artifact in zip(tabs, phase["artifacts"]):
                with tab:
                    if artifact['type'] == "quiz":
                        display_quiz(artifact["content"])
                    elif artifact['type'] == "code_practice":
                        display_code_practice(artifact["content"])
                    elif artifact['type'] == "slides":
                        display_slides(artifact["content"])
        else:
            # Display directly if only one material
            artifact = phase["artifacts"][0]
            with st.expander(f"{artifact['type'].title()}", expanded=True):
                if artifact['type'] == "quiz":
                    display_quiz(artifact["content"])
                elif artifact['type'] == "code_practice":
                    display_code_practice(artifact["content"])
                elif artifact['type'] == "slides":
                    display_slides(artifact["content"])
        
        st.markdown("---")
    
    if not has_materials:
        st.info("No learning materials have been generated yet. Click 'Generate Learning Materials' in any phase to create materials.")
    else:
        # 添加专门用于下载学习材料的按钮
        st.markdown("### 📥 Download Learning Materials")
        materials_markdown = export_learning_materials_to_markdown(broad_plan)
        st.markdown(create_download_link(materials_markdown, "learning_materials.md", "📥 Download Materials as Markdown"), unsafe_allow_html=True)

def display_broad_plan(plan):
    """Display the course outline"""
    try:
        # Parse plan
        if isinstance(plan, str):
            plan = json.loads(plan)
        
        # Extract broad plan draft
        if "broad_plan_draft" in plan:
            draft = plan["broad_plan_draft"]
            
            if isinstance(draft, str):
                try:
                    if "```json" in draft:
                        json_content = draft.split("```json")[1].split("```")[0].strip()
                        plan = json.loads(json_content)
                    else:
                        plan = json.loads(draft)
                except json.JSONDecodeError as e:
                    st.error(f"Error parsing draft JSON: {str(e)}")
                    st.code(draft, language="json")
                    return
        
        # Create display container
        with st.container():
            st.header(UI_TEXT["plan_title"])
            
            # Add download button
            broad_plan = plan.get("broad_plan", {})
            
            # Handle special case: if plan contains revised_plan key, it's a critique_and_improve result
            if not broad_plan and "revised_plan" in plan:
                revised_plan = plan["revised_plan"]
                
                # If revised_plan is a string, try to parse it
                if isinstance(revised_plan, str):
                    try:
                        if "```json" in revised_plan:
                            json_content = revised_plan.split("```json")[1].split("```")[0].strip()
                            revised_plan = json.loads(json_content)
                        else:
                            revised_plan = json.loads(revised_plan)
                    except json.JSONDecodeError as e:
                        st.error(f"Error parsing revised_plan: {str(e)}")
                        st.code(revised_plan, language="json")
                        return
                
                # If revised_plan contains broad_plan key, use it
                if isinstance(revised_plan, dict) and "broad_plan" in revised_plan:
                    broad_plan = revised_plan["broad_plan"]
                else:
                    # Otherwise use revised_plan directly
                    broad_plan = revised_plan
            
            # If broad_plan is empty, try to use plan directly
            if not broad_plan and isinstance(plan, dict) and "objectives" in plan and "outline" in plan:
                broad_plan = plan
                
            # Special handling: if plan contains broad_plan_json, critique_text, revised_plan keys
            if not broad_plan and all(k in plan for k in ["broad_plan_json", "critique_text", "revised_plan"]):
                revised_plan = plan["revised_plan"]
                
                # If revised_plan is a string, try to parse it
                if isinstance(revised_plan, str):
                    try:
                        if "```json" in revised_plan:
                            json_content = revised_plan.split("```json")[1].split("```")[0].strip()
                            revised_plan = json.loads(json_content)
                        else:
                            revised_plan = json.loads(revised_plan)
                    except json.JSONDecodeError as e:
                        st.error(f"Error parsing revised_plan: {str(e)}")
                        st.code(revised_plan, language="json")
                        return
                
                # If revised_plan contains broad_plan key, use it
                if isinstance(revised_plan, dict) and "broad_plan" in revised_plan:
                    broad_plan = revised_plan["broad_plan"]
                else:
                    # Otherwise use revised_plan directly
                    broad_plan = revised_plan
            
            # Display learning objectives
            if broad_plan:
                st.write("#### 🎯 Learning Objectives")
                for obj in broad_plan.get("objectives", []):
                    if "[REF]" in obj:
                        st.markdown(f"- 📚 {obj}")
                    else:
                        st.write(f"- {obj}")
            
                # Display teaching phases
                st.write("#### 📊 Teaching Phases")
                
                # Initialize ArtifactModal
                from components.ArtifactModal import ArtifactModal
                artifact_modal = ArtifactModal()
                
                # Display each phase
                for i, phase in enumerate(broad_plan.get("outline", [])):
                    with st.expander(f"{phase['phase']} ({phase['duration']})", expanded=False):
                        if phase.get("purpose"):
                            st.write("**🎯 Purpose:**")
                            if "[REF]" in phase["purpose"]:
                                st.markdown(f"📚 {phase['purpose']}")
                            else:
                                st.write(phase["purpose"])
                        
                        if phase.get("description"):
                            st.write("**📝 Description:**")
                            st.write(phase["description"])
                        
                        # Add generate materials button
                        st.markdown("---")
                        col1, col2 = st.columns([2, 4])
                        with col1:
                            if st.button("📦 Generate Learning Materials", key=f"add_artifact_{i}"):
                                # Create a closure to save broad_plan
                                def generate_callback(params):
                                    return handle_artifact_generation(params, broad_plan)
                                artifact_modal.show(
                                    phase_id=str(i),
                                    phase_content={
                                        "phase": phase["phase"],
                                        "purpose": phase.get("purpose", ""),
                                        "description": phase.get("description", "")
                                    },
                                    generate_callback=generate_callback
                                )
                                st.rerun()
                
                # Render artifact dialog
                artifact_modal.render_dialog()
                
                st.markdown("---")
                add_download_button(broad_plan)
                
                # Add buttons for plan enhancement
                col1, col2 = st.columns([1, 1])
                with col1:
                    # Add revise plan button (opens dialog)
                    if st.button("✏️ Revise Plan", type="primary"):
                        st.session_state.show_revision_dialog = True
                        st.rerun()
                with col2:
                    # Add critique & improve button (automatic enhancement)
                    if st.button("🔍 Critique & Improve", type="secondary"):
                        critique_and_improve()
            
            # If structure is not correct, display original data
            if not broad_plan:
                st.warning("Plan structure is not as expected. Raw data:")
                st.write(plan)
                
            # Display learning materials
            if broad_plan:
                display_learning_materials(broad_plan)
                
    except Exception as e:
        st.error(f"Error displaying plan: {str(e)}")
        st.write("Raw plan data:")
        st.write(plan)
        import traceback
        st.error(f"Detailed error: {traceback.format_exc()}")

def prepare_revision_input():
    """Prepare the revision input combining user feedback and phase changes"""
    # Get user feedback
    feedback = st.session_state.get('broad_plan_feedback', '')
    
    # Get current phases (including modifications)
    current_phases = []
    if st.session_state.phase_edits['has_changes']:
        # Get the original plan phases
        original_phases = st.session_state.phase_edits['original_plan']['broad_plan']['outline']
        changes_dict = {change['index']: change for change in st.session_state.phase_edits['changes']}
        
        # Apply changes while maintaining order
        for i, phase in enumerate(original_phases):
            if i in changes_dict:
                current_phases.append({
                    'phase': changes_dict[i]['phase'],
                    'duration': changes_dict[i]['duration']
                })
            else:
                current_phases.append({
                    'phase': phase['phase'],
                    'duration': phase['duration']
                })
    else:
        # If no changes, get phases from original plan
        original_phases = st.session_state.phase_edits['original_plan']['broad_plan']['outline']
        current_phases = [{
            'phase': phase['phase'],
            'duration': phase['duration']
        } for phase in original_phases]
    
    # Combine feedback and phase changes
    combined_feedback = {
        "user_feedback": feedback,
        "current_phases": current_phases,
        "has_phase_changes": st.session_state.phase_edits['has_changes']
    }
    
    return json.dumps(combined_feedback, ensure_ascii=False)

def revision_dialog():
    """Display the revision dialog for editing phases and providing feedback"""
    if not st.session_state.show_revision_dialog:
        return
        
    # Create a new page for revision
    st.markdown("## ✏️ Revise Lesson Plan")
    
    # Initialize revision data if empty
    if not st.session_state.revision_data['phases']:
        # Handle broad_plan data structure
        broad_plan = st.session_state.broad_plan
        if isinstance(broad_plan, str):
            broad_plan = json.loads(broad_plan)
        if "broad_plan_draft" in broad_plan:
            if isinstance(broad_plan["broad_plan_draft"], str):
                if "```json" in broad_plan["broad_plan_draft"]:
                    json_content = broad_plan["broad_plan_draft"].split("```json")[1].split("```")[0].strip()
                    broad_plan = json.loads(json_content)
                else:
                    broad_plan = json.loads(broad_plan["broad_plan_draft"])
        
        # Get phases data
        outline = broad_plan.get("broad_plan", {}).get("outline", [])
        st.session_state.revision_data['phases'] = [
            {
                'phase': phase['phase'],
                'duration': phase['duration'],
                'purpose': phase.get('purpose', ''),
                'description': phase.get('description', '')
            }
            for phase in outline
        ]
    
    # Display phases for editing
    st.markdown("### 📊 Teaching Phases")
    phases = st.session_state.revision_data['phases']
    for i, phase in enumerate(phases):
        with st.container():
            st.markdown(f"#### 📝 Phase {i+1}")
            col1, col2 = st.columns([2, 1])
            with col1:
                phase['phase'] = st.text_input(
                    "Phase Name",
                    value=phase['phase'],
                    key=f"phase_name_{i}"
                )
            with col2:
                phase['duration'] = st.text_input(
                    "Duration",
                    value=phase['duration'],
                    key=f"phase_duration_{i}"
                )
            # Display purpose and description (read-only)
            if phase.get('purpose'):
                st.markdown("**🎯 Purpose:**")
                st.markdown(f"_{phase['purpose']}_")
            if phase.get('description'):
                st.markdown("**📝 Description:**")
                st.markdown(f"_{phase['description']}_")
            st.markdown("---")
    
    # Add feedback section
    st.markdown("### 💬 Feedback")
    feedback = st.text_area(
        "Provide feedback to improve the plan",
        value=st.session_state.revision_data['feedback'],
        height=150,
        placeholder="Enter your suggestions for improvement..."
    )
    st.session_state.revision_data['feedback'] = feedback
    
    # Add buttons
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("💾 Save & Revise", type="primary"):
            # Prepare revision input
            combined_feedback = {
                "user_feedback": feedback,
                "current_phases": [
                    {
                        'phase': phase['phase'],
                        'duration': phase['duration']
                    }
                    for phase in st.session_state.revision_data['phases']
                ],
                "has_phase_changes": True
            }
            
            # Get reference text from session state
            reference_text = st.session_state.form_data.get("reference_text", "")
            
            # Generate revised plan
            with st.spinner("Revising plan..."):
                revised_broad_result = st.session_state.broad_chain.invoke({
                    "grade_level": st.session_state.form_data["grade_level"],
                    "topic": st.session_state.form_data["topic"],
                    "duration": st.session_state.form_data["duration"],
                    "style": st.session_state.form_data["style"],
                    "learning_objectives": json.dumps(st.session_state.form_data["objectives"], ensure_ascii=False),
                    "requirements": json.dumps(st.session_state.form_data["requirements"], ensure_ascii=False),
                    "broad_plan_feedback": json.dumps(combined_feedback, ensure_ascii=False),
                    "reference_context": reference_text
                })
                
                # Update plan and close dialog
                st.session_state.broad_plan = revised_broad_result
                st.session_state.show_revision_dialog = False
                st.session_state.revision_data = {'phases': [], 'feedback': ""}
                st.rerun()
    
    with col2:
        if st.button("❌ Cancel"):
            st.session_state.show_revision_dialog = False
            st.session_state.revision_data = {'phases': [], 'feedback': ""}
            st.rerun()

def handle_artifact_generation(artifact_result, broad_plan):
    """Handle the generation of learning materials
    
    Args:
        artifact_result: Result from ArtifactModal containing generation parameters
        broad_plan: Current teaching plan
        
    Returns:
        bool: Whether the generation was successful
    """
    if not artifact_result:
        return False
        
    try:
        # Create artifact chain
        llm = get_llm(model_name="gpt-4o", temperature=0)
        chain = create_artifact_chain(llm, artifact_result["type"])
        
        # Generate content
        with st.spinner(f"Generating {artifact_result['type']}..."):
            result = chain.invoke({
                "phase_content": json.dumps(artifact_result["phase_content"], ensure_ascii=False),
                **artifact_result["requirements"]
            })
            
            # Process output format
            if artifact_result['type'] == "quiz":
                # Handle quiz output
                if isinstance(result, dict) and "quiz" in result:
                    artifact_content = result["quiz"]
                else:
                    artifact_content = result
                
                if isinstance(artifact_content, str):
                    if "```json" in artifact_content:
                        artifact_content = artifact_content.split("```json")[1].split("```")[0].strip()
                    artifact_content = json.loads(artifact_content)
                    
            elif artifact_result['type'] == "code_practice":
                # Handle code practice output
                if isinstance(result, dict) and "code_practice" in result:
                    artifact_content = result["code_practice"]
                else:
                    artifact_content = result
            
            elif artifact_result['type'] == "slides":
                # Handle slides output
                if isinstance(result, dict) and "slides" in result:
                    artifact_content = result["slides"]
                else:
                    artifact_content = result
            
            # Add to corresponding phase
            phase_id = int(artifact_result["phase_id"])
            phase = broad_plan["outline"][phase_id]
            if "artifacts" not in phase:
                phase["artifacts"] = []
            
            phase["artifacts"].append({
                "type": artifact_result["type"],
                "content": artifact_content
            })
            
            # Update session state
            st.session_state.broad_plan = {
                "broad_plan_draft": json.dumps({
                    "broad_plan": broad_plan
                }, ensure_ascii=False)
            }
            
            return True
            
    except Exception as e:
        st.error(f"Error generating material: {str(e)}")
        return False

def export_to_markdown(plan_data):
    """Export the lesson plan to Markdown format"""
    # If plan_data is a string, try to parse it as JSON
    if isinstance(plan_data, str):
        try:
            plan_data = json.loads(plan_data)
        except:
            pass
    
    # Extract broad_plan if it exists
    if isinstance(plan_data, dict):
        if "broad_plan_draft" in plan_data:
            try:
                draft = plan_data["broad_plan_draft"]
                if isinstance(draft, str):
                    if "```json" in draft:
                        json_content = draft.split("```json")[1].split("```")[0].strip()
                        plan_data = json.loads(json_content)
                    else:
                        plan_data = json.loads(draft)
            except:
                pass
        
        if "broad_plan" in plan_data:
            plan_data = plan_data["broad_plan"]
    
    # Start building Markdown content
    md_content = "# Lesson Plan\n\n"
    
    # Add learning objectives
    md_content += "## Learning Objectives\n\n"
    for obj in plan_data.get("objectives", []):
        md_content += f"- {obj}\n"
    md_content += "\n"
    
    # Add teaching phases
    md_content += "## Teaching Phases\n\n"
    for i, phase in enumerate(plan_data.get("outline", [])):
        md_content += f"### {phase['phase']} ({phase['duration']})\n\n"
        
        # Add purpose
        if phase.get("purpose"):
            md_content += f"**Purpose:** {phase['purpose']}\n\n"
        
        # Add description
        if phase.get("description"):
            md_content += f"**Description:** {phase['description']}\n\n"
        
        # Add learning materials
        if phase.get("artifacts"):
            md_content += "#### Learning Materials\n\n"
            for artifact in phase["artifacts"]:
                md_content += f"##### {artifact['type'].title()}\n\n"
                
                # Format content based on type
                if artifact['type'] == "quiz" and isinstance(artifact['content'], dict):
                    # Format quiz content
                    md_content += "**Questions:**\n\n"
                    for j, question in enumerate(artifact['content'].get('questions', [])):
                        md_content += f"{j+1}. {question.get('question', '')}\n"
                        for option in question.get('options', []):
                            md_content += f"   - {option}\n"
                        md_content += f"   Answer: {question.get('answer', '')}\n\n"
                else:
                    # For code practice, slides, etc.
                    md_content += f"```\n{artifact['content']}\n```\n\n"
    
    return md_content

def create_download_link(content, filename, link_text):
    """Create a download link for text content"""
    import base64
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:text/markdown;base64,{b64}" download="{filename}" style="display: inline-block; padding: 0.5rem 1rem; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 4px; font-weight: bold;">{link_text}</a>'
    return href

def add_download_button(plan_data):
    """Add a download button for the lesson plan"""
    if not plan_data:
        return
    
    md_content = export_to_markdown(plan_data)
    download_link = create_download_link(
        md_content, 
        "lesson_plan.md", 
        "📥 Download Lesson Plan"
    )
    st.markdown(download_link, unsafe_allow_html=True)

def display_revised_plan(plan_data):
    """
    Specialized function to display the plan after critique & improve
    
    Args:
        plan_data: Data structure containing broad_plan_json, critique_text, revised_plan
    """
    try:
        # Extract revised_plan
        revised_plan = plan_data.get("revised_plan", {})
        
        # If revised_plan is a string, try to parse it
        if isinstance(revised_plan, str):
            try:
                if "```json" in revised_plan:
                    json_content = revised_plan.split("```json")[1].split("```")[0].strip()
                    revised_plan = json.loads(json_content)
                else:
                    revised_plan = json.loads(revised_plan)
            except json.JSONDecodeError as e:
                st.error(f"Error parsing revised_plan: {str(e)}")
                st.code(revised_plan, language="json")
                return
        
        # Ensure we have a valid plan structure
        broad_plan = None
        
        # Check if revised_plan already has the right structure
        if isinstance(revised_plan, dict) and "objectives" in revised_plan and "outline" in revised_plan:
            broad_plan = revised_plan
        # Check if revised_plan contains a broad_plan key
        elif isinstance(revised_plan, dict) and "broad_plan" in revised_plan:
            broad_plan = revised_plan["broad_plan"]
        
        # If we still don't have a valid plan, show an error
        if not broad_plan or not isinstance(broad_plan, dict) or "objectives" not in broad_plan or "outline" not in broad_plan:
            st.warning("Improved plan structure is incorrect.")
            st.write("revised_plan content:")
            st.write(revised_plan)
            return
        
        # Display plan content
        with st.container():
            st.header(UI_TEXT["plan_title"] + " (Improved)")
            
            # Display learning objectives
            st.write("#### 🎯 Learning Objectives")
            for obj in broad_plan.get("objectives", []):
                if "[REF]" in obj:
                    st.markdown(f"- 📚 {obj}")
                else:
                    st.write(f"- {obj}")
        
            # Display teaching phases
            st.write("#### 📊 Teaching Phases")
            
            # Initialize ArtifactModal
            from components.ArtifactModal import ArtifactModal
            artifact_modal = ArtifactModal()
            
            # Display each phase
            for i, phase in enumerate(broad_plan.get("outline", [])):
                with st.expander(f"{phase['phase']} ({phase['duration']})", expanded=False):
                    if phase.get("purpose"):
                        st.write("**🎯 Purpose:**")
                        if "[REF]" in phase["purpose"]:
                            st.markdown(f"📚 {phase['purpose']}")
                        else:
                            st.write(phase["purpose"])
                    
                    if phase.get("description"):
                        st.write("**📝 Description:**")
                        st.write(phase["description"])
                    
                    # Add generate materials button
                    st.markdown("---")
                    if st.button("📦 Generate Learning Materials", key=f"add_artifact_revised_{i}"):
                        def generate_callback(params):
                            return handle_artifact_generation(params, broad_plan)
                        artifact_modal.show(
                            phase_id=str(i),
                            phase_content={
                                "phase": phase["phase"],
                                "purpose": phase.get("purpose", ""),
                                "description": phase.get("description", "")
                            },
                            generate_callback=generate_callback
                        )
                        st.rerun()
            
            # Render artifact dialog
            artifact_modal.render_dialog()
            
            st.markdown("---")
            add_download_button(broad_plan)
            
            # Add plan enhancement button
            if st.button("✏️ Revise Plan", type="primary", key="revise_improved_plan"):
                st.session_state.show_revision_dialog = True
                st.rerun()
            
            # Display learning materials
            display_learning_materials(broad_plan)
                
    except Exception as e:
        st.error(f"Error displaying improved plan: {str(e)}")
        st.write("Original plan data:")
        st.write(plan_data)
        import traceback
        st.error(f"Detailed error: {traceback.format_exc()}")

def critique_and_improve():
    """
    Critique and improve the current broad plan without using the revision dialog.
    This function uses the critique and revise chains to enhance the plan quality.
    """
    if not st.session_state.broad_plan:
        st.error("Please generate a broad plan first")
        return
        
    with st.spinner("Analyzing and improving your lesson plan..."):
        try:
            # Initialize LLMs
            llm1 = get_llm(model_name="gpt-4o-mini", temperature=0)
            llm2 = get_openrouter_llm(model_name="anthropic/claude-3.7-sonnet", temperature=0)
            
            # Create critique chain
            from backend.prompts import CRITIQUE_TEMPLATE
            from langchain.chains import LLMChain
            
            critique_chain = LLMChain(
                llm=llm1,
                prompt=CRITIQUE_TEMPLATE,
                output_key="critique"
            )
            
            # Create revise chain
            revise_chain = create_revise_plan_chain(llm2, llm2)
            
            # Extract broad plan information
            broad_plan = st.session_state.broad_plan
            
            # Parse broad_plan
            if isinstance(broad_plan, str):
                try:
                    broad_plan = json.loads(broad_plan)
                except json.JSONDecodeError as e:
                    st.error(f"Error parsing broad_plan string: {str(e)}")
                    return
            
            # Parse broad_plan_draft
            if "broad_plan_draft" in broad_plan:
                draft = broad_plan.get("broad_plan_draft")
                
                if isinstance(draft, str):
                    try:
                        if "```json" in draft:
                            json_content = draft.split("```json")[1].split("```")[0].strip()
                            broad_plan = json.loads(json_content)
                        else:
                            broad_plan = json.loads(draft)
                    except json.JSONDecodeError as e:
                        st.error(f"Error parsing broad_plan_draft string: {str(e)}")
                        return
            
            # Ensure broad_plan contains broad_plan key
            original_plan = None
            if "broad_plan" in broad_plan:
                original_plan = broad_plan["broad_plan"]
            elif "objectives" in broad_plan and "outline" in broad_plan:
                original_plan = broad_plan
                broad_plan = {"broad_plan": original_plan}
            else:
                st.error("Could not find valid lesson plan structure")
                return
            
            # Convert broad_plan to JSON string
            broad_plan_json_str = json.dumps(broad_plan, ensure_ascii=False)
            
            # Generate critique
            with st.spinner("Analyzing plan quality..."):
                try:
                    critique_result = critique_chain.invoke({
                        "broad_plan_json": broad_plan_json_str
                    })
                    
                    # Process critique_result
                    if isinstance(critique_result, str):
                        if "```json" in critique_result:
                            json_content = critique_result.split("```json")[1].split("```")[0].strip()
                            critique_result = json.loads(json_content)
                        else:
                            try:
                                critique_result = json.loads(critique_result)
                            except json.JSONDecodeError:
                                # If not valid JSON, keep as is
                                pass
                except Exception as e:
                    st.error(f"Error generating critique: {str(e)}")
                    return
            
            # Convert critique_result to JSON string
            critique_text_str = json.dumps(critique_result, ensure_ascii=False) if isinstance(critique_result, dict) else critique_result
            
            # Generate revised plan
            with st.spinner("Improving plan based on analysis..."):
                try:
                    revised_result = revise_chain.invoke({
                        "broad_plan_json": broad_plan_json_str,
                        "critique_text": critique_text_str
                    })
                    
                    # Process revised_result
                    if isinstance(revised_result, str):
                        try:
                            if "```json" in revised_result:
                                json_content = revised_result.split("```json")[1].split("```")[0].strip()
                                revised_result = json.loads(json_content)
                            else:
                                revised_result = json.loads(revised_result)
                        except json.JSONDecodeError as e:
                            st.error(f"Error parsing revised_result: {str(e)}")
                            return
                    
                    # Extract the actual revised plan content
                    actual_revised_plan = None
                    if isinstance(revised_result, dict):
                        if "revised_plan" in revised_result:
                            actual_revised_plan = revised_result["revised_plan"]
                        elif "broad_plan" in revised_result:
                            actual_revised_plan = revised_result["broad_plan"]
                        elif "objectives" in revised_result and "outline" in revised_result:
                            actual_revised_plan = revised_result
                    
                    if not actual_revised_plan:
                        st.error("Could not extract revised plan from result")
                        return
                    
                    # Create final result structure
                    final_result = {
                        "broad_plan_json": broad_plan_json_str,
                        "critique_text": critique_text_str,
                        "revised_plan": actual_revised_plan
                    }
                    
                    # Update session state
                    st.session_state.broad_plan = final_result
                    
                    # Display success message
                    st.success("Your lesson plan has been improved based on professional critique!")
                    
                    # Use st.rerun() to reload page to display improved plan
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error improving plan: {str(e)}")
                    import traceback
                    st.error(f"Detailed error: {traceback.format_exc()}")
            
        except Exception as e:
            st.error(f"Error in critique and improve process: {str(e)}")
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
    
    # Show revision dialog if needed
    if st.session_state.show_revision_dialog:
        revision_dialog()
    else:
        render_input_form()

if __name__ == "__main__":
    main() 
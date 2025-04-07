# Standard library imports
import sys
import os
import json
from pathlib import Path

import time

# Third-party imports
import streamlit as st

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Local application imports
from backend.chains import get_llm, get_openrouter_llm
from backend.chains import create_broad_plan_draft_chain
from backend.chains import create_artifact_chain

# For Teaching Styles and Instructional Strategies Info
from components.InfoSidebar import display_tips, display_teaching_styles_info

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Local application imports

# For Teaching Styles and Instructional Strategies Info

# UI text constants
UI_TEXT = {
    "title": "AI Lesson Plan Generator",
    "grade_level": "🏫 Education Level",
    "duration": "⏱️ Duration (minutes)",
    "topic": "📝 Topic",
    "teaching_style": "📖 Teaching Style",
    "learning_objectives": "🎯 Learning Objectives (Optional)",
    "requirements": "📋 Requirements (Optional)",
    "example_plan": "📄 Example Lesson Plan (Optional)",
    "generate_button": "🚀 Generate Plan",
    "generate_learning_materials": "📦 Generate Learning Materials",
    "error_missing_fields": "Please fill out all required fields. The following fields are missing: ",
    "error_missing_field": "Please fill out all required fields. The following field is missing:",
    "generating_message": "Generating lesson plan, please wait...",
    "error_prefix": "Error occurred: ",
    "plan_title": "📚 Lesson Plan",
    "objectives_title": "🎯 Learning Objectives",
    "phases_title": "📊 Teaching Phases",
    "purpose_label": "Purpose: ",
    "method_label": "Method: ",
    "requirements_label": "Requirements: ",
    "critique_button": "🔍 Analyze & Enhance with AI",
    "critique_button_info": "Receive AI-generated feedback and suggestions to improve your lesson plan.",
    "revise_button": "✏️ Edit Plan",
    "revise_button_info": "Revise the lesson plan manually or provide feedback for AI to incorporate.",
    "finalize_button": "☑️ Finalize Plan",
    "tab_names": ["📝 Create Lesson Plan", "📚 Generated Lesson Plan", "📦 Learning Materials"],
    "explanation": """Welcome to the AI Lesson Plan Generator! This tool is designed to help educators create 
customized, effective, and engaging lesson plans tailored to their specific teaching needs. 
                    
With this tool, you can: 
- 🏫 **Select the Education Level**: Choose from elementary, middle, high school, undergraduate, or graduate.
- 📝 **Specify the Topic and Duration**: Define the focus and length of your lesson.
- 📖 **Choose Teaching Styles**: Select up to three teaching styles to guide the structure of your lesson plan.
- 🎯 **Define Learning Objectives**: Ensure the lesson aligns with your educational goals.
- 📄 **Upload Reference Materials**: Provide additional context for a more personalized plan.
- 📦 **Generate Learning Materials**: Create supplementary materials such as slides, quizzes, and more.  

<br />

Please note that the following details are **required**: education level, topic, duration, and teaching style.
The example lesson plan, reference materials, learning objectives, and requirements are **optional** but can help refine the lesson plan further.
        """,
    "steps": """##### Steps to Generate a Lesson Plan:
1. 📝 **Fill Out the Form**: Provide the required information (e.g., education level, topic, duration) and any optional details (e.g., learning objectives, reference materials).
2. 🚀 **Generate the Plan**: Click **Generate Plan** to create a detailed lesson plan tailored to your inputs.
3. ✏️ **Review and Revise**: Review the generated lesson plan and make any necessary revisions. 
    - Use **Analyze & Enhance with AI** to get AI-generated improvement ideas and select the ones you want the AI to incorporate.
    - Use **Edit Plan** to manually revise the plan, or provide feedback for AI to incorporate.
    - Once satisfied, click **Finalize Plan** to lock the plan and proceed.
4. 📦 **Generate Learning Materials**: Click **Generate Learning Materials** in any teaching phase to create supplementary materials such as slides and quizzes.
5. 📥 **Download Your Plan**: Download the complete lesson plan and learning materials as a Markdown file for easy reference.

This tool leverages AI to save you time and effort in the lesson planning process, allowing you to focus on what you do best - teaching. Get started today
by filling out the form below!
        """
    ""
}

GRADE_LEVELS = [
    "Elementary School",
    "Middle School",
    "High School",
    "Undergraduate",
    "Graduate"
]

TEACHING_STYLES = [
    {"name": "Expert", "description": "A teacher-centered approach where teachers hold the knowledge and expertise that students need. Focuses on sharing knowledge, demonstrating knowledge, and providing feedback to promote learning."},
    {"name": "Formal Authority", "description": "A teacher-centered approach that focuses on lecturing and the traditional teaching style. Goals and expectations are clearly defined and communicated. Offers a well-structured learning environment. Ideal for delivering large amounts of information in a timely manner. More suited for higher-education settings and larger classrooms. May not be suitable for all students and limits student engagement."},
    {"name": "Personal Model", "description": "A teacher-centered approach that focuses on teaching with real-life and personal examples, with students observing and following directions. The teacher takes a coach or mentor role, making it a popular approach for subjects such as physical education or art. Highly hands-on method with direct observation and teachers guiding students. A key concern with this approach is the example being seen as an ideal which may result in students feeling incapable of meeting the standard."},
    {"name": "Facilitator", "description": "A student-centered approach that focuses on facilitating critical thinking and guiding students to be independent learners through activities. Emphasizes teacher-student interactions for teachers to guide and direct students towards discovery, with students encouraged to ask questions and explore options. Requires more one-on-one interaction, making it harder to implement in larger classrooms."},
    {"name": "Delegator", "description": "A student-centered approach where teachers take on more of an observer role with students working independently or in groups. Promotes collaboration between students and peer learning. Popular for practical lessons, such as science labs, or those ideal for peer feedback, such as creative writing. May not be suitable for all students, subjects, or grade levels, and requires careful management to ensure active participation from all students."}
]

BUTTON_TO_TAB = {
    UI_TEXT["generate_button"]: UI_TEXT["tab_names"][1],
    UI_TEXT["generate_learning_materials"]: UI_TEXT["tab_names"][2]
}

# Style for buttons to be next to each other (columns are limited to width of element)
FIXED_COL = """
<style class="hide">
    .element-container:has(.hide) {
        display: none;
    }
    div[data-testid="stVerticalBlock"]:has(> .element-container .horizontal-marker) {
        display: flex;
        flex-direction: row !important;
        flex-wrap: wrap;
        gap: 0.5rem;
        align-items: baseline;
    }
    div[data-testid="stVerticalBlock"]:has(> .element-container .horizontal-marker) div {
        width: max-content !important;
    }
</style>
"""


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
    # Teaching style info dialog state
    if 'show_style_info' not in st.session_state:
        st.session_state.show_style_info = False
    if 'selected_style_info' not in st.session_state:
        st.session_state.selected_style_info = None

    if 'plan' not in st.session_state:
        st.session_state.plan = None

    # Check lesson plan is finalized
    if 'finalized' not in st.session_state:
        st.session_state.finalized = False

def switch_tabs(tab_name):
    js = f"""
    <script>
        var tabContainer = window.parent.document.querySelector('.stTabs');
        var tabButtons = tabContainer.querySelectorAll('[role="tab"]');
        tabButtons.forEach(function(button) {{
            if (button.innerText.trim() === "{tab_name}") {{
                button.click();
            }}
        }});
    </script>
    """
    # Execute the JavaScript code
    st.components.v1.html(js, height=0, width=0)

def valiate_form_data(form_data):
    """
    Validate the form data, ensuring required fields are filled
    """
    missing = []
    if not form_data["style"]:
        missing.append("teaching style")
    if not form_data["duration"]:
        missing.append("duration")
    if not form_data["topic"]:
        missing.append("topic")
    return missing

def render_header():
    """
    Render the header section with explanation of the tool
    """
    st.header(UI_TEXT["title"])
    st.markdown(UI_TEXT["explanation"], unsafe_allow_html=True)
    display_tips()
    st.markdown(UI_TEXT["steps"], unsafe_allow_html=True)
    st.divider()

def render_input_form():
    """Render the lesson plan input form"""
    # Store LLM instance in session state
    if 'llm' not in st.session_state:
        st.session_state.llm = get_llm(model_name="gpt-4o", temperature=0)
    if 'broad_chain' not in st.session_state:
        st.session_state.broad_chain = create_broad_plan_draft_chain(
            st.session_state.llm)

    # Store current selected teaching style
    current_styles = st.session_state.form_data["style"] if st.session_state.form_data["style"] else [
        TEACHING_STYLES[0]["name"]]
    if not isinstance(current_styles, list):
        current_styles = [current_styles]  # Compatible with old version data

    # Start the form
    with st.form(key="lesson_plan_input"):
        # First row: Education Level and Duration
        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**{UI_TEXT['grade_level']}**")
            grade_level = st.selectbox(
                UI_TEXT["grade_level"],
                GRADE_LEVELS,
                index=GRADE_LEVELS.index(
                    st.session_state.form_data["grade_level"]) if st.session_state.form_data["grade_level"] else 4,
                label_visibility="collapsed"
            )

        with col2:
            st.write(f"**{UI_TEXT['duration']}**")
            duration = st.number_input(
                UI_TEXT["duration"],
                value=st.session_state.form_data["duration"] if st.session_state.form_data["duration"] else 60,
                label_visibility="collapsed"
            )

        # Second row: Topic takes the full width
        st.write(f"**{UI_TEXT['topic']}**")
        topic = st.text_input(
            UI_TEXT["topic"],
            value=st.session_state.form_data["topic"] if st.session_state.form_data["topic"] else "",
            placeholder="Example: Introduction to Python Programming",
            label_visibility="collapsed"
        )

        # Teaching style - multiselect
        style_names = [style["name"] for style in TEACHING_STYLES]
        st.markdown(f'**{UI_TEXT['teaching_style']}**', help="Please see the sidebar located on the right for more details on each teaching style.")
        styles = st.multiselect(
            "Teaching Styles guide the structure of your lesson plan. You can select up to (3) styles. If multiple styles are selected, the tool will incorporate features from all selected styles.",
            options=style_names,
            default=current_styles,
            max_selections=3,
        )

        # Add learning objectives with expander
        with st.expander(UI_TEXT["learning_objectives"], expanded=False):
            # Explanation and link to Bloom's Taxonomy for guidance
            st.markdown(
                        """
                        <div style="font-size: 14px; font-weight: 500; color: #31333F;">
                        Learning objectives refer to what students should be able to do after the lesson. Clearly defining your learning objectives 
                        helps guide the lesson plan and ensures that the lesson is focused and effective.
                        <br/><br/>
                        Need help defining learning objectives? Check out 
                        <a href="https://tips.uark.edu/using-blooms-taxonomy/#gsc.tab=0" target="_blank" style="color: #1a73e8; text-decoration: none;">
                            Bloom's Taxonomy
                        </a>.
                        <br/><br/>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            learning_objectives = st.text_area(
                "Enter learning objectives",
                height=100,
                value="\n".join(
                    st.session_state.form_data["objectives"]) if st.session_state.form_data["objectives"] else "",
                placeholder="Example:\n1. Write a simple Python program to print a message\n2. Understand the basic concepts of data types\n3. Apply loops to solve problems"
            )

        # Add requirements with expander
        with st.expander(UI_TEXT["requirements"], expanded=False):
            requirements = st.text_area(
                "Enter any additional requirements for the lesson below.",
                height=100,
                value="\n".join(
                    st.session_state.form_data["requirements"]) if st.session_state.form_data["requirements"] else "",
                placeholder="Example:\n- Group discussion required\n- Include a quiz at the end\n- Use a specific textbook"
            )

        # Add example lesson plan input area with expander
        with st.expander(UI_TEXT["example_plan"], expanded=False):
            example = st.text_area(
                "Enter an example lesson plan below as reference to guide the AI.",
                height=150,
                value=st.session_state.form_data["example"] if st.session_state.form_data["example"] else "",
                placeholder="You can provide a reference lesson plan example here. If left empty, default examples will be used."
            )
        
        # Add file upload component
        from components.FileUpload import FileUpload
        file_uploader = FileUpload()

        # File upload component
        uploaded_files = st.file_uploader(
            "📄 Upload Reference Materials (Optional) - Max (2) PDF Files",
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
            st.session_state.form_data["reference_files"] = [
                f.name for f in uploaded_files]

            # Display processing results
            st.success(
                f"Successfully processed {len(processed_files)} reference files")

        # Ensure submit button displays correctly
        submitted = st.form_submit_button(label=UI_TEXT["generate_button"])

    if submitted:
        # Store form data in session state
        objectives_list = [obj.strip() for obj in learning_objectives.split(
            '\n') if obj.strip()] if learning_objectives else []
        requirements_list = [req.strip() for req in requirements.split(
            '\n') if req.strip()] if requirements else []

        st.session_state.form_data.update({
            "grade_level": grade_level,
            "topic": topic,
            "duration": duration,
            "style": styles,
            "objectives": objectives_list,
            "requirements": requirements_list,
            "example": example.strip() if example else ""
        })

        # Check duration is valid whole number
        if not isinstance(duration, int) or duration <= 0:
            st.error("Please enter a duration greater than 0 minutes.")
        # Check for missing fields and display error if needed
        missing = valiate_form_data(st.session_state.form_data)
        if len(missing) > 1:
            error_message = UI_TEXT["error_missing_fields"]
            for field in missing:
                error_message += f"\n- **{field.title()}**"
            st.error(error_message)
        elif len(missing) == 1:
            st.error(f"{UI_TEXT['error_missing_field']} **{missing[0].title()}**")
        else:
            # Reset the display state
            st.session_state.show_buttons = False
            st.session_state.full_plan = None
            st.session_state.finalized = False
            
            with st.spinner(UI_TEXT["generating_message"]):
                generate_lesson_plan(
                    grade_level,
                    topic,
                    duration,
                    styles,
                    objectives_list,
                    requirements_list
                )

            # Info message in case tabs don't change
            st.success(f"Lesson plan generated successfully! Please switch to the **{UI_TEXT["tab_names"][1]}** tab to view the results.")

            # Switch active tab to plan
            switch_tabs(BUTTON_TO_TAB[UI_TEXT["generate_button"]])

def display_input_details():
    """
    Display user's submitted input details
    """
    with st.container(border=True):
        grade_level = st.session_state.form_data["grade_level"]
        topic = st.session_state.form_data["topic"]
        duration = st.session_state.form_data["duration"]
        styles = st.session_state.form_data["style"]
        objectives = st.session_state.form_data["objectives"]
        requirements = st.session_state.form_data["requirements"]

        st.write("##### 📝 Provided Lesson Plan Details")
        st.write(f"**{UI_TEXT['grade_level']}**: {grade_level}")
        st.write(f"**{UI_TEXT['topic']}**: {topic}")
        st.write(f"**{UI_TEXT['duration']}**: {duration} minutes")
        st.write(f"**{UI_TEXT['teaching_style']}**: {', '.join(styles)}")
        if st.session_state.form_data["objectives"]:
            st.write(f"**🎯 Learning Objectives**: ")
            for obj in objectives:
                st.write(f"{obj}")
        if st.session_state.form_data["requirements"]:
            st.write(f"**📋 Requirements**:")
            for req in requirements:
                st.write(f"{req}")
        
def generate_lesson_plan(grade_level, topic, duration, styles, objectives, requirements):
    """Generate the lesson plan"""
    try:
        # Initialize LLM and chains
        llm = get_llm(model_name="gpt-4o", temperature=0)
        llm2 = get_openrouter_llm(
            model_name="anthropic/claude-3.7-sonnet", temperature=0)
        broad_chain = create_broad_plan_draft_chain(llm)

        # Prepare reference document content
        reference_text = st.session_state.form_data.get(
            "reference_text", "")

        # Format objectives and requirements as proper JSON arrays
        objectives_json = json.dumps(objectives) if isinstance(
            objectives, list) else objectives
        requirements_json = json.dumps(requirements) if isinstance(
            requirements, list) else requirements

        # Convert styles list to JSON string
        styles_json = json.dumps(styles) if isinstance(
            styles, list) else json.dumps([styles])

        # Generate broad plan
        broad_result = broad_chain.invoke({
            "grade_level": grade_level,
            "topic": topic,
            "duration": duration,
            "style": styles_json,  # Pass JSON formatted multiple teaching styles
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
                    json_content = broad_result.split(
                        "```json")[1].split("```")[0].strip()
                    broad_result = json.loads(json_content)

        # Store the result and update step
        st.session_state.broad_plan = broad_result
        st.session_state.current_step = "broad_plan"
        st.session_state.show_buttons = True

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
                    quiz_data = json.loads(quiz_content) if isinstance(
                        quiz_content, str) else quiz_content

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
        return "No learning materials have been generated yet. After finalizing your lesson plan, click **{UI_TEXT['generate_learning_materials']}** in any teaching phase of your lesson plan to generate materials."

    return markdown_content


def display_learning_materials(broad_plan):
    """Display all learning materials for the course

    Args:
        broad_plan: Teaching plan containing learning materials
    """
    st.markdown("## 📚 Learning Materials")
    if not broad_plan or not broad_plan.get("outline"):
        st.info(f"No learning materials have been generated yet. After finalizing your lesson plan, click **{UI_TEXT['generate_learning_materials']}** in any teaching phase of your lesson plan to generate materials.")
        return

    def display_quiz(quiz_content):
        """Display quiz content"""
        try:
            # Parse quiz data
            quiz_data = json.loads(quiz_content) if isinstance(
                quiz_content, str) else quiz_content

            # Display quiz title
            st.markdown(f"### {quiz_data['phase_name']} - Quiz")

            # Create questions and answers tabs
            questions_tab, answers_tab = st.tabs(
                ["Questions", "Answers & Explanations"])

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
                    st.markdown(
                        f"**Correct Answer:** {answer['correct_answer']}")
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
        else: 
            with st.expander(f"{phase['phase']} ({phase['duration']})", expanded=True):

                has_materials = True

                # Use tabs if multiple materials exist
                if len(phase["artifacts"]) > 1:
                    tabs = st.tabs(
                        [f"{artifact['type'].title()}" for artifact in phase["artifacts"]])
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
                    if artifact['type'] == "quiz":
                        display_quiz(artifact["content"])
                    elif artifact['type'] == "code_practice":
                        display_code_practice(artifact["content"])
                    elif artifact['type'] == "slides":
                        display_slides(artifact["content"])

    if has_materials:
        # Add dedicated button for downloading learning materials
        st.divider()
        materials_markdown = export_learning_materials_to_markdown(broad_plan)
        st.markdown(create_download_link(materials_markdown, "learning_materials.md",
                    "📥 Download Materials as Markdown"), unsafe_allow_html=True)
    
    if not has_materials:
        st.info(f"No learning materials have been generated yet. After finalizing your lesson plan, click **{UI_TEXT['generate_learning_materials']}** in any teaching phase of your lesson plan to generate materials.")

def add_finalize_button():
    """Add finalize button to the UI"""
    st.markdown(
        """
        <style>
        .element-container:has(style){
            display: none;
        }
        #button-after {
            display: none;
        }
        .element-container:has(#button-after) {
            display: none;
        }
        .element-container:has(#button-after) + div button {
            background-color: #4CAF50;
            padding: 15px 15px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
    if st.button(f"**{UI_TEXT["finalize_button"]}**"):
        st.session_state.finalized = True
        st.rerun()

def add_undo_finalize_button():
    """Add undo finalize button to the UI"""
    if st.button("🔙 Go Back to Revising Lesson Plan"):
        st.session_state.finalized = False
        st.rerun()

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
                        json_content = draft.split(
                            "```json")[1].split("```")[0].strip()
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
                            json_content = revised_plan.split(
                                "```json")[1].split("```")[0].strip()
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
                            json_content = revised_plan.split(
                                "```json")[1].split("```")[0].strip()
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
                    # 如果plan已finalize，则自动展开所有phases
                    expanded = st.session_state.finalized
                    with st.expander(f"{phase['phase']} ({phase['duration']})", expanded=expanded):
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
                        if st.session_state.finalized:
                            st.markdown("---")
                            if st.button(UI_TEXT["generate_learning_materials"], key=f"add_artifact_{i}"):
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

                # Add buttons for plan enhancement if in revision phase
                if not st.session_state.finalized:
                    st.markdown(FIXED_COL, unsafe_allow_html=True)
                    with st.container():
                        st.markdown('<span class="hide horizontal-marker"></span>', unsafe_allow_html=True)
                        # Add critique & improve button (automatic enhancement)
                        critique_button_clicked = st.button(UI_TEXT["critique_button"])
                        st.write(UI_TEXT["critique_button_info"])
                    
                    # Handle critique button click
                    if critique_button_clicked:
                        critique_and_improve()
                    
                    st.markdown(FIXED_COL, unsafe_allow_html=True)
                    with st.container():
                        st.markdown('<span class="hide horizontal-marker"></span>', unsafe_allow_html=True)
                        # Add revise plan button (opens dialog)
                        revise_button_clicked = st.button(UI_TEXT["revise_button"])
                        st.write(UI_TEXT["revise_button_info"])
                        
                    # Handle revise button click
                    if revise_button_clicked:
                        st.session_state.show_revision_dialog = True
                        st.rerun()                    

                    # Add button to end revision phase and finalize plan
                    add_finalize_button()

                # If plan is finalized, display success message, download button, and undo finalize button
                if st.session_state.finalized:
                    st.success(f"Lesson plan finalized. Click **{UI_TEXT["generate_learning_materials"]}** as needed in any teaching phase to generate supplementary materials.")
                    add_download_button(broad_plan)
                    add_undo_finalize_button()

            # If structure is not correct, display original data
            if not broad_plan:
                st.warning("Plan structure is not as expected. Raw data:")
                st.write(plan)

            if broad_plan:
                # Store the plan in session state
                st.session_state.plan = broad_plan

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
        changes_dict = {
            change['index']: change for change in st.session_state.phase_edits['changes']}

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
        # Handle different broad_plan data structures
        broad_plan = st.session_state.broad_plan

        # Check if we have a stored plan from the improved version
        if hasattr(st.session_state, 'revision_plan_data'):
            extracted_plan = st.session_state.revision_plan_data
        else:
            # Extract plan from various possible formats
            extracted_plan = None

            # Handle string format
            if isinstance(broad_plan, str):
                try:
                    broad_plan = json.loads(broad_plan)
                except json.JSONDecodeError:
                    st.error("Could not parse plan data from string format")
                    return

            # Handle draft format
            if "broad_plan_draft" in broad_plan:
                draft = broad_plan["broad_plan_draft"]
                if isinstance(draft, str):
                    try:
                        if "```json" in draft:
                            json_content = draft.split(
                                "```json")[1].split("```")[0].strip()
                            extracted_plan = json.loads(json_content)
                        else:
                            extracted_plan = json.loads(draft)

                        if "broad_plan" in extracted_plan:
                            extracted_plan = extracted_plan["broad_plan"]
                    except json.JSONDecodeError:
                        st.error("Could not parse plan data from draft format")
                        return
                else:
                    # Draft is already parsed JSON
                    if "broad_plan" in draft:
                        extracted_plan = draft["broad_plan"]
                    else:
                        extracted_plan = draft

            # Handle critique & improve result format
            elif "revised_plan" in broad_plan:
                revised_plan = broad_plan["revised_plan"]

                if isinstance(revised_plan, str):
                    try:
                        if "```json" in revised_plan:
                            json_content = revised_plan.split(
                                "```json")[1].split("```")[0].strip()
                            revised_plan = json.loads(json_content)
                        else:
                            revised_plan = json.loads(revised_plan)
                    except json.JSONDecodeError:
                        st.error("Could not parse revised plan data")
                        return

                if "broad_plan" in revised_plan:
                    extracted_plan = revised_plan["broad_plan"]
                else:
                    extracted_plan = revised_plan

            # Handle direct plan format
            elif "broad_plan" in broad_plan:
                extracted_plan = broad_plan["broad_plan"]

            # Handle plan when it already has the right structure
            elif "objectives" in broad_plan and "outline" in broad_plan:
                extracted_plan = broad_plan

        # If we still don't have a valid plan
        if not extracted_plan or not isinstance(extracted_plan, dict) or "outline" not in extracted_plan:
            st.error("Could not extract a valid lesson plan structure")
            st.write("Current plan data:")
            st.write(broad_plan)
            return

        # Set up the revision phases
        st.session_state.revision_data['phases'] = [
            {
                'phase': phase['phase'],
                'duration': phase['duration'],
                'purpose': phase.get('purpose', ''),
                'description': phase.get('description', '')
            }
            for phase in extracted_plan.get("outline", [])
        ]

        # Store the original plan for reference
        st.session_state.phase_edits['original_plan'] = {
            'broad_plan': extracted_plan
        }

        # Store the original plan for precise revision
        st.session_state.original_plan_for_revision = extracted_plan

    # Display phases for editing
    st.markdown("### 📊 Teaching Phases")
    phases = st.session_state.revision_data['phases']
    phase_changes = []  # Track which phases have been modified

    st.info("📌 Click on any phase name or duration to modify it. If you modify the duration, please clearly state in the feedback box that you've adjusted the time allocation. For other content changes, please also specify them in the feedback box below. The system will intelligently update the lesson plan based on your input.")

    for i, phase in enumerate(phases):
        with st.container():
            st.markdown(f"#### 📝 Phase {i+1}")
            col1, col2 = st.columns([2, 1])

            # Get original phase data for comparison
            original_phase = {
                'phase': phase['phase'],
                'duration': phase['duration']
            }

            with col1:
                new_phase_name = st.text_input(
                    "Phase Name",
                    value=phase['phase'],
                    key=f"phase_name_{i}"
                )
                if new_phase_name != phase['phase']:
                    phase['phase'] = new_phase_name
                    # Mark this phase as changed
                    phase_changes.append({
                        'index': i,
                        'original': original_phase,
                        'new': {
                            'phase': new_phase_name,
                            'duration': phase['duration']
                        }
                    })

            with col2:
                new_duration = st.text_input(
                    "Duration",
                    value=phase['duration'],
                    key=f"phase_duration_{i}"
                )
                if new_duration != phase['duration']:
                    phase['duration'] = new_duration
                    # Update or add to phase changes
                    existing_change = next(
                        (c for c in phase_changes if c['index'] == i), None)
                    if existing_change:
                        existing_change['new']['duration'] = new_duration
                    else:
                        phase_changes.append({
                            'index': i,
                            'original': original_phase,
                            'new': {
                                'phase': phase['phase'],
                                'duration': new_duration
                            }
                        })

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
    st.info("📝 Provide specific revision suggestions below. For example:\n"
            "- Add more group discussion activities to Phase 4\n"
            "- Include practical exercises in Phase 2\n"
            "- Update Phase 3 purpose to emphasize critical thinking\n\n"
            "The system will automatically understand your feedback and apply it to the specified phases. No need to use complex formats - simply be clear about which phase you want to modify and how.")

    feedback = st.text_area(
        "Provide specific improvement suggestions",
        value=st.session_state.revision_data['feedback'],
        height=150,
        placeholder="Enter specific suggestions describing which phases you want to change and how..."
    )
    st.session_state.revision_data['feedback'] = feedback

    # Add buttons
    st.markdown(FIXED_COL, unsafe_allow_html=True)
    with st.container():
        st.markdown('<span class="hide horizontal-marker"></span>', unsafe_allow_html=True)
        if st.button("💾 Save & Apply"):
            # Check if there are actual changes
            if not phase_changes and not feedback.strip():
                st.warning(
                    "No changes detected. Please modify phase names, durations, or provide feedback.")
                return

            # Format the revised phases data
            revised_phases_str = ""
            if phase_changes:
                for change in phase_changes:
                    i = change['index']
                    original = change['original']
                    new = change['new']
                    revised_phases_str += f"- Phase {i+1}: Change '{original['phase']}' ({original['duration']}) to '{new['phase']}' ({new['duration']})\n"
            else:
                revised_phases_str = "No phase name or duration changes requested."

            # Get the original plan JSON
            original_plan_json = json.dumps(
                {"broad_plan": st.session_state.original_plan_for_revision},
                ensure_ascii=False
            )

            # Use precise revision chain
            with st.spinner("Making precise revisions..."):
                try:
                    # Check if feedback contains complete JSON
                    contains_json = False
                    json_content = None

                    # Try to extract JSON from feedback if it exists
                    if feedback.strip():
                        # Look for JSON pattern in feedback
                        json_start_idx = feedback.find('{')
                        json_end_idx = feedback.rfind('}')

                        if json_start_idx != -1 and json_end_idx != -1 and json_end_idx > json_start_idx:
                            potential_json = feedback[json_start_idx:json_end_idx+1]
                            try:
                                json_content = json.loads(potential_json)

                                # Validate that JSON has the expected structure
                                is_valid_structure = False
                                if isinstance(json_content, dict):
                                    # Check if the structure contains broad_plan
                                    if "broad_plan" in json_content:
                                        broad_plan = json_content["broad_plan"]
                                        if isinstance(broad_plan, dict) and "objectives" in broad_plan and "outline" in broad_plan:
                                            is_valid_structure = True

                                if is_valid_structure:
                                    contains_json = True
                                    st.info(
                                        "Detected complete lesson plan JSON in your feedback. Using it directly.")
                                else:
                                    st.warning(
                                        "Detected JSON in your feedback, but it doesn't have the required structure. JSON must contain a 'broad_plan' key with 'objectives' and 'outline'. Proceeding with AI-assisted revision.")
                                    json_content = None
                            except json.JSONDecodeError:
                                # Not a valid JSON, continue with normal processing
                                pass

                    if contains_json and json_content:
                        # Use the JSON directly from user input
                        revised_plan = json_content
                    else:
                        # Initialize LLM for precise revision
                        llm = get_openrouter_llm(
                            model_name="anthropic/claude-3.7-sonnet", temperature=0)

                        # Import the precise revision chain
                        from backend.chains import create_precise_revision_chain
                        precise_chain = create_precise_revision_chain(llm)

                        # Enhanced feedback validation
                        enhanced_feedback = feedback

                        # Generate precisely revised plan
                        revised_result = precise_chain.invoke({
                            "original_plan_json": original_plan_json,
                            "revised_phases": revised_phases_str,
                            "user_feedback": enhanced_feedback if enhanced_feedback.strip() else "No additional feedback provided."
                        })

                        # Process the result
                        if isinstance(revised_result, dict) and "precisely_revised_plan" in revised_result:
                            revised_plan = revised_result["precisely_revised_plan"]

                            # Parse if it's a string
                            if isinstance(revised_plan, str):
                                try:
                                    # Look for JSON pattern in the response
                                    json_start_idx = revised_plan.find('{')
                                    json_end_idx = revised_plan.rfind('}')

                                    if json_start_idx != -1 and json_end_idx != -1 and json_end_idx > json_start_idx:
                                        json_content = revised_plan[json_start_idx:json_end_idx+1]
                                        revised_plan = json.loads(json_content)
                                    elif "```json" in revised_plan:
                                        json_content = revised_plan.split(
                                            "```json")[1].split("```")[0].strip()
                                        revised_plan = json.loads(json_content)
                                    else:
                                        revised_plan = json.loads(revised_plan)
                                except json.JSONDecodeError as e:
                                    st.error(
                                        f"Error parsing revised plan: {str(e)}")
                                    st.error(
                                        "Please provide more specific suggestions about which phases you want to modify.")
                                    st.code(revised_plan, language="json")
                                    return
                        else:
                            st.error(
                                "Couldn't get a valid revised plan. Please provide more specific feedback.")
                            return

                    # Final validation before updating
                    if not isinstance(revised_plan, dict):
                        st.error(
                            "Invalid revision format. Expected a JSON object.")
                        return

                    # Check if we have a valid structure before proceeding
                    is_valid_structure = False
                    if "broad_plan" in revised_plan:
                        broad_plan = revised_plan["broad_plan"]
                        if isinstance(broad_plan, dict) and "objectives" in broad_plan and "outline" in broad_plan:
                            is_valid_structure = True

                    if not is_valid_structure:
                        st.error(
                            "Invalid lesson plan structure. The plan must contain a 'broad_plan' key with 'objectives' and 'outline'.")
                        st.write("Received structure:")
                        st.write(revised_plan)
                        return

                    # Update session state
                    st.session_state.broad_plan = {
                        "broad_plan_draft": json.dumps(revised_plan, ensure_ascii=False)}
                    st.session_state.show_revision_dialog = False
                    st.session_state.revision_data = {
                        'phases': [], 'feedback': ""}
                    if hasattr(st.session_state, 'revision_plan_data'):
                        delattr(st.session_state, 'revision_plan_data')
                    if hasattr(st.session_state, 'original_plan_for_revision'):
                        delattr(st.session_state, 'original_plan_for_revision')
                    st.success("Plan has been precisely revised!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error during revision: {str(e)}")
                    import traceback
                    st.error(f"Detailed error: {traceback.format_exc()}")

        if st.button("❌ Cancel"):
            st.session_state.show_revision_dialog = False
            st.session_state.revision_data = {'phases': [], 'feedback': ""}
            if hasattr(st.session_state, 'revision_plan_data'):
                delattr(st.session_state, 'revision_plan_data')
            if hasattr(st.session_state, 'original_plan_for_revision'):
                delattr(st.session_state, 'original_plan_for_revision')
            st.rerun()


def handle_artifact_generation(artifact_result, broad_plan):
    """Generate learning material based on the selected type
    
    Args:
        artifact_result: Selected artifact configuration
        broad_plan: Current teaching plan

    Returns:
        bool: Whether the generation was successful
    """
    if not artifact_result:
        return False

    try:
        # Create artifact chain
        llm = get_llm(model_name="gpt-4o", temperature=0)
        llm2 = get_openrouter_llm(
            model_name="anthropic/claude-3.7-sonnet", temperature=0)
        chain = create_artifact_chain(llm2, artifact_result["type"])

        # Prepare parameters for artifact generation
        params = {
            "phase_content": json.dumps(artifact_result["phase_content"], ensure_ascii=False),
            **artifact_result["requirements"]
        }
        
        # Add lesson objectives if generating quiz
        if artifact_result['type'] == "quiz":
            lesson_objectives = broad_plan.get("objectives", [])
            params["lesson_objectives"] = json.dumps(lesson_objectives, ensure_ascii=False)

        # Generate content
        with st.spinner(f"Generating {artifact_result['type']}..."):
            result = chain.invoke(params)

            # Process output format
            if artifact_result['type'] == "quiz":
                # Handle quiz output
                if isinstance(result, dict) and "quiz" in result:
                    artifact_content = result["quiz"]
                else:
                    artifact_content = result

                if isinstance(artifact_content, str):
                    if "```json" in artifact_content:
                        artifact_content = artifact_content.split(
                            "```json")[1].split("```")[0].strip()
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

            # Switch to learning materials tab
            switch_tabs(BUTTON_TO_TAB[UI_TEXT["generate_learning_materials"]])

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
                        json_content = draft.split(
                            "```json")[1].split("```")[0].strip()
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
                    json_content = revised_plan.split(
                        "```json")[1].split("```")[0].strip()
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
            st.header(UI_TEXT["plan_title"] + " :green[(Improved)]")

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
                    if st.session_state.finalized:
                        st.markdown("---")
                        if st.button(UI_TEXT["generate_learning_materials"], key=f"add_artifact_revised_{i}"):
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

            # Add enhancement buttons if in revision phase
            if not st.session_state.finalized:
                st.markdown(FIXED_COL, unsafe_allow_html=True)
                with st.container():
                    st.markdown('<span class="hide horizontal-marker"></span>', unsafe_allow_html=True)
                    # Add critique & improve button to enable multiple rounds of critique
                    critique_button_clicked = st.button(UI_TEXT["critique_button"], key="critique_again")
                    st.write(UI_TEXT["critique_button_info"])
                
                # Handle critique button click
                if critique_button_clicked:
                    # Store the current improved plan in a temporary variable
                    temp_plan = {"broad_plan": broad_plan}
                    # Update session state
                    st.session_state.broad_plan = temp_plan
                    # Call critique_and_improve
                    critique_and_improve()
                    
                st.markdown(FIXED_COL, unsafe_allow_html=True)
                with st.container():
                    st.markdown('<span class="hide horizontal-marker"></span>', unsafe_allow_html=True)
                    # Always show Revise Plan button regardless of critique status
                    revise_button_clicked = st.button(UI_TEXT["revise_button"], key="revise_improved_plan")
                    st.write(UI_TEXT["revise_button_info"])

                # Handle revise button click
                if revise_button_clicked:
                    # Store the current plan in session state for the revision dialog
                    st.session_state.revision_plan_data = broad_plan
                    st.session_state.show_revision_dialog = True
                    st.rerun()

                # Add button to end revision phase and finalize the plan
                if not critique_button_clicked:
                    add_finalize_button()
            
            # If plan is finalized, display success message, download button, and undo finalize button
            if st.session_state.finalized:
                st.success(f"Lesson plan finalized. Click **{UI_TEXT["generate_learning_materials"]}** as needed in any teaching phase to create supplementary materials.")
                add_download_button(broad_plan)
                add_undo_finalize_button()

    except Exception as e:
        st.error(f"Error displaying improved plan: {str(e)}")
        st.write("Original plan data:")
        st.write(plan_data)
        import traceback
        st.error(f"Detailed error: {traceback.format_exc()}")


def critique_and_improve():
    """
    Analyze the current lesson plan and display improvement suggestions for user selection.
    Instead of automatically applying all improvements, this function lets users choose
    which suggestions to apply.
    """
    if not st.session_state.broad_plan:
        st.error("Please generate a broad plan first")
        return

    with st.spinner("Analyzing your lesson plan..."):
        try:
            # Initialize LLM
            llm1 = get_llm(model_name="gpt-4o-mini", temperature=0)

            # Create critique chain
            from backend.prompts import CRITIQUE_TEMPLATE
            from langchain.chains import LLMChain

            critique_chain = LLMChain(
                llm=llm1,
                prompt=CRITIQUE_TEMPLATE,
                output_key="critique"
            )

            # Extract broad plan information based on the current structure
            broad_plan = st.session_state.broad_plan

            # Extract the actual plan for critique
            extracted_plan = None

            # Parse broad_plan if it's a string
            if isinstance(broad_plan, str):
                try:
                    broad_plan = json.loads(broad_plan)
                except json.JSONDecodeError as e:
                    st.error(f"Error parsing broad_plan string: {str(e)}")
                    return

            # Handle different plan structures

            # 1. Handle the case when broad_plan contains broad_plan_draft
            if "broad_plan_draft" in broad_plan:
                draft = broad_plan.get("broad_plan_draft")

                if isinstance(draft, str):
                    try:
                        if "```json" in draft:
                            json_content = draft.split(
                                "```json")[1].split("```")[0].strip()
                            draft_json = json.loads(json_content)
                        else:
                            draft_json = json.loads(draft)

                        if "broad_plan" in draft_json:
                            extracted_plan = {
                                "broad_plan": draft_json["broad_plan"]}
                        else:
                            extracted_plan = {"broad_plan": draft_json}
                    except json.JSONDecodeError as e:
                        st.error(
                            f"Error parsing broad_plan_draft string: {str(e)}")
                        return
                else:
                    # Already a dict
                    if "broad_plan" in draft:
                        extracted_plan = {"broad_plan": draft["broad_plan"]}
                    else:
                        extracted_plan = {"broad_plan": draft}

            # 2. Handle the case when broad_plan has a critique result
            elif "revised_plan" in broad_plan:
                revised_plan = broad_plan.get("revised_plan")

                if isinstance(revised_plan, str):
                    try:
                        if "```json" in revised_plan:
                            json_content = revised_plan.split(
                                "```json")[1].split("```")[0].strip()
                            revised_json = json.loads(json_content)
                        else:
                            revised_json = json.loads(revised_plan)

                        if "broad_plan" in revised_json:
                            extracted_plan = {
                                "broad_plan": revised_json["broad_plan"]}
                        elif "objectives" in revised_json and "outline" in revised_json:
                            extracted_plan = {"broad_plan": revised_json}
                        else:
                            extracted_plan = {"broad_plan": revised_json}
                    except json.JSONDecodeError as e:
                        st.error(
                            f"Error parsing revised_plan string: {str(e)}")
                        return
                elif isinstance(revised_plan, dict):
                    if "broad_plan" in revised_plan:
                        extracted_plan = {
                            "broad_plan": revised_plan["broad_plan"]}
                    elif "objectives" in revised_plan and "outline" in revised_plan:
                        extracted_plan = {"broad_plan": revised_plan}
                    else:
                        extracted_plan = {"broad_plan": revised_plan}

            # 3. Handle the case when broad_plan has a direct broad_plan structure
            elif "broad_plan" in broad_plan:
                extracted_plan = {"broad_plan": broad_plan["broad_plan"]}

            # 4. Handle the case when broad_plan itself is the plan
            elif "objectives" in broad_plan and "outline" in broad_plan:
                extracted_plan = {"broad_plan": broad_plan}

            # If we couldn't extract a valid plan
            if not extracted_plan:
                st.error("Could not find valid lesson plan structure")
                st.write("Current plan data:")
                st.write(broad_plan)
                return

            # Convert extracted_plan to JSON string
            broad_plan_json_str = json.dumps(
                extracted_plan, ensure_ascii=False)

            # Generate critique
            with st.spinner("Analyzing plan quality..."):
                try:
                    critique_result = critique_chain.invoke({
                        "broad_plan_json": broad_plan_json_str
                    })

                    # Process critique_result
                    critique_points = None
                    if isinstance(critique_result['critique'], str):
                        # Try to parse JSON
                        try:
                            if "```json" in critique_result['critique']:
                                json_content = critique_result['critique'].split(
                                    "```json")[1].split("```")[0].strip()
                                critique_points = json.loads(json_content)
                            else:
                                critique_points = json.loads(
                                    critique_result['critique'])
                        except json.JSONDecodeError:
                            st.error(
                                "Could not parse critique result as JSON. Please try again.")
                            return
                    else:
                        critique_points = critique_result['critique']

                    # Save broad_plan_json_str to session state for later use
                    st.session_state.critique_original_plan = broad_plan_json_str

                    # Initialize CritiqueDialog and display
                    from components.CritiqueDialog import CritiqueDialog
                    critique_dialog = CritiqueDialog()

                    # Define improvement callback function
                    def improvement_callback(selected_points):
                        apply_improvements(selected_points)

                    # Show dialog
                    critique_dialog.show(critique_points, improvement_callback)
                    # Render dialog
                    critique_dialog.render_dialog()

                except Exception as e:
                    st.error(f"Error generating critique: {str(e)}")
                    import traceback
                    st.error(f"Detailed error: {traceback.format_exc()}")

        except Exception as e:
            st.error(f"Error in critique and improve process: {str(e)}")
            import traceback
            st.error(f"Detailed error: {traceback.format_exc()}")


def apply_improvements(selected_critique_points):
    """
    Apply improvements to the lesson plan based on user-selected critique points

    Args:
        selected_critique_points: List of critique points selected by the user
    """
    if not hasattr(st.session_state, 'critique_original_plan'):
        st.error("Original plan not found. Please try the critique process again.")
        return

    broad_plan_json_str = st.session_state.critique_original_plan

    with st.spinner("Improving your lesson plan based on selected suggestions..."):
        try:
            # Initialize LLM
            llm2 = get_openrouter_llm(
                model_name="anthropic/claude-3.7-sonnet", temperature=0)

            # Create revise selected chain
            from backend.chains import create_revise_selected_plan_chain
            revise_chain = create_revise_selected_plan_chain(llm2)

            # Convert selected critique points to JSON string
            selected_critique_str = json.dumps(
                selected_critique_points, ensure_ascii=False)

            # Generate revised plan
            revised_result = revise_chain.invoke({
                "broad_plan_json": broad_plan_json_str,
                "selected_critique_points": selected_critique_str
            })

            # Process revised_result
            if isinstance(revised_result, str):
                try:
                    if "```json" in revised_result:
                        json_content = revised_result.split(
                            "```json")[1].split("```")[0].strip()
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
                "critique_text": selected_critique_str,
                "revised_plan": actual_revised_plan
            }

            # Update session state
            st.session_state.broad_plan = final_result

            # Display success message
            st.success(
                "Your lesson plan has been improved based on the selected suggestions!")

            # Use st.rerun() to reload page to display improved plan
            st.rerun()

        except Exception as e:
            st.error(f"Error improving plan: {str(e)}")
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

    # tab styling (wrap for small screens)
    st.markdown(
        """
    <style>
        .stTabs [data-baseweb="tab-list"] {
            display: flex;
            flex-wrap: wrap;
            justify-content: flex-start;
            gap: 10px;
        }

        .stTabs [data-baseweb="tab"] {
            height: 30px;
            white-space: pre-wrap;
            background-color: #F0F2F6;
            border-radius: 10px 10px 0px 0px;
            padding: 5px 10px;
        }

        .stTabs [aria-selected="true"] {
            border-bottom: 1px solid red;
        }
        .stTabs [data-baseweb="tab-highlight"] {
            display: none;
        }
    </style>
        """, unsafe_allow_html=True)

    init_session_state()

    # Header with title and explanation
    render_header()

    # Create two columns
    left_col, right_col = st.columns([2, 1])

    # Create tabs
    with left_col:
        tabs = st.tabs(UI_TEXT["tab_names"])

        # Tab 1: Form
        with tabs[0]:
            render_input_form()
        
        # Tab 2: Generated plan or revision dialog
        with tabs[1]:
            if st.session_state.show_revision_dialog:
                revision_dialog()
            elif st.session_state.broad_plan:
                # Check if this is a critique_and_improve result
                if isinstance(st.session_state.broad_plan, dict) and all(k in st.session_state.broad_plan for k in ["broad_plan_json", "critique_text", "revised_plan"]):
                    # Use specialized function to display improved plan
                    display_revised_plan(st.session_state.broad_plan)
                else:
                    # Use original function to display regular plan
                    display_broad_plan(st.session_state.broad_plan)
            else:
                st.header(UI_TEXT["plan_title"])
                st.info(f"No lesson plan has been generated yet. Please fill out the form in the **{UI_TEXT["tab_names"][0]}** tab and click **{UI_TEXT["generate_button"]}**.")

        # Tab 3: Learning materials
        with tabs[2]:
            display_learning_materials(st.session_state.plan)

    with right_col:
        # Empty space padding to line up with left column after tabs
        st.markdown(
            """
            <div style="height: 59px;"></div>
            """,
            unsafe_allow_html=True
        )

        # Display inputted details after submitting
        # Only when plan has already been generated
        if st.session_state.broad_plan:
            display_input_details()

        # Teaching styles info
        display_teaching_styles_info()

    

if __name__ == "__main__":
    main()

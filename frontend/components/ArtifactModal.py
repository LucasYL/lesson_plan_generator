import streamlit as st
from typing import Dict, Any, Optional
from frontend.app import FIXED_COL

# Define artifact types and their configurations
ARTIFACT_TYPES = {
    "quiz": {
        "name": "Quiz",
        "icon": "❓",
        "requirements": [
            "Number of questions (1-8)",
            "Difficulty level (Easy/Medium/Hard)",
            "Question types (Multiple choice/Short answer)",
            "Additional notes (Optional)"
        ]
    },
    "code_practice": {
        "name": "Code Practice",
        "icon": "💻",
        "requirements": [
            "Programming language",
            "Difficulty level (Easy/Medium/Hard)",
            "Question type:",
            "- Complete the function: Provide function structure, students implement the body",
            "- Debug the code: Provide code with bugs, students fix them",
            "- Fill in the blanks: Code with gaps, students fill in key parts",
            "Additional requirements (Optional)"
        ]
    },
    "slides": {
        "name": "Slides",
        "icon": "📊",
        "requirements": [
            "Slide style (Academic/Visual/Minimalist)",
            "Number of slides (1-10)",
            "Additional requirements (Optional)"
        ]
    }
}

class ArtifactModal:
    def __init__(self):
        """Initialize the artifact modal component"""
        if 'show_artifact_dialog' not in st.session_state:
            st.session_state.show_artifact_dialog = False
        if 'current_phase_id' not in st.session_state:
            st.session_state.current_phase_id = None
        if 'current_phase_content' not in st.session_state:
            st.session_state.current_phase_content = None
        if 'artifact_result' not in st.session_state:
            st.session_state.artifact_result = None
        if 'generate_callback' not in st.session_state:
            st.session_state.generate_callback = None
    
    def show(self, phase_id: str, phase_content: Dict[str, Any], generate_callback) -> None:
        """Show the artifact dialog
        
        Args:
            phase_id: ID of the phase to generate material for
            phase_content: Content of the phase
            generate_callback: Callback function to handle material generation
        """
        st.session_state.current_phase_id = phase_id
        st.session_state.current_phase_content = phase_content
        st.session_state.show_artifact_dialog = True
        st.session_state.generate_callback = generate_callback
        
    @st.dialog("📦 Generate Learning Material", width="large")
    def _show_dialog(self) -> None:
        """Display the learning material generation dialog"""
        if not st.session_state.show_artifact_dialog:
            return
            
        # 1. Select material type
        st.markdown("### 📋 Select Material Type")
        artifact_type = st.selectbox(
            "Material Type",
            options=["quiz", "code_practice", "slides"],
            format_func=lambda x: {
                "quiz": "Quiz / Assessment",
                "code_practice": "Coding Exercise",
                "slides": "Presentation Slides"
            }.get(x, x)
        )
        
        requirements = {}
        
        # 2. Display requirements based on type
        if artifact_type == "quiz":
            requirements["num_questions"] = st.number_input(
                "Number of questions",
                min_value=1,
                max_value=8,
                value=3
            )
            requirements["difficulty"] = st.select_slider(
                "Difficulty level",
                options=["Easy", "Medium", "Hard"]
            )
            requirements["question_type"] = st.selectbox(
                "Question type",
                options=["Multiple choice", "Short answer"]
            )
            requirements["additional_notes"] = st.text_area(
                "Additional notes (Optional)",
                placeholder="Specify any special requirements for the quiz, such as focusing on specific concepts, including visual elements, or targeting particular learning objectives."
            )
            
        elif artifact_type == "code_practice":
            requirements["programming_language"] = st.selectbox(
                "Programming language",
                options=["Python", "JavaScript", "Java", "C++", "SQL", "C", "TypeScript", "Ruby", "Swift"]
            )
            requirements["difficulty"] = st.select_slider(
                "Difficulty level",
                options=["Easy", "Medium", "Hard"]
            )
            requirements["question_type"] = st.selectbox(
                "Question type",
                options=[
                    "Complete the function",
                    "Debug the code",
                    "Fill in the blanks"
                ]
            )
            requirements["additional_requirements"] = st.text_area(
                "Additional requirements (Optional)",
                placeholder="Specify any other requirements for the coding exercise. If you need a programming language not listed above, please specify it here (e.g., 'Please use Golang instead')."
            )
        
        elif artifact_type == "slides":
            requirements["slide_style"] = st.selectbox(
                "Slide style",
                options=["Academic", "Visual", "Minimalist"]
            )
            requirements["num_slides"] = st.number_input(
                "Number of slides",
                min_value=1,
                max_value=10,
                value=3
            )
            requirements["additional_requirements"] = st.text_area(
                "Additional requirements (Optional)",
                placeholder="Specify any special requirements for the slides, such as focusing on particular concepts, including specific diagrams, or preferred presentation style details."
            )
        
        # 3. Generate and Cancel buttons
        st.markdown(FIXED_COL, unsafe_allow_html=True)
        with st.container():
            st.markdown('<span class="hide horizontal-marker"></span>', unsafe_allow_html=True)
            if st.button("✨ Generate"):
                # Generate artifact
                artifact_params = {
                    "type": artifact_type,
                    "phase_id": st.session_state.current_phase_id,
                    "phase_content": st.session_state.current_phase_content,
                    "requirements": requirements
                }
                
                # Close dialog
                st.session_state.show_artifact_dialog = False
                
                # Call generate callback
                if st.session_state.generate_callback:
                    st.session_state.generate_callback(artifact_params)
                st.rerun()
        
            if st.button("❌ Cancel"):
                st.session_state.show_artifact_dialog = False
                st.rerun()      
        
    def render_dialog(self) -> None:
        """Render the artifact dialog content"""
        if not st.session_state.show_artifact_dialog:
            return
            
        # Show dialog
        self._show_dialog() 
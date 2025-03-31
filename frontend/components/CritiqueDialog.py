import streamlit as st
import json
from typing import List, Dict, Any, Callable
from frontend.app import FIXED_COL

class CritiqueDialog:
    def __init__(self):
        """Initialize the critique dialog component"""
        if 'show_critique_dialog' not in st.session_state:
            st.session_state.show_critique_dialog = False
        if 'critique_points' not in st.session_state:
            st.session_state.critique_points = []
        if 'selected_critique_points' not in st.session_state:
            st.session_state.selected_critique_points = []
        if 'improvement_callback' not in st.session_state:
            st.session_state.improvement_callback = None
    
    def show(self, critique_points: List[Dict[str, Any]], callback: Callable) -> None:
        """Show the critique dialog
        
        Args:
            critique_points: List of critique points
            callback: Callback function to handle user selection
        """
        st.session_state.critique_points = critique_points
        st.session_state.show_critique_dialog = True
        st.session_state.improvement_callback = callback
        
        # Default to all selected
        st.session_state.selected_critique_points = [point['id'] for point in critique_points]
    
    @st.dialog("🔍 Lesson Plan Analysis", width="large")
    def _show_dialog(self) -> None:
        """Display the critique dialog content"""
        if not st.session_state.show_critique_dialog:
            return
        
        st.markdown("### 📋 We've identified the following potential improvements")
        st.markdown("Please select the suggestions you'd like to apply:")
        
        # Display each critique point
        for point in st.session_state.critique_points:
            col1, col2 = st.columns([0.1, 0.9])
            with col1:
                is_selected = st.checkbox("", value=(point['id'] in st.session_state.selected_critique_points), key=f"critique_{point['id']}")
                if is_selected and point['id'] not in st.session_state.selected_critique_points:
                    st.session_state.selected_critique_points.append(point['id'])
                elif not is_selected and point['id'] in st.session_state.selected_critique_points:
                    st.session_state.selected_critique_points.remove(point['id'])
            
            with col2:
                st.markdown(f"**Issue {point['id']}**: {point['issue']}")
                st.markdown(f"**Suggestion**: {point['suggestion']}")
                st.markdown("---")
        
        # Buttons
        st.markdown(FIXED_COL, unsafe_allow_html=True)
        with st.container():
            st.markdown('<span class="hide horizontal-marker"></span>', unsafe_allow_html=True)
            if st.button("✅ Apply Selected Improvements"):
                # Get selected critique points
                selected_points = [point for point in st.session_state.critique_points 
                                  if point['id'] in st.session_state.selected_critique_points]
                
                # Close dialog
                st.session_state.show_critique_dialog = False
                
                # Call callback function
                if st.session_state.improvement_callback and selected_points:
                    st.session_state.improvement_callback(selected_points)
                st.rerun()
        
            if st.button("❌ Cancel"):
                st.session_state.show_critique_dialog = False
                st.rerun()
    
    def render_dialog(self) -> None:
        """Render the critique dialog"""
        if not st.session_state.show_critique_dialog:
            return
        
        self._show_dialog() 
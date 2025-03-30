import streamlit as st
import json
from pathlib import Path

# Import jsons for teaching styles and instructional strategies info
base_path = Path(__file__).parent.parent / "data"
teaching_styles_path = base_path / "teaching_styles.json"
instructional_strategies_path = base_path / "instructional_strategies.json"

with open(teaching_styles_path, "r") as file:
    teaching_info = json.load(file)
with open(instructional_strategies_path, "r") as file:
    instructional_strategies = json.load(file)

def display_tips():
    """
    Displays information about creating effective lesson plans.
    """
    with st.expander("Creating Effective Lesson Plans"):
        st.write("""An effective lesson plan is a key component of successful teaching. Crafting a lesson plan provides teachers 
                 the opportunity to think through the content, activities, and assessments that will be used in a lesson. 
                 A lesson plan also serves as a roadmap for the teacher to follow and ensures that all necessary information is covered.
                 """)
        st.write("Here are some tips for creating an effective lesson plan:")
        st.write("- **Set clear objectives:** Clearly define what you want your students to learn by the end of the lesson.")
        st.write("- **Ensure lessons are logical and sequential:** Make sure that the content flows in a logical order and builds on previous knowledge.")
        st.write("- **Incorporate a variety of learning methods:** Use a mix of instructional strategies that are directly related to the learning objectives such as lectures, discussions, group work, and hands-on activities to keep students engaged and cater to different needs.")
        st.write("- **Include assessments:** Regularly assess students through various assessment methods such as quizzes, tests, and projects to allow students to practice, demonstrate their understanding, and receive targeted feedback.")
        st.write("- **Good time management:** Allocate time for each activity to ensure that the lesson stays on track. When planning, consider the time needed for transitions, explanations, and student work. While allocating time is important to ensure all content is covered, it is also important to be flexible and adjust the lesson as needed based on student understanding and engagement.")
        st.write("- **Appropriate content:** Ensure that the content is age-appropriate, relevant, and aligned with learning objectives.")

def display_teaching_styles_info():
    """
    Displays information about teaching styles.
    """
    with st.container(border=True):
      # Teaching Styles
      st.write(("##### Teaching Styles"))
      st.write(teaching_info["description"])
      st.write(f"Access to [full PDF of Grasha's Model]({teaching_info["pdf"]}).")

      # Style for list items spacing
      st.markdown(
      """
      <style>
      ul {
        margin: 0;
      }
      </style>
      """,
      unsafe_allow_html=True
      ) 

      # Show each style in a tab
      teaching_styles = [style["name"] for style in teaching_info["styles"]]
      tabs = st.tabs(teaching_styles)
      for tab, style in zip(tabs, teaching_info["styles"]):
            with tab:
                for line in style["description"]:
                    st.markdown(f"- {line}")
                st.write('\n')

### If adding instructional strategies, uncomment the following
# def display_instructional_strategies_info():
#       """
#       Displays information about instructional strategies.
#       """
#       with st.container(border=True):
#         st.subheader("Instructional Strategies")
#         st.write(instructional_strategies["description"])
#         st.write(
#             f"More information can be found [here]({instructional_strategies['link']}).")
        
#         # Show each strategy in a tab
#         strategies = [strategy["name"] for strategy in instructional_strategies["types"]]
#         tabs = st.tabs(strategies)
#         for tab, strategy in zip(tabs, instructional_strategies["types"]):
#             with tab:
#                 st.write(strategy["description"])
#                 if "examples" in strategy:
#                     st.markdown("**Examples:**")
#                     for example in strategy["examples"]:
#                         st.markdown(f"- {example}")
#                 if "more_examples_link" in strategy:
#                     st.markdown(
#                         f"[More Examples]({strategy['more_examples_link']})")

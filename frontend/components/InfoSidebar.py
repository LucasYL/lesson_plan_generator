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


def render_sidebar():
    """
    Renders the sidebar with information about teaching styles and instructional strategies.
    """
    with st.container(border=True):
      # Teaching Styles
      st.subheader("Teaching Styles")
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

      # If adding instructional strategies, uncomment the following
      # st.divider()

      # # Instructional Strategies
      # st.subheader("Instructional Strategies")
      # st.write(instructional_strategies["description"])
      # st.write(
      #     f"More information can be found [here]({instructional_strategies['link']}).")
      
      # # Show each strategy in a tab
      # strategies = [strategy["name"] for strategy in instructional_strategies["types"]]
      # tabs = st.tabs(strategies)
      # for tab, strategy in zip(tabs, instructional_strategies["types"]):
      #     with tab:
      #         st.write(strategy["description"])
      #         if "examples" in strategy:
      #             st.markdown("**Examples:**")
      #             for example in strategy["examples"]:
      #                 st.markdown(f"- {example}")
      #         if "more_examples_link" in strategy:
      #             st.markdown(
      #                 f"[More Examples]({strategy['more_examples_link']})")

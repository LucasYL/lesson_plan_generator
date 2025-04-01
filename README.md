# AI Lesson Plan Generator

<div align="center">
  <img src="https://img.shields.io/badge/AI-Powered-blue?style=for-the-badge" alt="AI Powered"/>
  <img src="https://img.shields.io/badge/Education-Tool-green?style=for-the-badge" alt="Education Tool"/>
  <img src="https://img.shields.io/badge/Smart-Workflows-orange?style=for-the-badge" alt="Smart Workflows"/>
</div>
<br>

## 📚 Overview

The AI Lesson Plan Generator is a powerful tool designed for educators to create customized, effective, and engaging lesson plans tailored to their specific teaching needs. Using advanced AI technology, it generates comprehensive lesson plans and supplementary teaching materials based on your inputs.

## ✨ Key Features

With this tool, you can:

- 🏫 **Select Education Level**: Choose from elementary, middle, high school, undergraduate, or graduate
- 📝 **Specify Topic and Duration**: Define the focus and length of your lesson
- 📖 **Choose Teaching Styles**: Select up to three teaching styles to guide the structure of your lesson plan
- 🎯 **Define Learning Objectives**: Ensure the lesson aligns with your educational goals
- 📄 **Upload Reference Materials**: Provide additional context for a more personalized plan
- 📦 **Generate Learning Materials**: Create supplementary materials such as slides, quizzes, and coding exercises

## 🚀 Usage Guide

Follow these steps to generate a lesson plan:

1. **Fill Out the Form**: Provide required information (e.g., education level, topic, duration) and any optional details (e.g., learning objectives, reference materials)
2. **Generate the Plan**: Click the **Generate Plan** button to create a detailed lesson plan tailored to your inputs
3. **Review and Revise**: 
   - Review the generated lesson plan
   - Use the **Revise Plan** button to edit manually
   - Or use the **Refine with AI** button to receive AI-generated improvement suggestions
   - Once satisfied, click **Complete Revision Phase** to finalize the plan
4. **Generate Learning Materials**: Click the **Generate Learning Materials** button in any teaching phase to create supplementary materials like slides and quizzes
5. **Download Your Plan**: Download the complete lesson plan and learning materials as a Markdown file for easy reference

## 📖 Teaching Styles

This tool supports five teaching styles that you can mix and match to suit your teaching approach:

### Expert
A teacher-centered approach where teachers hold knowledge and expertise. Focuses on sharing knowledge, demonstrating skills, and providing direct feedback to promote learning. Excels in content delivery and demonstrations.

### Formal Authority
A teacher-centered approach focused on lecturing in a structured environment, ideal for efficiently delivering large amounts of information. Excels in clarity of goals and expectations.

### Personal Model
A teacher-centered approach using real-life examples with direct observation, where the teacher acts as a coach/mentor. Excels in demonstrations and modeling behavior.

### Facilitator
A student-centered approach focused on guiding critical thinking through activities, emphasizing teacher-student interactions. Excels in fostering independent learning and discovery.

### Delegator
A student-centered approach where the teacher serves as an observer while students work independently or in groups. Excels in promoting collaboration and peer learning.

## 💻 Tech Stack

<div align="center">
  <table>
    <tr>
      <td align="center"><img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/></td>
      <td align="center"><img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit"/></td>
      <td align="center"><img src="https://img.shields.io/badge/LangChain-121212?style=for-the-badge&logo=chainlink&logoColor=white" alt="LangChain"/></td>
    </tr>
    <tr>
      <td align="center"><img src="https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI"/></td>
      <td align="center"><img src="https://img.shields.io/badge/Claude-000000?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude"/></td>
      <td align="center"><img src="https://img.shields.io/badge/PyPDF2-00A4CC?style=for-the-badge&logo=adobe&logoColor=white" alt="PyPDF2"/></td>
    </tr>
  </table>
</div>

## 📋 Tips for Creating Effective Lesson Plans

An effective lesson plan is a key component of successful teaching. Crafting a lesson plan provides teachers the opportunity to think through the content, activities, and assessments that will be used in a lesson.

Here are some tips for creating an effective lesson plan:

- **Set clear objectives**: Clearly define what you want your students to learn by the end of the lesson
- **Ensure logical sequencing**: Make sure that the content flows in a logical order and builds on previous knowledge
- **Incorporate variety**: Use a mix of instructional strategies directly related to the learning objectives to keep students engaged and cater to different needs
- **Include assessments**: Regularly assess students through various methods to allow them to practice, demonstrate understanding, and receive targeted feedback
- **Manage time effectively**: Allocate time for each activity while considering transitions, explanations, and student work
- **Choose appropriate content**: Ensure content is age-appropriate, relevant, and aligned with learning objectives

## ⚙️ Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd lesson-plan-generator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
Create a `.env` file and add the following:
```
OPENAI_API_KEY=your_api_key_here
OPEN_ROUTER_API_KEY=your_api_key_here
```

4. Run the application:
```bash
streamlit run frontend/app.py
```

## 📝 Important Notes

- Ensure a stable internet connection for the best experience
- PDF file size limit: 10MB
- Maximum 2 reference files allowed
- Complete the revision phase before generating learning materials
- All generated content can be downloaded in Markdown format

## 📄 License

MIT License 
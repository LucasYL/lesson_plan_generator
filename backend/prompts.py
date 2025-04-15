from langchain.prompts import PromptTemplate

# ==========================================
# A) BROAD PLAN (Draft Only, No Critique/Revise)
# ==========================================
BROAD_PLAN_DRAFT_TEMPLATE = PromptTemplate(
    input_variables=[
        "grade_level",
        "topic",
        "duration",
        "style",
        "learning_objectives",
        "requirements",
        "broad_plan_feedback",
        "reference_context"
    ],
    template="""
You are an expert instructional designer specializing in {grade_level} education.

INPUTS:
1. Core Parameters:
   - Topic: {topic}
   - Duration: {duration} minutes total
   - Grade Level: {grade_level}

2. Teaching Approach:
   - Selected Teaching Style(s): {style}
   
   * Understanding Teaching Styles:
     - Expert: A teacher-centered approach where teachers hold knowledge and expertise, focusing on sharing knowledge and providing direct feedback. Strong in content delivery and demonstrations.
     - Formal Authority: A teacher-centered approach focused on lecturing in a structured environment, ideal for delivering large amounts of information efficiently. Strong in clarity of goals and expectations.
     - Personal Model: A teacher-centered approach using real-life examples with direct observation, where teacher acts as a coach/mentor. Strong in demonstrations and modeling behavior.
     - Facilitator: A student-centered approach focused on guiding critical thinking through activities, emphasizing teacher-student interactions. Strong in fostering independent learning and discovery.
     - Delegator: A student-centered approach where teacher serves as an observer while students work independently or in groups. Strong in promoting collaboration and peer learning.
   
   * Blended Style Approach:
     - When multiple styles are selected, they should be integrated to create a balanced approach
     - Teacher-centered styles (Expert, Formal Authority, Personal Model) should be balanced with student-centered approaches (Facilitator, Delegator)
     - The beginning phases often utilize more structured approaches (Expert/Formal Authority)
     - The middle phases should transition to more interactive approaches (Personal Model/Facilitator)
     - The final phases can incorporate more independent work (Facilitator/Delegator)
     - Each phase should clearly reflect elements of the selected teaching styles
     - Time allocation should be balanced appropriately between teacher-led and student-centered activities based on the combination of selected styles

3. Learning Goals:
   - Objectives: {learning_objectives}
     * These are the specific outcomes students should achieve by the end of the lesson
     * Each phase should contribute to one or more of these objectives
     * All objectives must be addressed in the lesson plan
     * if there are only one or two objectives, then add more objectives that are related to the topic

4. Structural Requirements:
   - Requirements: {requirements}
     * These are specific activities or elements that must be included
     * Each requirement should be naturally integrated into appropriate phases
     * The placement should make pedagogical sense within the lesson flow

5. Additional Inputs:
   - Reference Materials: {reference_context}
   - User Feedback and Phase Structure: {broad_plan_feedback}

TASK:
1) Process Reference Materials (if provided):
   - Extract key concepts and main ideas
   - Identify important examples and case studies
   - Note key terminology and definitions
   - Map content to learning objectives
   - Ensure at least 60% of lesson content is based on references
   - Seamlessly integrate reference-based content without explicit markers
   - If there is no reference material, generate content based on best practices

2) Process User Feedback and Phase Changes:
   - User feedback has the highest priority
   - If feedback suggests removing phases:
     * Remove specified phases
     * Redistribute time to maintain total duration
   - If feedback suggests adding phases:
     * Add new phases as specified
     * Adjust time allocation accordingly
   - If feedback suggests modifying phases:
     * Apply all specified modifications
     * Maintain the exact names and durations provided
   - For any other feedback:
     * Apply suggested improvements
     * Maintain overall structure unless explicitly told to change

3) Design or Adapt Lesson Structure:
   A. If modifying existing structure:
      - First apply any structural changes from feedback
      - Then apply any phase modifications
      - Maintain exact phase names and durations as specified
      - Enhance content within fixed structure
      
   B. If creating new structure:
      - Break {duration} minutes into logical phases
      - Ensure progression toward objectives
      - Incorporate all requirements
      - Follow pedagogical sequence
      - CRITICALLY IMPORTANT: Ensure each phase reflects the selected teaching style(s)
      - If multiple styles are selected, create a balanced progression:
        * Opening phases might be more structured/teacher-led
        * Middle phases should include more guided interaction
        * Later phases can involve more student independence and application
        * The overall balance should reflect the combination of selected styles

4) Teaching Style Integration in Phases:
   - For each phase, explicitly consider how the selected teaching style(s) influence:
     * The teacher's role in the phase
     * The level of student participation
     * The types of activities and interactions
     * The delivery methods for content
     * The assessment approaches
   - When blending styles, maintain coherence by:
     * Creating clear transitions between different teaching approaches
     * Ensuring the overall flow feels natural, not disjointed
     * Maintaining alignment with the learning objectives throughout

5) Quality Check:
   - Verify all feedback has been addressed
   - Ensure phase modifications are applied exactly
   - Check alignment with objectives
   - Validate reference material usage
   - Confirm total duration matches {duration}
   - Verify that teaching phases accurately reflect the selected teaching style(s)

OUTPUT FORMAT (JSON):
{{
  "broad_plan": {{
    "objectives": [
      "Refined learning goals (should consider the reference materials)"
    ],
    "outline": [
      {{
        "phase": "Phase name (must match if specified in feedback)",
        "duration": "Duration (must match if specified in feedback)",
        "purpose": "What students will achieve in this phase",
        "description": "Detailed explanation of how this phase will unfold and how it contributes to objectives"
      }}
    ]
  }}
}}

CONSTRAINTS:
1. Reference Materials:
   * When provided, at least 60% of content must be reference-based
   * Integrate reference material seamlessly without explicit markers
   * Maintain academic level and teaching style

2. User Feedback:
   * User feedback has absolute priority
   * Apply ALL requested changes exactly as specified
   * Maintain exact phase names and durations when provided
   * Only modify structure if explicitly requested

3. Teaching Style Integration:
   * Each phase must clearly reflect the selected teaching style(s)
   * If multiple styles are selected, create a thoughtful blend that leverages the strengths of each
   * Ensure the overall lesson structure creates a coherent learning experience
   * Maintain appropriate balance between teacher-led and student-centered activities

4. Technical Requirements:
   * Output only valid JSON
   * Include all required fields
   * Ensure total duration matches {duration} minutes
"""
)


# ==========================================
# B) RVISE PLAN (Critique, Revise)
# ==========================================
CRITIQUE_TEMPLATE = PromptTemplate(
    input_variables=["broad_plan_json"],
    template="""
You are an expert educational consultant reviewing a detailed lesson plan.

### **ANALYZE THE PLAN**
{broad_plan_json}

### **EVALUATION CRITERIA**
1. Content Quality
   - Clarity of instructions
   - Alignment with learning objectives
   - Appropriateness of activities
2. Implementation
   - Time management
   - Resource utilization
   - Activity transitions
3. Student Engagement
   - Activity variety
   - Interaction opportunities
   - Learning assessment methods

### **OUTPUT FORMAT**
Your output must be a valid JSON array containing 1-7 critique points, each with the following structure:
```json
[
  {{
    "id": 1,
    "issue": "Clear description of a specific issue in the lesson plan",
    "suggestion": "Specific, actionable suggestion to address the issue"
  }},
  {{
    "id": 2,
    "issue": "Another clear issue description",
    "suggestion": "Another specific improvement suggestion"
  }}
]
```

### **REQUIREMENTS**
1. Each critique point must be specific and actionable
2. Focus on meaningful improvements that enhance the educational value
3. Provide a balanced analysis covering different aspects of the lesson plan
4. Ensure suggestions are realistic and implementable
5. NUMBER your critique points from 1 to however many you provide (1-7), no need to be 4 critique points everytime
6. If this is likely a follow-up critique after previous improvements, focus on remaining issues
7. If the plan is already high quality, it's acceptable to provide fewer critique points (as few as 1-2)
8. STRICTLY follow the JSON format specified above
9. Do NOT include any explanatory text outside the JSON structure
"""
)

# Template for revising based on user-selected critique points
REVISE_SELECTED_TEMPLATE = PromptTemplate(
    input_variables=["broad_plan_json", "selected_critique_points"],
    template="""
You are an expert instructional designer improving a lesson plan based on selected critique points.

### **1) REVIEW ORIGINAL PLAN**
{broad_plan_json}

### **2) SELECTED CRITIQUE POINTS**
{selected_critique_points}

### **3) IMPROVE THE PLAN**
Apply ONLY the selected critique points while following these rules:
1. You CAN add new phases if the selected critique points suggest the plan needs more activities
2. You CAN modify phase names and durations if the selected critique points suggest improvements
3. Improve phase purposes and descriptions based on the selected feedback
4. Enhance alignment with learning objectives
5. Address ONLY the selected critique points thoroughly
6. Do NOT make changes related to critique points that were NOT selected
7. If you make any changes to any teaching phase, please provide a brief summary of the changes that were made to that phase based on selected critique points
8. If any phases have a summary of changes from previous revisions, please update that summary to reflect the changes made in this revision or remove it if no changes were made

### **OUTPUT FORMAT (JSON)**
{{
  "broad_plan": {{
    "objectives": [
      "Improved learning objectives based on selected critique points"
    ],
    "outline": [
      {{
        "phase": "Phase name (can be modified based on selected critique)",
        "duration": "Duration (can be adjusted based on selected critique)",
        "purpose": "Enhanced purpose statement addressing selected critique points",
        "description": "Improved description with more clarity and detail", 
        "summary of changes": "Summary of changes made to this phase based on selected critique points (if applicable)"
      }}
    ]
  }}
}}

### **REQUIREMENTS**
1. Make meaningful improvements based ONLY on the selected critique points
2. Ensure the total duration still matches the original plan's total time
3. Focus on improving content quality, clarity, and student engagement
4. Output valid JSON only, no additional text
"""
)

# New template for precisely revising a lesson plan
PRECISE_REVISION_TEMPLATE = PromptTemplate(
    input_variables=["original_plan_json", "revised_phases", "user_feedback"],
    template="""
You are an expert instructional designer tasked with making precise, targeted revisions to a lesson plan.

### **ORIGINAL LESSON PLAN**
{original_plan_json}

### **USER REVISION REQUESTS**
The user has requested the following changes:

1. Phase name and duration changes:
{revised_phases}

2. Additional feedback:
{user_feedback}

### **INSTRUCTIONS FOR PRECISE REVISION**
1. Make specific changes requested by the user
2. If the user's feedback is vague (e.g., "Make Phase 4 better" or "Change Phase 2"):
   - Identify which phase(s) the user wants to modify
   - Make intelligent improvements to those phases based on teaching best practices
   - If a phase name is changed, update its purpose and description to match the new name
   - Ensure the content remains aligned with the overall learning objectives

3. If a phase is specifically mentioned in the feedback:
   - Update that phase's description and purpose to reflect requested changes
   - Make the description more detailed, clear, and actionable
   - Ensure the purpose aligns with the learning objectives
   - Update the teaching approach and activities to match the requested changes

4. For any changes to a phase's name or duration:
   - ALWAYS update the corresponding description and purpose to match the new name
   - Ensure the activities and teaching methods described are appropriate for the new duration
   - Maintain pedagogical consistency with the new phase name
   - If ONLY the duration of a phase is modified:
     * Automatically adjust the durations of other phases to maintain the total lesson time
     * Distribute time adjustments proportionally across other phases when possible
     * Prioritize preserving time for critical learning activities
     * Ensure no phase becomes too short to be effective (minimum 5-10 minutes depending on complexity)

5. Do NOT modify phases that weren't mentioned in the user feedback
6. Do NOT alter the learning objectives unless explicitly requested by the user

### **HANDLING USER FEEDBACK**
For all types of user feedback:
1. Analyze carefully to understand which phases the user wants to modify
2. For clearly specified changes, apply them exactly as requested
3. For vague feedback, make intelligent improvements to mentioned phases
4. If a phase name is changed, its description MUST be updated accordingly
5. Ensure all changes enhance the educational value of the lesson
6. If feedback contains complete JSON, use it as the basis for revision
7. When a single phase's duration is changed:
   - Calculate the time difference between original and new duration
   - Distribute this time difference across other phases proportionally
   - Document the duration adjustments clearly in your plan
8. If you make any changes to any teaching phase, please provide a brief summary of the changes that were made to that phase based on user feedback
8. If any phases have a summary of changes from previous revisions, please update that summary to reflect the changes made in this revision or remove it if no changes were made

### **OUTPUT FORMAT (JSON)**
You must return a valid JSON object with the same structure as the original plan:
{{
  "broad_plan": {{
    "objectives": [
      "Original objectives (unchanged unless explicitly requested to modify)"
    ],
    "outline": [
      {{
        "phase": "Phase name (modified if specified in request)",
        "duration": "Duration (modified if specified in request)",
        "purpose": "Purpose statement (updated for any modified phase)",
        "description": "Description (updated for any modified phase to match new phase name and content)",
        "summary of changes": "Summary of changes made to this phase based on user feedback (if applicable)"
      }},
      // Additional phases...
    ]
  }}
}}

### **CRITICAL REQUIREMENTS**
1. Your output MUST be valid JSON
2. When a phase name is changed, its description and purpose MUST be updated to match
3. Only modify phases that were mentioned in the user feedback, EXCEPT when redistributing time due to duration changes
4. Ensure the total duration matches the original plan's total time, always maintain the exact total lesson duration
5. Make all changes educationally sound and beneficial to the learning experience
6. When updating a phase's content, ensure it remains aligned with the learning objectives
7. When redistributing time due to duration changes:
   - Maintain proportional balance between phases
   - Ensure no phase becomes too short to achieve its learning purpose
   - Consider the pedagogical importance of each phase when redistributing time
   - Document any duration changes in the phase descriptions
8. ALWAYS return JUST the JSON content, nothing else (no preamble, no explanation)
9. Handle all types of user feedback gracefully - from specific changes to vague requests
"""
)


# ==========================================
# C) ARTIFACTS (Quiz and Code Practice)
# ==========================================
QUIZ_GENERATION_TEMPLATE = PromptTemplate(
    input_variables=[
        "phase_content",
        "num_questions",
        "difficulty",
        "question_type",
        "additional_notes",
        "lesson_objectives"
    ],
    template="""
You are creating a STUDENT-FOCUSED quiz for a lesson phase with the following content:
{phase_content}

Overall lesson objectives:
{lesson_objectives}

Requirements:
- Number of questions: {num_questions}
- Difficulty: {difficulty} 
- Question type: {question_type}
- Additional notes: {additional_notes}

## QUIZ GUIDELINES:
1. TARGET AUDIENCE: This quiz is EXCLUSIVELY for STUDENTS, not for teachers or instructors. Questions should directly test student understanding of concepts.

2. CONTENT FOCUS:
   - Questions must primarily relate to the current phase content provided above
   - However, ensure questions align with the overall lesson objectives
   - Test understanding of key concepts, not memorization of trivial details

3. DIFFICULTY CALIBRATION:
   - Easy: Basic recall and simple application questions accessible to all students
   - Medium: Application and analysis questions requiring deeper understanding
   - Hard: Questions involving synthesis, evaluation, or complex problem-solving

4. QUESTION STYLE BY TYPE:
   - Multiple choice: Provide one clearly correct answer and three plausible distractors
   - Short answer: Create questions that can be answered in 1-3 sentences

5. PEDAGOGICAL BEST PRACTICES:
   - Use clear, concise language appropriate for the intended grade level
   - Avoid ambiguous wording or trick questions
   - Questions should assess genuine understanding, not confuse students
   - Include a mix of lower and higher-order thinking skills (per Bloom's taxonomy)
   - For multiple choice: all options should be plausible, with only one clearly correct answer

6. QUIZ STRUCTURE REQUIREMENTS:
   - Begin with easier questions and gradually increase difficulty
   - Include visual elements or scenarios when appropriate
   - Frame questions in relevant, real-world contexts when possible
   - For multiple-choice: ensure distractors are plausible but clearly incorrect

7. EXPLANATIONS:
   - Provide detailed, educational explanations for each answer
   - Explain not just why the correct answer is right, but also why incorrect options are wrong
   - Include relevant theory or concepts in explanations to reinforce learning

Create engaging and relevant questions that test understanding of the phase content.
Focus on key concepts and learning objectives.
Provide clear explanations for the correct answers.

Output the quiz in the following JSON format:
{{
  "phase_name": "Phase name from the content",
  "quiz_data": {{
    "questions": [
      {{
        "id": 1,
        "question": "Question text here",
        "options": {{
          "A": "Option A text",
          "B": "Option B text",
          "C": "Option C text",
          "D": "Option D text"
        }}
      }}
    ],
    "answers": [
      {{
        "id": 1,
        "correct_answer": "A",
        "explanation": "Detailed explanation of why this is the correct answer and why the other options are incorrect"
      }}
    ]
  }}
}}

Requirements:
1. Output must be valid JSON
2. Each question must have:
   - Unique ID (starting from 1)
   - Clear question text
   - 4 options (A through D) for multiple choice OR clear expectations for short answer
3. Each answer must have:
   - Matching ID with its question
   - Correct answer letter (for multiple choice) or expected response elements (for short answer)
   - Detailed explanation
4. Questions should be relevant to the phase content
5. Explanations should be educational and thorough
"""
)

CODE_PRACTICE_GENERATION_TEMPLATE = PromptTemplate(
    input_variables=[
        "phase_content",
        "programming_language",
        "difficulty",
        "question_type",
        "additional_requirements"
    ],
    template="""
You are creating a coding practice exercise for a lesson phase with the following content:
{phase_content}

Requirements:
- Programming language: {programming_language}
- Difficulty: {difficulty}
- Question type: {question_type} (possible types: "complete function", "fill in the blanks", "debug")
- Additional requirements: {additional_requirements}

Format your output in the following structure:

#### Coding Exercise: [Exercise Name]
[Write a introduction that:
1. Clearly explains what the exercise is about and what students will be implementing
2. Describes the purpose of this exercise - why it's important for students to learn this concept/skill
Keep this introduction concise but informative.]

#### Starter Code
```{programming_language}
# For "complete function" type:
# Provide function signature and docstring, with TODO comments where student should implement
# Example:
# def function_name(parameters):
#     \"\"\"Docstring explaining function purpose\"\"\"
#     # TODO: Implement the function

# For "fill in the blanks" type:
# Provide mostly complete code with specific sections marked for completion
# Example:
# def function_name(parameters):
#     # Base case
#     if condition:
#         return value
#     
#     # TODO: Implement recursive case
#     # ____ your code here ____

# For "debug" type:
# Provide code with intentional bugs for students to fix
# Example:
# def function_name(parameters):
#     # This function has bugs that need to be fixed
#     result = []
#     for i in range(len(parameters) - 1):  # BUG: Incorrect range
#         # More code with bugs...
```

#### Hints
- [One concise, helpful hint that guides without giving away the solution]
- [Optional second hint if really needed]

#### Solution
```{programming_language}
# Complete, correct solution with brief comments explaining key concepts
# Make sure this solution matches the question_type:
# - For "complete function": Show the full implementation
# - For "fill in the blanks": Show the complete code with blanks filled
# - For "debug": Show the corrected code with comments explaining the fixes
```

Important notes:
1. Tailor the starter code specifically to the question_type
2. Keep all sections concise and focused
3. Ensure the solution directly addresses the learning objectives
4. Do NOT include Example or Test Cases sections
5. Make sure hints are genuinely helpful without giving away the solution
"""
)

SLIDES_GENERATION_TEMPLATE = PromptTemplate(
    input_variables=[
        "phase_content",
        "slide_style",
        "num_slides",
        "additional_requirements"
    ],
    template="""
You are a professional instructional slide designer tasked with creating slides for the following teaching phase content:
{phase_content}

Requirements:
- Slide style: {slide_style}
- Number of slides: {num_slides}
- Additional requirements: {additional_requirements}

Please output the slide content in the following structure:

### Slides: [Topic Name]

#### Slide Content

##### Slide 1: [Title - Make this engaging and clear]
**Content:**
- [Key point 1 - Keep concise but informative]
- [Key point 2 - Consider using the "what, why, how" structure]
- [Key point 3 - Include a thought-provoking question to engage students]

**Visual Elements:**
- [Suggest a specific image/diagram that would enhance understanding]
- [Describe any charts/graphs that would illustrate the concept]
- [Recommend animation sequence if applicable]

**Instructor Notes:**
[Brief guidance on delivering this slide, including key emphasis points and potential student engagement techniques]

##### Slide 2: [Title]
**Content:**
- [Key point 1]
- [Key point 2]
- [Interactive element - e.g., "Pause for a 2-minute pair discussion on..."]

**Visual Elements:**
- [Suggest specific visual that complements the content]
- [Recommend layout for optimal learning]

**Instructor Notes:**
[Concise delivery guidance including timing and transition to next slide]

// Continue based on the required number of slides...

##### Slide [N]: [Title - Make the final slide conclusive]
**Content:**
- [Summary of key points]
- [Application or next steps]
- [Call to action or reflection prompt for students]

**Visual Elements:**
- [Suggest a visual that reinforces the main takeaway]
- [Consider a memorable final image or diagram]

**Instructor Notes:**
[Brief guidance on concluding the presentation effectively]

#### Design Recommendations
- [Color scheme suggestions aligned with content mood/tone]
- [Font and typography recommendations for readability]
- [Image/chart usage recommendations with specific examples]
- [Interactive element suggestions that enhance learning]
- [Accessibility considerations]

Important notes:
1. Ensure each slide's content is concise, with each point not exceeding 1-2 lines
2. Content should directly support the specific learning objectives
3. Use clear hierarchy and visual organization
4. Naturally incorporate engagement strategies throughout (questions, activities, discussions)
5. Balance text with visual elements on each slide
6. Create a narrative flow from beginning to end
7. For each slide, suggest specific visual elements that enhance learning, not just decorative
8. Keep instructor notes brief but actionable
"""
)

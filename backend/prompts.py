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
        "broad_plan_feedback"
    ],
    template="""
You are an expert instructional designer specializing in {grade_level} education.

Below are the essential inputs for a broad lesson plan:
- **Topic**: {topic}
- **Duration**: {duration}
- **Style**: {style}
- **Learning Objectives**: {learning_objectives}
- **Requirements** (Specific elements required in phases): {requirements}  
  (e.g. "quiz", "group work", "lecture-based instruction", "hands-on coding activity", etc.)
- **User Feedback for Revision** (if any): {broad_plan_feedback}

### **TASK**
1) **SUMMARIZE INPUTS** (Do not copy verbatim):
   - Identify the **core concepts** from `{topic}`
   - Note the **time/style constraints**
   - Distill key **learning objectives**
   - Reflect **mandatory phase elements** from `requirements`
   - Integrate **relevant user feedback** `{broad_plan_feedback}`

2) **STRUCTURE A BROAD LESSON PLAN**:
   - Break `{duration}` into **logical phases**
   - Ensure each phase explicitly **covers the required elements** (`requirements`)
   - Structure **progressive skill-building** per `{style}`
   - Align with `{grade_level}` student level

3) **VALIDATE**:
   - Ensure **all required elements** are **mapped into phases**
   - Implement relevant **user feedback** `{broad_plan_feedback}`
   - Check **time distribution and logical flow**

### **OUTPUT FORMAT (Valid JSON)**
{{
  "input_summary": {{
    "core_focus": "Short summary of the main concept",
    "key_constraints": ["time", "style", "grade level"],
    "main_objectives": ["List of 3-4 key points"],
    "feedback_notes": "Concise summary of user feedback"
  }},
  "broad_plan": {{
    "objectives": ["Refined, measurable learning goals"],
    "outline": [
      {{
        "phase": "Phase name",
        "duration": "Minutes",
        "purpose": "Clear goal",
        "approach": "Teaching method",
        "required_elements": {requirements}  # Directly using the required elements
      }}
    ]
  }}
}}

### **CONSTRAINTS**
- **No direct copying of inputs**
- **Each phase must have a clear purpose**
- **Must incorporate all `requirements` and `broad_plan_feedback`**
- **Output only valid JSON, no extra text**
"""
)


# ==========================================
# B) FULL PLAN (Draft, Critique, Revise)
# ==========================================
FULL_PLAN_DRAFT_TEMPLATE = PromptTemplate(
    input_variables=["broad_plan_json"],
    template="""
You are an expert instructional designer tasked with creating a detailed lesson plan based on an approved outline.

### **1) ANALYZE THE OUTLINE**
{broad_plan_json}

### **2) DEVELOP DETAILED PLAN**
Follow these principles strictly:
1. Maintain exact phase names and time allocations from the outline
2. Expand each phase while preserving its core structure and objectives
3. Provide appropriate details based on activity type:
   - Programming Tasks: Focus on algorithm logic, key concepts, and implementation strategies
   - Group Activities: Detail facilitation methods, discussion prompts, and expected outcomes
   - Demonstrations: Specify demonstration flow and highlight critical observations
   - Theoretical Content: Structure key concepts and provide relevant examples

### **OUTPUT FORMAT (JSON)**
{{
  "full_plan": {{
    "content": [
      {{
        "phase": "Exact phase name from outline",
        "duration": "Same duration as outline",
        "activities": [
          {{
            "type": "lecture/discussion/exercise/demonstration",
            "instructions": "Detailed step-by-step instructions for conducting the activity",
            "notes": "Guidance for the instructor on managing the activity",
            "success_criteria": "Specific indicators of successful completion"
          }}
        ]
      }}
    ]
  }}
}}

### **REQUIREMENTS**
1. Phase names and durations must exactly match the outline
2. Each phase should contain 1-3 well-defined activities
3. Instructions must be specific and actionable
4. Success criteria should be measurable
5. Include practical guidance for instructors
6. Output valid JSON only, no additional text
"""
)


FULL_PLAN_CRITIQUE_TEMPLATE = PromptTemplate(
   input_variables=["full_plan_json"],
   template="""
You are an expert educational consultant reviewing a detailed lesson plan.

### **ANALYZE THE PLAN**
{full_plan_json}

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

IMPORTANT: Do NOT suggest changes to:
- Phase names or sequence
- Time allocations
- Core structure of the plan

### **OUTPUT FORMAT (JSON)**
{{
  "critique": {{
    "scores": {{
      "content_quality": {{
        "score": "1-5",
        "strengths": ["List strong points"],
        "areas_for_improvement": ["List specific areas to improve"]
      }},
      "implementation": {{
        "score": "1-5",
        "strengths": ["List strong points"],
        "areas_for_improvement": ["List specific areas to improve"]
      }},
      "engagement": {{
        "score": "1-5",
        "strengths": ["List strong points"],
        "areas_for_improvement": ["List specific areas to improve"]
      }}
    }},
    "improvement_suggestions": [
      {{
        "phase": "Exact phase name",
        "activity_type": "Type of activity to improve",
        "suggestion": "Specific, actionable improvement"
      }}
    ]
  }}
}}

### **REQUIREMENTS**
1. Maintain JSON format
2. Provide specific, actionable feedback
3. Focus on improving content within existing structure
4. Do not suggest structural changes
"""
)


FULL_PLAN_REVISE_TEMPLATE = PromptTemplate(
    input_variables=["full_plan_json", "critique_text"],
    template="""
You are an expert instructional designer improving a lesson plan based on professional critique.

### **1) REVIEW ORIGINAL PLAN**
{full_plan_json}

### **2) ANALYZE CRITIQUE**
{critique_text}

### **3) IMPROVE THE PLAN**
Apply the critique while following these rules:
1. Maintain exact phase names and durations
2. Keep the same activity types
3. Improve instructions, notes, and success criteria
4. Enhance engagement and clarity
5. Address specific critique points

### **4) GENERATE PRESENTATION SLIDES**
Create a slide outline that:
1. Follows the phase structure exactly
2. Includes key content from each phase
3. Provides clear speaker notes for delivery
4. Uses concise bullet points for main ideas

### **OUTPUT FORMAT (JSON)**
{{
  "full_plan": {{
    "content": [
      {{
        "phase": "Exact phase name from original",
        "duration": "Same duration as original",
        "activities": [
          {{
            "type": "Same type as original",
            "instructions": "Improved step-by-step instructions",
            "notes": "Enhanced guidance for instructor",
            "success_criteria": "Refined success indicators",
          }}
        ]
      }}
    ]
  }},
  "slides": [
    {{
      "number": "Slide number (starting from 1)",
      "title": "Clear, concise slide title",
      "bullet_points": [
        "Key points from the phase content",
        "Important concepts or steps",
        "Relevant examples or activities"
      ],
      "speaker_notes": "notes for instructor delivery"
    }}
  ]
}}

### **REQUIREMENTS**
1. Preserve all phase names and durations exactly
2. Maintain activity types within each phase
3. Focus improvements on content and clarity
4. Address critique points without structural changes
5. Ensure slides align with phase content
6. Output valid JSON only
"""
)


# Define your default example. If no user-provided example is available,
# this default will be used to guide the output.
default_example = """
## Total Duration: 90 Minutes

## Agenda
1. Arrays & Pointer Basics in C (20 min)
2. Visualizing Pointer Arithmetic (15 min)
3. Break (5 min)
4. Bubble Sort: Group Simulation (20 min)
5. Selection Sort: Whiteboarding Exercise (20 min)
6. Wrap-up & Quick Reflection (10 min)

### 1. Arrays & Pointer Basics in C (20 min)
- **Overview**: Explain how arrays are stored, pointer notation, and the concept of `arr[i]` vs `*(ptr + i)`.
- **Activity**: Provide a short code snippet for students to compile. Have them predict pointer addresses.

### 2. Visualizing Pointer Arithmetic (15 min)
- **Tool**: Use [Pythontutor](https://pythontutor.com) or a similar online tool to step through code.
- **Objective**: Show how pointers increment in memory, clarifying how element addresses differ by 4 bytes (for `int`).

### 3. Bubble Sort: Group Simulation (20 min)
- **Setup**: 6 students represent array elements with numbers on index cards. Two more students track comparisons & swaps.
- **Process**: Step through bubble sort passes physically. Each pass, compare adjacent pairs, swap if out of order.
- **Debrief**: Count total swaps, discuss best vs worst case time complexity.

### 4. Selection Sort: Whiteboarding Exercise (20 min)
- **Groups**: Students draw arrays on a small whiteboard.
- **Task**: Step through selection sort, marking the minimum each time, then swapping.
- **Debrief**: Compare with bubble sort. Note the differences in swap frequency.

### 5. Wrap-up & Quick Reflection (10 min)
- **Reflection**: Students write down 2 key takeaways about pointers & 2 about sorting.
- **Optional Check**: If time allows, do a quick question: "Which scenario is bubble sort more efficient than selection sort?" (Trick question: typically they share O(n^2), but details matter.)

"""

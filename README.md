# AI Lesson Plan Generator

An intelligent lesson plan generator powered by AI that helps teachers create professional teaching plans efficiently.

## Features

- 🎯 Automatically generate course outlines and detailed teaching plans
- 📚 Support multiple teaching styles (Lecture-based, Interactive, Practice-oriented, Blended)
- 🎓 Suitable for all education levels (Elementary to Graduate)
- 💡 Smart quiz and coding practice generation
- 📝 Plan revision and feedback support
- 📄 PDF reference material upload support

## Tech Stack

- Python
- Streamlit
- LangChain
- OpenAI GPT-4
- PyPDF2

## Installation

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

## Usage Guide

1. Enter Basic Information:
   - Select education level
   - Input course topic
   - Set course duration
   - Choose teaching style

2. Optional Configuration:
   - Add learning objectives
   - Set specific requirements
   - Upload reference materials
   - Provide example lesson plans

3. Generate and Modify:
   - Generate lesson plan
   - Create learning materials for each teaching phase
   - Revise and refine plan as needed

## Important Notes

- Ensure stable internet connection
- Keep API keys secure
- PDF file size limit: 10MB
- Maximum 2 reference files allowed

## License

MIT License 
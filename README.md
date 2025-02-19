# AI Lesson Plan Generator

An intelligent application that generates detailed lesson plans using AI. Built with Streamlit and powered by advanced language models.

## Features

- Generate comprehensive lesson plans for various education levels
- Interactive UI for inputting lesson requirements
- Support for different teaching styles
- Detailed activity breakdowns with instructions and success criteria
- Optional presentation slides generation

## Installation

1. Clone the repository:
```bash
git clone https://github.com/LucasYL/lesson_plan_generator.git
cd lesson_plan_generator
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

## Usage

Run the application locally:
```bash
streamlit run frontend/app.py
```

## Environment Variables

Create a `.env` file with the following variables:
```
OPENAI_API_KEY=your_openai_api_key
OPEN_ROUTER_API_KEY=your_openrouter_api_key
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/) 
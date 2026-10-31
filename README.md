# WorldWise – AI-Powered Travel Safety and Destination Guide

WorldWise is an AI-powered travel guide designed to help users explore countries and cities, discover travel destinations, and learn about destination safety. The application combines a curated dataset, real destination photographs from Wikimedia Commons, and an AI-powered briefing and conversational assistant.

The project demonstrates how artificial intelligence, data management, software architecture, and web technologies can be integrated into a practical travel information platform.

## Features

- **Destination Explorer:** Browse information about countries and cities using a curated dataset.
- **Travel Safety Information:** Explore destination safety information and editorial safety classifications.
- **AI-Powered Travel Briefings:** Generate destination briefings using an AI language model.
- **Follow-Up AI Chat:** Ask additional questions about destinations and travel information.
- **Destination Photography:** Display real photographs sourced from Wikimedia Commons, with image credits.
- **Interactive Globe:** Explore destinations through an interactive globe interface.
- **Structured Dataset:** Use JSON and CSV files containing information about 23 destinations.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend development |
| FastAPI | Backend API and web framework |
| HTML5 | Web page structure |
| CSS3 | Styling and responsive layout |
| JavaScript | Frontend functionality and interactivity |
| Anthropic API | AI-powered travel briefings and chat |
| Wikimedia Commons | Destination photographs |
| JSON and CSV | Destination data storage |

## Project Architecture

The application follows a modular architecture that separates the frontend, backend, data management, and external service integrations.

```text
worldwise/
│
├── main.py
│   └── Backend routes and API endpoints
│
├── services.py
│   └── Dataset repository, photo provider,
│       AI adapter, and briefing services
│
├── dataset.json
├── dataset.csv
│   └── Curated destination dataset
│
├── static/
│   ├── index.html
│   │   └── Main web page
│   │
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       ├── app.js
│       ├── chat.js
│       ├── dataset.js
│       ├── gallery.js
│       ├── globe.js
│       ├── ui.js
│       └── utils.js
│
├── docs/
│   └── EXPLANATION.md
│
├── requirements.txt
└── README.md
```

## Software Design Patterns

The project uses modular software design principles and several design patterns:

- **Repository Pattern:** Separates destination data access from application logic.
- **Adapter Pattern:** Provides an integration layer for external services such as the AI provider and image provider.
- **Strategy Pattern:** Supports interchangeable service implementations.
- **Dependency Injection:** Helps separate service dependencies from application routes.
- **Separation of Concerns:** Divides the application into frontend, backend, data, and service components.

For a more detailed explanation of the architecture, design patterns, and application workflow, see [`docs/EXPLANATION.md`](docs/EXPLANATION.md).

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/maftuna-coder/worldwise-travel-guide.git
cd worldwise-travel-guide
```

### 2. Create a virtual environment

**Windows:**

```powershell
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Anthropic API key

The AI functionality requires an Anthropic API key.

You can obtain an API key from the [Anthropic Console](https://console.anthropic.com/).

Set the API key as an environment variable.

**Windows PowerShell:**

```powershell
$env:ANTHROPIC_API_KEY="your_actual_api_key"
```

**Windows Command Prompt:**

```cmd
set ANTHROPIC_API_KEY=your_actual_api_key
```

**macOS / Linux:**

```bash
export ANTHROPIC_API_KEY="your_actual_api_key"
```

Replace `your_actual_api_key` with your own API key.

### 5. Start the application

```bash
uvicorn main:app --reload
```

### 6. Open the application

Open the following address in your browser:

```text
http://127.0.0.1:8000
```

## Dataset

WorldWise uses a curated dataset containing information about 23 destinations.

The project includes two dataset formats:

- `dataset.json` – JSON representation of destination information.
- `dataset.csv` – CSV representation of the same dataset.

The dataset supports destination exploration and provides information used by the application's travel guidance features.

**Note:** Safety classifications are editorial estimates intended for informational purposes. They should not be treated as official government travel advisories or guarantees of personal safety.

## External Services

### Anthropic API

The application uses the Anthropic API for AI-powered travel briefings and follow-up questions.

An API key must be configured through the `ANTHROPIC_API_KEY` environment variable before using AI functionality.

### Wikimedia Commons

Destination photographs are sourced from Wikimedia Commons. Image credits and attribution information should be retained where required by the original image licenses.

## Deployment

The frontend can be hosted on a static hosting platform such as Netlify.

The Python FastAPI backend requires a separate Python-compatible hosting environment or an appropriate serverless deployment.

For a fully functional deployed application, configure the backend URL and securely set the required API key in the backend hosting provider's environment variables.

## Security

- Never upload API keys, passwords, or private credentials to GitHub.
- Do not commit `.env` files containing secrets.
- Store API keys in environment variables or secure hosting configuration.
- Keep virtual environments and other unnecessary local files out of the repository.
- Do not expose private credentials in frontend JavaScript or HTML files.

## Limitations and Future Improvements

Potential future improvements include:

- Expanding the destination dataset.
- Adding more detailed travel safety information.
- Improving AI-generated recommendations.
- Integrating official travel advisories.
- Adding user preferences and personalized travel planning.
- Improving automated testing and backend deployment.
- Supporting additional languages.

## Academic Project Information

**Project:** WorldWise – AI-Powered Travel Safety and Destination Guide

**Course:** Software Design in Intelligent Systems

**Student:** Maftuna Sharabbayeva

**University:** Muhammad al-Khwarizmi Tashkent University of Information Technologies

## License

This project was developed for educational and academic purposes.

Please respect the original licenses and attribution requirements of third-party photographs, libraries, and external services used in this project.

# AI-Powered Mental Wellness Assistant for Women

An intelligent system that provides personalized mental wellness support through emotion detection and activity recommendations.

## Overview

This project implements an AI-powered mental wellness assistant specifically designed for women. The system uses natural language processing to detect emotions from user journal entries and provides personalized mindfulness activities and recommendations.

## Features

- Emotion detection from journal entries using fine-tuned DistilBERT
- Personalized activity recommendations based on detected emotions
- Interactive chat/journal interface
- Mood tracking dashboard
- Secure and private data handling

## Tech Stack

- **Backend**: FastAPI, Python 3.9+
- **Frontend**: ReactJS, Material-UI
- **ML**: PyTorch, Hugging Face Transformers
- **Infrastructure**: Docker, Kubernetes
- **Monitoring**: Prometheus, Grafana

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 16+
- Docker and Docker Compose
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-mental-wellness-assistant.git
cd ai-mental-wellness-assistant
```

2. Set up the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up the frontend:
```bash
cd frontend
npm install
```

4. Start the development environment:
```bash
docker-compose up
```

## Project Structure

```
ai-mental-wellness-assistant/
├── data/                   # Raw and processed datasets
├── notebooks/              # Exploratory EDA and model prototyping
├── models/                 # Trained emotion detection models
├── backend/               # FastAPI services
├── frontend/              # ReactJS application
├── docker/                # Docker configuration
├── scripts/               # Utility scripts
└── docs/                  # Documentation
```

## Development

- Backend API documentation is available at `http://localhost:8000/docs`
- Frontend development server runs at `http://localhost:3000`

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- GoEmotions dataset
- EmotionStimulus dataset
- Hugging Face Transformers library 

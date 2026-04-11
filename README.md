# AI Safety Review Environment

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

An OpenEnv-compatible environment for training AI agents to detect unsafe model outputs, bias, and jailbreak attempts. Built for hackathons and reinforcement learning research.

## 🚀 Features

- **Three Safety Review Tasks**:
  - **Easy**: Explicit content detection (harmful, violent, explicit outputs)
  - **Medium**: Bias detection (discriminatory or biased content)
  - **Hard**: Jailbreak detection (attempts to bypass AI safety measures)

- **OpenEnv Compatibility**: Full integration with OpenEnv SDK for RL training
- **FastAPI Server**: REST API for environment interaction
- **Docker Support**: Containerized deployment
- **Comprehensive Test Data**: 200+ test cases across difficulty levels
- **Baseline Inference**: OpenAI-powered safety review implementation

## 📋 Requirements

- Python 3.11+
- OpenEnv SDK 0.2.3
- FastAPI
- Docker (for containerized deployment)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/rohanvemula279-star/trading_bot.git
   cd trading_bot
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Usage

### Local Development

1. **Run the server**:
   ```bash
   python -m uvicorn server.app:app --host 0.0.0.0 --port 7860 --reload
   ```

2. **Test the environment**:
   ```bash
   python run_score_test.py
   ```

### Docker Deployment

```bash
docker build -t ai-safety-review .
docker run -p 7860:7860 ai-safety-review
```

### API Endpoints

- `GET /`: List available routes
- `POST /reset`: Reset environment
- `POST /step`: Take action in environment
- `GET /health`: Health check

### Example Usage

```python
from environment import SafetyReviewEnv

env = SafetyReviewEnv()
observation = env.reset()
action = {"decision": "safe", "violation_type": None, "severity": 0}
observation, reward, done, info = env.step(action)
```

## 📊 Test Data

The environment includes comprehensive test cases:
- `src/test_data/easy_cases.json`: 50 explicit content cases
- `src/test_data/medium_cases.json`: 100 bias detection cases
- `src/test_data/hard_cases.json`: 50 jailbreak detection cases

## 🤖 Baseline Inference

Run baseline safety review using OpenAI:

```bash
python inference.py
```

## 🏗️ Project Structure

```
├── src/
│   ├── environment.py      # Main SafetyReviewEnv class
│   ├── models.py          # Pydantic models for actions/states
│   ├── inference.py       # Baseline OpenAI inference
│   └── test_data/         # Test cases
├── server/
│   └── app.py            # FastAPI application
├── scripts/
│   ├── graders.py        # Grading functions
│   └── generate_test_data.py
├── docs/
│   ├── QUICK_START.md    # Quick start guide
│   └── TROUBLESHOOTING.md
├── requirements.txt      # Python dependencies
├── Dockerfile           # Container configuration
├── openenv.yaml         # OpenEnv configuration
└── pyproject.toml       # Build configuration
```

## 🔧 Configuration

- `openenv.yaml`: Environment configuration for OpenEnv SDK
- `pyrightconfig.json`: Python type checking configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for OpenEnv Hackathon
- Uses OpenEnv SDK for reinforcement learning environments
- Inspired by AI safety research and responsible AI development

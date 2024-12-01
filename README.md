# SmartSync Lighting 🎵💡

## Overview

SmartSync Lighting is an innovative project that synchronizes your smart home lighting with your music, creating an immersive audiovisual experience across multiple smart home platforms.

## Features

- 🎵 Spotify Track Detection
- 🌈 Dynamic Color Extraction
- 🏠 Multi-Platform Smart Home Integration
  - SmartThings
  - Philips Hue (Planned)
  - LIFX (Planned)
  - Govee (Planned)

## Prerequisites

- Python 3.9+
- Spotify Developer Account
- Smart Home Platform Credentials

## Setup
For detailed setup instructions, see [SETUP.md](SETUP.md).

## Setup
For detailed setup instructions, see [SETUP.md](SETUP.md).

### Clone the Repository

```bash
git clone https://github.com/bananz0/SmartSync-Lighting.git
cd SmartSync-Lighting
```

### Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configuration

1. Copy `.env.example` to `.env`
2. Fill in your credentials:
   - Spotify API Keys
   - Smart Home Platform Tokens

```bash
cp .env.example .env
nano .env  # or use your preferred text editor
```

## Usage

### Running the Application

```bash
python src/main.py
```

## Development

### Running Tests

```bash
pytest tests/
```

### Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Architecture

```
[Spotify Data Source]
         ↓
[Universal Lighting Controller]
         ↓
[Platform-Specific Adapters]
```

## Roadmap

- [ ] SmartThings Integration
- [ ] Philips Hue Support
- [ ] Advanced Color Extraction
- [ ] Machine Learning Color Prediction
- [ ] Additional Platform Support

## Performance Considerations

- Async endpoint updates
- Caching mechanisms
- Optional C++ extensions for processing

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact


Project Link: [https://github.com/bananz0/SmartSync-Lighting](https://github.com/bananz0/SmartSync-Lighting)
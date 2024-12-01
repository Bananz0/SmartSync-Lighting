# Setup Guide for SmartSync Lighting

## 1. Prerequisites

Before you begin, ensure you have the following:

- **Python**: Version 3.9+ installed
- **Spotify Developer Account**: For API keys to enable Spotify integration
- **Smart Home Platform Credentials**: Such as SmartThings or other supported platforms

## 2. Installation

### Clone the Repository

Clone the project to your local machine:

```bash
git clone https://github.com/bananz0/SmartSync-Lighting.git
cd SmartSync-Lighting
```

### Create a Virtual Environment

It's recommended to use a virtual environment to manage dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### Install Dependencies

Install all required libraries using pip:

```bash
pip install -r requirements.txt
```

## 3. Configuration

### Copy and Update Environment Variables

Copy the example `.env.example` file:

```bash
cp .env.example .env
```

Open the `.env` file in your preferred editor and add the required credentials:

#### Spotify API Keys
- `SPOTIPY_CLIENT_ID`
- `SPOTIPY_CLIENT_SECRET`

#### SmartThings Access Token (optional)
- `SMARTTHINGS_ACCESS_TOKEN`

### How to Obtain SmartThings Token

If you plan to use SmartThings integration:

1. **Create a SmartThings Developer Account**:
   - Visit [SmartThings Developer Portal](https://smartthings.developer.samsung.com/) and log in

2. **Generate a Personal Access Token**:
   - Go to the Personal Access Tokens page
   - Create a token with the following scopes:
     - `r:devices` (read devices)
     - `x:devices` (control devices)
   - Save the token securely

3. **Add to .env**:
   ```bash
   SMARTTHINGS_ACCESS_TOKEN=your-token-here
   ```

## 4. Running the Application

To start the application:

```bash
python src/main.py
```

## 5. Testing

### Running Tests

Run tests to ensure the project works as expected:

```bash
pytest tests/
```

## 6. Contributing

If you'd like to contribute:

1. Fork the repository
2. Create your feature branch:
   ```bash
   git checkout -b feature/YourFeatureName
   ```
3. Commit your changes:
   ```bash
   git commit -m 'Add YourFeatureName'
   ```
4. Push to the branch:
   ```bash
   git push origin feature/YourFeatureName
   ```
5. Open a Pull Request

## 7. Troubleshooting

### Common Issues

#### Missing Environment Variables
- Ensure all required variables are added to `.env`

#### Invalid SmartThings Token
- Double-check the token's scopes and test it with curl:
  ```bash
  curl -X GET https://api.smartthings.com/v1/devices \
  -H "Authorization: Bearer your-generated-token"
  ```

#### Spotify Authentication Errors
- Verify your `SPOTIPY_CLIENT_ID` and `SPOTIPY_CLIENT_SECRET`

## References

- [SmartThings Developer Portal](https://smartthings.developer.samsung.com/)
- [Spotify Developer Documentation](https://developer.spotify.com/documentation/)
# KptncookExporter

A Python application that exports all your favorite recipes from [kptncook.com](https://kptncook.com) as beautifully formatted PDF files.

## Features

- 🔐 Secure authentication with kptncook.com
- 📋 Retrieves all your favorite recipes
- 🇩🇪 German language support for recipes
- 📄 Generates individual PDF files for each recipe
- 📸 Includes step-by-step images in PDFs
- 📏 Automatically scales ingredients for 2 portions
- 🔢 Smart fraction formatting (e.g., "1/2" instead of "0.5")
- 📖 Professional PDF layout with German headings

## Prerequisites

- Python 3.8+
- A kptncook.com account with favorite recipes

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd kc
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your kptncook.com credentials:
```
KPTNCOOK_EMAIL=your-email@example.com
KPTNCOOK_PASSWORD=your-password
KPTNCOOK_API_KEY=your-api-key-here
```

**Note:** To find the API key, search for "kptncook api key" on GitHub. You'll need to find the correct key value from public repositories or reverse engineering resources.

## Usage

1. Activate the virtual environment:
```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Run the exporter:
```bash
python main.py
```

The application will:
- Authenticate with kptncook.com
- Retrieve all your favorite recipes
- Download recipe images
- Generate PDF files for each recipe in the current directory

## Output

Each recipe PDF contains:
- Recipe title and metadata (type, prep time, cook time, description, recipe ID)
- Complete ingredient list (scaled for 2 portions)
- Step-by-step instructions with images
- Professional formatting with German headings

## Project Structure

```
kc/
├── main.py              # Main application entry point
├── auth.py              # Authentication handling
├── api_client.py        # API client for kptncook.com
├── recipe.py            # Recipe data models
├── image_downloader.py  # Image downloading and caching
├── pdf_generator.py     # PDF generation with formatting
├── requirements.txt     # Python dependencies
└── .env.example         # Environment configuration template
```

## Dependencies

- `requests` - HTTP client for API communication
- `reportlab` - PDF generation
- `Pillow` - Image processing
- `python-dotenv` - Environment variable management

## API Endpoints Used

This tool uses the following kptncook.com API endpoints:
- Authentication: `POST /auth/login`
- Favorites: `GET /favorites`
- Recipe search: `POST /recipes/search` (with German language support)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

This tool is for personal use only. Please respect kptncook.com's terms of service and only export recipes that you have legitimately favorited on the platform.
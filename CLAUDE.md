# Goal

I'd like to write a Python application that exports all my recipes from ktpncook.

Each recipe should be written to a separate PDF file. It should include:
    - the title
    - all ingredients
    - all necessary steps and times in the correct order
    - each step contains what how much from the ingredients should be used

Also, the PDF recipes should contain all relevant pictures of each step.

# How to achieve it

Use the kptncook API. I prepared for you a HTTP script which demonstrates how to use the API:

```
### Authentication

POST https://api.production.kptncook.com/auth/login
Content-Type: application/json
kptnkey: YOUR_API_KEY_HERE

{
  "email": "name@email.net",
  "password": "..."
}

> {% client.global.set("accessToken", response.body.accessToken) %}

### Favorites Retrieval

GET https://api.production.kptncook.com/favorites
Token: {{accessToken}}

### Recipe Search (use identifier from favorites)

POST https://api.production.kptncook.com/recipes/search?kptnkey=YOUR_API_KEY_HERE
Content-Type: application/json
Token: {{accessToken}}

[
    {
        "identifier": "5a7c6c133e0000a013a5d768"
    }
]
```

You decide how the python application is structured and what packages to use. I strongly recommend using external libraries or tools for PDF processing.

Ask me whenever you need anything.

# Debugging the API

Use httpie (command: http) to debug the API and understand how reponses look like

# Running the application

There is a virtual environment which you can use: .venv - just source it.

# Implementation Steps

1. **Project Setup** - Install Python dependencies for HTTP requests, PDF generation (reportlab/fpdf), and image processing
2. **API Integration** - Implement authentication, favorites retrieval, and detailed recipe fetching using the endpoints provided
3. **Content Processing** - Download recipe images and structure the data (ingredients, steps, times)
4. **PDF Generation** - Create formatted PDFs with recipe content and step images
5. **Application Logic** - Main loop to process all favorites and handle errors

# Status

We are done! There might be some minor bugs to fix though...
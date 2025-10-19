---
title: TutorBee Assistant
emoji: 🐝
colorFrom: yellow
colorTo: pink
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: mit
---

# TutorBee - Smart Business Agent

An AI-powered chatbot that represents TutorBee, an interactive tutoring service.

## Features

- 💬 **Answer Questions**: Provides information about TutorBee services, team, and features
- 📝 **Collect Leads**: Automatically captures customer contact information
- 💡 **Record Feedback**: Logs unanswered questions for continuous improvement
- 🎯 **Business-Grounded**: Only answers from actual business documentation

## How to Use

1. Enter your OpenAI API key in the input field
2. Click "Initialize Agent" to start the chatbot
3. Start chatting in the Chat tab
4. View collected leads and feedback in the Analytics tab

## Technology Stack

- **AI Model**: OpenAI GPT-4o-mini with function calling
- **Framework**: Gradio for the web interface
- **Tools**: Custom Python functions for lead collection and feedback recording

## Project Structure

```
.
├── app.py                     # Main application file
├── requirements.txt           # Python dependencies
├── me/
│   ├── business_summary.txt   # Business information (text)
│   └── about_business.pdf     # Business information (PDF)
└── README.md                  # This file
```

## Local Development

```bash
pip install -r requirements.txt
python app.py
```

## Deployment

This app is designed to run on HuggingFace Spaces. Simply:
1. Create a new Space on HuggingFace
2. Upload all files including the `me/` folder
3. The app will automatically deploy!

## Note

You'll need to provide your own OpenAI API key to use this chatbot.

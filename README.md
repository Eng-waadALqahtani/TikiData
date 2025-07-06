# Sports Coach Assistant System

A comprehensive coaching assistant system that supports both football (soccer) and basketball analytics. The system provides team statistics, match predictions, opponent analysis, lineup recommendations, and an AI chatbot assistant.

## Features

### For Both Sports
- Interactive dashboard with team statistics
- Game predictions with detailed explanations
- Opponent analysis and strategic recommendations
- Lineup/formation recommendations
- Game reports with detailed analysis
- AI chatbot assistant for coaching questions

### Football (Soccer) Features
- Uses match_data.json for team statistics, game reports, lineup, and game strategy
- Uses RapidAPI Football API for next game prediction and opponent analysis
- Arabic interface designed for Al Hilal team
- Football-specific analytics and visualizations
- Football field visualization for formations

### Basketball Features
- Uses NYK-JAN.json for team statistics, game reports, lineup, and game strategy
- Uses RapidAPI Basketball API for next game prediction and opponent analysis
- English interface designed for New York Knicks
- Basketball-specific analytics and visualizations
- Basketball court visualization for lineups

## Installation

1. Make sure you have Python 3.6+ installed on your system
2. Download all the files to a directory on your computer
3. Make the run script executable:
   ```
   chmod +x updated_run.sh
   ```
4. Run the script:
   ```
   ./updated_run.sh
   ```

## System Requirements

- Python 3.6 or higher
- Internet connection (for OpenAI API and RapidAPI calls)
- Modern web browser (Chrome, Firefox, Safari, or Edge)
- 2GB RAM minimum
- 500MB free disk space

## Files Included

- `updated_unified_app.py` - The main application backend with API integrations
- `football_frontend.html` - Football interface
- `basketball_frontend.html` - Basketball interface
- `landing_page.html` - Main entry point
- `updated_run.sh` - Setup and run script
- `match_data.json` - Football match data
- `NYK-JAN.json` - Basketball game data

## Usage

1. Run the application using the updated_run.sh script
2. Open your web browser and navigate to http://localhost:5000
3. Select either Football or Basketball from the landing page
4. Use the various features in the selected sport's interface:
   - View dashboard statistics
   - Analyze opponents
   - Get lineup/formation recommendations
   - Generate game reports
   - Chat with the AI assistant

## API Integration

The system uses two different APIs:

1. **RapidAPI Football API**
   - Used for football next game prediction and opponent analysis
   - API key is included in the code

2. **RapidAPI Basketball API**
   - Used for basketball next game prediction and opponent analysis
   - API key is included in the code

## OpenAI API Key

The system uses OpenAI's API for generating insights and powering the chatbot. The run script includes a sample API key, but you may need to replace it with your own key for continued use.

## Customization

You can customize the system by:
- Updating the match_data.json file with your football team's data
- Modifying the NYK-JAN.json file with your basketball team's data
- Adjusting the frontend HTML files to match your team's branding
- Modifying the prompts in updated_unified_app.py to customize the AI responses

## Troubleshooting

- If the application fails to start, ensure Python is installed correctly
- If you see API errors, check that your API keys are valid
- If the frontend doesn't load properly, check that all HTML files are in the correct location
- For any other issues, check the console output for error messages

## License

This project is provided as-is for educational and demonstration purposes.

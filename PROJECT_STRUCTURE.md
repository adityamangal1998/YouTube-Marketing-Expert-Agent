# YouTube Marketing Expert Agent - Project Structure

```
YouTube Marketing Expert Agent/
│
├── 📄 main.py                  # Main Streamlit application
├── 📄 youtube_api.py           # YouTube Data API v3 wrapper
├── 📄 ai_analyzer.py           # AWS Bedrock AI analyzer (Claude Sonnet 3.5)
├── 📄 utils.py                 # Utility functions
├── 📄 configure.py             # Interactive configuration setup
├── 📄 test_setup.py           # Setup verification script
├── 📄 launcher.py             # Cross-platform launcher
├── 📄 run.bat                 # Windows batch launcher
├── 📄 requirements.txt        # Python dependencies
├── 📄 .env                    # Environment variables (API keys)
├── 📄 README.md              # Comprehensive documentation
└── 📄 PROJECT_STRUCTURE.md   # This file
```

## File Descriptions

### Core Application Files

**main.py**
- Main Streamlit application interface
- Orchestrates the analysis workflow
- Provides interactive dashboard with charts and visualizations
- Handles user input and displays results

**youtube_api.py**
- YouTube Data API v3 wrapper class
- Handles channel and video data fetching
- Manages API quotas and error handling
- Supports multiple URL formats

**ai_analyzer.py**
- AWS Bedrock integration for Claude Sonnet 3.5
- Generates AI-powered optimization suggestions
- Includes mock mode when AI is not configured
- Provides title, description, and tag improvements

**utils.py**
- Utility functions for data processing
- URL validation and parsing
- Text formatting and cleaning
- Number formatting and calculations

### Setup and Configuration Files

**configure.py**
- Interactive setup wizard for API credentials
- Securely manages environment variables
- Validates configuration settings
- User-friendly configuration interface

**test_setup.py**
- Comprehensive setup verification
- Tests all dependencies and API connections
- Provides diagnostic information
- Helps troubleshoot common issues

**launcher.py**
- Cross-platform application launcher
- Handles dependency installation
- Manages virtual environments
- Automated startup process

**run.bat**
- Windows-specific batch launcher
- Simplified one-click startup for Windows users
- Handles virtual environment creation
- Automated dependency management

### Configuration Files

**.env**
- Environment variables for API credentials
- YouTube Data API key
- AWS Bedrock configuration
- Regional settings

**requirements.txt**
- Python package dependencies
- Version specifications for compatibility
- Core packages for web interface and APIs

## Key Features by Component

### Main Application (main.py)
- **Channel Analysis Dashboard**: Interactive Streamlit interface
- **Performance Visualization**: Charts and graphs using Plotly
- **Video Analysis**: Individual video breakdown and suggestions
- **Export Functionality**: JSON and PDF report generation
- **Progress Tracking**: Real-time analysis progress indicators

### YouTube API (youtube_api.py)
- **Multi-format URL Support**: Handles various YouTube URL formats
- **Comprehensive Data Fetching**: Channel stats, video metadata, comments
- **Error Handling**: Robust API error management
- **Rate Limiting**: Respects API quotas and limits
- **Data Processing**: Clean, structured data output

### AI Analyzer (ai_analyzer.py)
- **Claude Sonnet 3.5 Integration**: Advanced AI analysis via AWS Bedrock
- **Smart Suggestions**: Context-aware optimization recommendations  
- **Content Ideas**: Future video suggestions based on performance
- **SEO Analysis**: Comprehensive SEO scoring and improvements
- **Mock Mode**: Fallback functionality when AI is unavailable

### Utilities (utils.py)
- **URL Processing**: YouTube URL parsing and validation
- **Data Formatting**: Human-readable number and text formatting
- **Text Analysis**: Keyword extraction and content analysis
- **File Operations**: Safe filename generation and text processing

## Workflow

1. **Setup**: User configures API credentials using `configure.py`
2. **Launch**: Application started via `launcher.py` or `run.bat`  
3. **Input**: User enters YouTube channel URL
4. **Fetch**: YouTube API retrieves channel and video data
5. **Analyze**: Basic metrics calculated and AI suggestions generated
6. **Display**: Results shown in interactive dashboard
7. **Export**: Optional report generation and download

## Dependencies

### Core Dependencies
- **streamlit**: Web application framework
- **pandas**: Data manipulation and analysis
- **plotly**: Interactive visualizations and charts
- **google-api-python-client**: YouTube Data API integration
- **boto3**: AWS Bedrock integration
- **python-dotenv**: Environment variable management

### Supporting Dependencies
- **isodate**: ISO 8601 duration parsing
- **requests**: HTTP library for web requests
- **fpdf2**: PDF generation for reports

## Security Considerations

- API credentials stored in `.env` file (not version controlled)
- Sensitive data masked in configuration interface
- Error handling prevents credential exposure
- Input validation prevents malicious data processing

## Extensibility

The modular design allows for easy extension:

- **New AI Models**: Add providers in `ai_analyzer.py`
- **Additional APIs**: Extend data sources in dedicated modules
- **Custom Metrics**: Add analysis functions in `main.py`
- **Export Formats**: Extend export functionality
- **UI Enhancements**: Modify Streamlit interface components

## Development Guidelines

- Follow PEP 8 style guidelines
- Add comprehensive error handling
- Include docstrings for all functions
- Maintain backward compatibility
- Test all API integrations
- Document configuration changes

# LLM Knowledge Extractor

A prototype application that uses Claude AI to extract summaries and structured data from text input. Built with FastAPI, PostgreSQL, Nuxt.js, and Vuetify.

## Features

- **Text Analysis**: Submit any text and get AI-powered summaries and structured data extraction
- **Claude Integration**: Uses Anthropic's Claude API for intelligent text processing
- **Structured Data Extraction**: Extracts key entities, topics, sentiment, dates, action items, and categories
- **History Management**: View, search, and manage previous extractions
- **Modern UI**: Clean, responsive interface built with Vuetify
- **Real-time Updates**: Instant feedback and live data updates

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: Nuxt.js 3, Vue 3, Vuetify 3
- **AI**: Anthropic Claude API
- **Database**: PostgreSQL
- **Containerization**: Docker & Docker Compose

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Anthropic API key ([Get one here](https://console.anthropic.com/))

### Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd llm-knowledge-extractor
   ```

2. **Set up environment variables**
   Create a `.env` file in the root directory:

   ```bash
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

3. **Project Structure**

   ```
   llm-knowledge-extractor/
   ├── backend/
   │   ├── main.py
   │   ├── requirements.txt
   │   └── Dockerfile
   ├── frontend/
   │   ├── pages/
   │   │   └── index.vue
   │   ├── plugins/
   │   │   └── vuetify.ts
   │   ├── nuxt.config.ts
   │   ├── package.json
   │   └── Dockerfile
   ├── docker-compose.yml
   ├── .env
   └── README.md
   ```

4. **Run with Docker Compose**

   ```bash
   docker compose -f docker-compose-local.yml up --build

   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Manual Setup (Alternative)

### Backend Setup

1. **Navigate to backend directory**

   ```bash
   cd backend
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL**

   - Install PostgreSQL locally
   - Create database: `knowledge_extractor`
   - Update database URL in `main.py` if needed

5. **Set environment variable**

   ```bash
   export ANTHROPIC_API_KEY=your_api_key_here
   ```

6. **Run the backend**
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup

1. **Navigate to frontend directory**

   ```bash
   cd frontend
   ```

2. **Install dependencies**

   ```bash
   npm install
   ```

3. **Run development server**
   ```bash
   npm run dev
   ```

## API Endpoints

### POST /api/extract

Extract knowledge from text using Claude AI.

**Request Body:**

```json
{
  "text": "Your text content here..."
}
```

**Response:**

```json
{
  "id": 1,
  "original_text": "Your text content here...",
  "summary": "AI-generated summary...",
  "structured_data": {
    "key_entities": ["Entity1", "Entity2"],
    "main_topics": ["Topic1", "Topic2"],
    "sentiment": "positive",
    "key_dates": ["2024-01-01"],
    "action_items": ["Task1", "Task2"],
    "categories": ["Category1"]
  },
  "created_at": "2024-01-01T12:00:00Z"
}
```

### GET /api/extractions

Get all extractions (latest 50).

### GET /api/extractions/{id}

Get a specific extraction by ID.

### DELETE /api/extractions/{id}

Delete an extraction by ID.

### GET /health

Health check endpoint.

## Features in Detail

### Text Analysis

- Paste any text content into the input field
- Click "Extract with Claude" to analyze
- Get instant AI-powered insights

### Structured Data Extraction

The system extracts:

- **Key Entities**: Important people, places, organizations
- **Main Topics**: 3-5 primary themes or subjects
- **Sentiment**: Overall emotional tone (positive, negative, neutral)
- **Key Dates**: Important dates mentioned in the text
- **Action Items**: Tasks or actions identified
- **Categories**: Suggested content categories

### History Management

- View all previous extractions in a sortable table
- Search and filter through extraction history
- Delete unwanted extractions
- View detailed results in expandable panels

### User Interface

- **Responsive Design**: Works on desktop and mobile
- **Dark/Light Theme**: Toggle between themes
- **Real-time Feedback**: Loading states and notifications
- **Expandable Panels**: Organized display of results
- **Data Tables**: Sortable, searchable extraction history

## Architecture

### Backend (FastAPI)

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM for database operations
- **PostgreSQL**: Robust relational database for data persistence
- **Anthropic SDK**: Official SDK for Claude AI integration

### Frontend (Nuxt.js + Vuetify)

- **Nuxt.js 3**: Vue.js framework for production-ready applications
- **Vue 3**: Progressive JavaScript framework with Composition API
- **Vuetify 3**: Material Design component framework
- **Pinia**: State management for Vue applications

### Database Schema

```sql
CREATE TABLE extractions (
    id SERIAL PRIMARY KEY,
    original_text TEXT NOT NULL,
    summary TEXT NOT NULL,
    structured_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Environment Variables

### Backend Environment Variables

- `ANTHROPIC_API_KEY`: Your Anthropic API key (required)
- `FRONTEND_URL`: Frontend URL for CORS (default: http://localhost:3000)
- `DATABASE_URL`: PostgreSQL connection string

### Frontend Environment Variables

- `API_BASE_URL`: Backend API URL (default: http://localhost:8000)

### Docker Environment Variables

- `POSTGRES_DB`: PostgreSQL database name
- `POSTGRES_USER`: PostgreSQL username
- `POSTGRES_PASSWORD`: PostgreSQL password

## Error Handling

The application includes comprehensive error handling:

- API request failures with user-friendly messages
- Database connection issues
- Claude API rate limiting and errors
- Input validation and sanitization

## Security Considerations

- Environment variables for sensitive data
- CORS configuration for cross-origin requests
- Input sanitization and validation
- SQL injection prevention with SQLAlchemy ORM

## Performance Optimizations

- Database indexing on frequently queried fields
- Efficient pagination for large datasets
- Caching strategies for repeated requests
- Optimized database queries with SQLAlchemy

## Future Enhancements

- User authentication and authorization
- File upload support for documents
- Export functionality (CSV, PDF)
- Advanced search and filtering
- Batch processing for multiple texts
- Custom extraction templates
- Integration with other LLM providers

## Troubleshooting

### Common Issues

1. **Claude API Errors**

   - Verify your API key is correct
   - Check your API usage limits
   - Ensure network connectivity

2. **Database Connection Issues**

   - Verify PostgreSQL is running
   - Check database credentials
   - Ensure database exists

3. **Frontend Build Issues**
   - Clear node_modules and reinstall
   - Check Node.js version compatibility
   - Verify Nuxt.js configuration

### Logs and Debugging

- Backend logs: Check FastAPI console output
- Frontend logs: Check browser developer console
- Database logs: Check PostgreSQL logs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is for demonstration purposes. Please respect the terms of service for the APIs used (Anthropic Claude).

## Support

For issues and questions:

- Check the troubleshooting section
- Review API documentation
- Create an issue in the repository

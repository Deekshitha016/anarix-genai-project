# GenAI SQL Assistant – ANARIX Internship Assignment

This project is a natural language interface to a SQL database built using FastAPI and OpenRouter LLMs. Users can ask questions about sales data, and the assistant will translate it into SQL, query the database, and return a clean, structured response — along with visual charts for comparative queries.

##  Features

-  LLM-powered natural language to SQL conversion
-  SQLite backend using real CSV product data
-  Auto-generated charts (bar graphs) for per-item or top-item queries
-  Streaming endpoint for real-time typing effect
-  Clean and modular code structure

##  Technologies Used

- Python 3.11+
- FastAPI
- Uvicorn
- SQLite
- OpenRouter (LLM)
- Pandas
- Matplotlib
- Requests

##  Project Structure

anarix_project/
├── main.py # Main FastAPI server with logic
├── build_db.py # Converts CSVs to SQLite database
├── ecommerce_data.db # SQLite database
├── chart.png # Auto-generated chart image
├── requirements.txt # All dependencies
├── README.md # Project documentation
├── .gitignore # Ignored files for Git
└── venv/ # Virtual environment 








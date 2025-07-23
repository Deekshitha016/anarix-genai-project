# GenAI SQL Assistant 

GenAI SQL Assistant is a natural language interface for querying sales data using FastAPI and OpenRouter LLMs. It translates user questions into SQL, executes them on a local SQLite database, and returns structured results with visual charts.

---

## Features

- LLM-powered natural language to SQL conversion  
- SQLite backend using real CSV product data  
- Auto-generated bar charts for top-item or per-item comparisons  
- Streaming endpoint for real-time typing effect  
- Modular, maintainable codebase  

---

## Technologies Used

- Python 3.11+  
- FastAPI  
- Uvicorn  
- SQLite  
- OpenRouter (LLM API)  
- Pandas  
- Matplotlib  
- Requests  

---

## Project Structure

anarix_project/
├── main.py # FastAPI server with core logic
├── build_db.py # Converts CSV files into SQLite database
├── ecommerce_data.db # Generated SQLite database file
├── chart.png # Output image from matplotlib
├── requirements.txt # Python dependencies
├── README.md # Project documentation
├── .gitignore # Git ignored files
└── venv/ # Python virtual environment

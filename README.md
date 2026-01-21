# FastAPI Application

This project is a simple FastAPI application that provides three API endpoints: `/health`, `/error`, and `/load`. It is designed to demonstrate basic API functionality and can be used as a template for more complex applications.

## Project Structure

```
fastapi-app
├── src
│   ├── main.py          # Entry point of the FastAPI application
│   ├── routers
│   │   └── health.py    # Defines the API endpoints
│   └── models
│       └── __init__.py  # Placeholder for data models or schemas
├── requirements.txt      # Lists the project dependencies
├── .gitignore            # Specifies files to be ignored by Git
└── README.md             # Documentation for the project
```

## API Endpoints

- **GET /health**
  - Returns a JSON response indicating the health status of the application.

- **GET /error**
  - Intentionally raises an error to demonstrate error handling.

- **GET /load**
  - Simulates latency and CPU load for testing purposes.

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd fastapi-app
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   uvicorn src.main:app --reload
   ```

4. Access the API documentation at `http://127.0.0.1:8000/docs`.

## Usage Examples

- Check health status:
  ```
  curl http://127.0.0.1:8000/health
  ```

- Trigger an error:
  ```
  curl http://127.0.0.1:8000/error
  ```

- Simulate load:
  ```
  curl http://127.0.0.1:8000/load
  ```

## License

This project is licensed under the MIT License. See the LICENSE file for more details.# ai-learning-azure

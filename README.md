# swe573-ozguner
SWE 573 Repository - Ozguner


# SWE573 App Documentation

Application is deployed and can be reached at: http://34.234.74.196:3000/

## Folder Structure

- **`backend/`**: Contains the backend application built with FastAPI.
  - `main.py`: The entry point for the FastAPI application.
  - `.env`: Environment variables file for the backend (explained below).
- **`frontend/`**: Contains the frontend application built with React.
  - `swe573-app/`: The main directory for the frontend React code.
- **`static/images/`**: A directory used to store uploaded images for the application.
- **`docker-compose.yml`**: Defines the services for the application, including the backend, frontend, and database.
- **`requirements.txt`**: Specifies the Python dependencies for the backend.

---

## Required `.env` Files

### Backend `.env` File
Create a `.env` file inside the `backend/` folder. Example content:

```env
SECRET_KEY=your_secret_key
DATABASE_URL=postgresql://postgres:password@db/swe573_database
```
( you can refer to configuration of the backend for the content )

## How to run

- Go to root folder of the project.
- Make sure you have necessary .env content is created.
- `docker-compose up --build` ( sudo if necessary )

# Todo List API

This is a simple Todo List API built with Python and FastAPI.

## Features

- [x] User registration to create a new user
- [x] Login endpoint to authenticate the user and generate a token
- [x] CRUD operations for managing the to-do list
- [x] User authentication to allow only authorized users to access the to-do list
- [x] Error handling and security measures
- [x] Database integration to store user and to-do list data
- [x] Proper data validation
- [x] Pagination and filtering for the to-do list

### Bonus Features

- [x] Implement filtering and sorting for the to-do list
- [x] Implement unit tests for the API(I have used pytest)
- [x] Implement rate limiting and throttling for the API
- [x] Implement refresh token mechanism for the authentication

## Prerequisites

- Python 3.x
- pip (Python package manager)
- Git

## Getting Started

Follow these steps to set up and run the Todo List API on your local machine:

1. **Clone the repository:**

```
git clone https://github.com/IOabsolutes/Todo_API_roadmap.sh.git
```

2. **Navigate to the project directory:**

```
cd Todo-List-API
```

3. **Create a virtual environment (optional but recommended):**

```
python -m venv .venv
```

4. **Activate the virtual environment:**

- For Windows:
  ```
  .venv\Scripts\activate
  ```
- For macOS and Linux:
  ```
  source .venv/bin/activate
  ```

5. **Install the project dependencies:**

```
pip install -r requirements.txt
```

6. **Set up the database:**

- Make sure you have a compatible database system installed (e.g., SQLite, PostgreSQL).
- Update the database connection settings in the project configuration file (`config.py`) if necessary.
- Run the database migrations:
  ```
    alembic upgrade head
  ```

7. **Start the development server:**

```
py main.py:app --reload
```

8. **Access the API Documentation:**
   Open your web browser and visit `http://localhost:5000/docs` to access the Todo List API.

## API Endpoints

The following endpoints are available in the Todo List API:

### Todo List API

- `GET /task`: Retrieve a list of all todos.
- `GET /task/sorted>`: Retrieve a sorted list of all todos.
- `GET /task/filtered>`: Retrieve a filtered list of all todos.
- `POST /task`: Create a new todo.
- `PUT /task/<int:todo_id>`: Update an existing todo.
- `DELETE /task/<int:todo_id>`: Delete a todo.

### User Authentication

- 'POST /auth/register': Register a new user.
- 'POST /auth/login': Log in and obtain an access token.
- 'POST /auth/logout': Log out and invalidate the access token.
- 'GET /auth/refresh': Refresh the access token.
- 'POST /auth/access_token': Obtain a new access token using a refresh token.

## Project Regiments

- [Todo List API](https://roadmap.sh/projects/todo-list-api)

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a
pull request.


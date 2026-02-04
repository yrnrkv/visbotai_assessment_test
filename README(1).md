# School Library Chat Agent 📚

A Python console-based chat agent that answers natural language questions about a school library database.

## Features

- **Natural Language Queries**: Ask questions in plain English
- **Book Management**: Search, check availability, browse by genre/author
- **Student Management**: View students, filter by grade
- **Borrowing Tracking**: View current borrowings, overdue books, borrowing history
- **Library Statistics**: Get an overview of the library's status

## Quick Start

### 1. Set up the database

```bash
python setup_database.py
```

This creates `library.db` with sample data including:
- 12 books across various genres
- 8 students in grades 9-12
- Multiple borrowing records

### 2. Run the chat agent

```bash
python library_agent.py
```

### 3. Start asking questions!

```
You: What books are available?
You: What books did Alice Chan borrow?
You: Show me fantasy books
You: Library stats
You: help
```

## Example Queries

### Books
- "What books are available?"
- "Show all books"
- "Books by George Orwell"
- "Fantasy books"
- "Is The Hobbit available?"

### Students
- "List all students"
- "Students in grade 10"

### Borrowings
- "What books did Alice Chan borrow?"
- "Current borrowings"
- "Overdue books"
- "Borrowing history"

### Statistics
- "Library stats"
- "How many books do we have?"

## Project Structure

```
school-library-agent/
├── library_agent.py      # Main agent code (LibraryDatabase + LibraryChatAgent)
├── setup_database.py     # Database initialization script
├── test_agent.py         # Unit tests
├── requirements.txt      # Dependencies (standard library only)
└── README.md            # This file
```

## Running Tests

```bash
python test_agent.py
```

## Database Schema

```sql
-- Books table
CREATE TABLE books (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    isbn TEXT UNIQUE,
    published_year INTEGER,
    genre TEXT,
    total_copies INTEGER NOT NULL DEFAULT 1,
    available_copies INTEGER NOT NULL DEFAULT 1
);

-- Students table
CREATE TABLE students (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    grade INTEGER,  -- 7 to 12
    student_id TEXT UNIQUE  -- e.g., 'S2023001'
);

-- Borrowings table
CREATE TABLE borrowings (
    id INTEGER PRIMARY KEY,
    student_id INTEGER,
    book_id INTEGER,
    borrow_date DATE DEFAULT CURRENT_DATE,
    due_date DATE,
    return_date DATE,  -- NULL = still borrowed
    FOREIGN KEY(student_id) REFERENCES students(id),
    FOREIGN KEY(book_id) REFERENCES books(id)
);
```

## Architecture

The agent uses a **rule-based pattern matching** approach:

1. **LibraryDatabase**: Handles all SQL queries and database operations
2. **LibraryChatAgent**: Processes natural language using regex patterns and routes to appropriate database methods

### Why Rule-Based?

- **No external dependencies**: Works with Python standard library only
- **Fast and deterministic**: No API calls or latency
- **Easy to extend**: Add new patterns and handlers
- **Transparent**: Easy to understand and debug

### Extending with LLM

To add LLM-based understanding, you could:
1. Add OpenAI/Anthropic API calls for intent classification
2. Use LangChain or similar frameworks for tool calling
3. Keep the database layer unchanged

## License

MIT License - Feel free to use and modify!
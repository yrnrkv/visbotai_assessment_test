"""
Database setup script for the School Library Chat Agent.
Creates the database schema and populates it with sample data.
"""

import sqlite3
import os


def setup_database(db_path: str = "library.db"):
    """Create the database schema and populate with sample data."""
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    print("Creating database schema...")
    
    # Books table
    cursor.execute("""
        CREATE TABLE books (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT UNIQUE,
            published_year INTEGER,
            genre TEXT,
            total_copies INTEGER NOT NULL DEFAULT 1,
            available_copies INTEGER NOT NULL DEFAULT 1
        )
    """)
    
    # Students table
    cursor.execute("""
        CREATE TABLE students (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            grade INTEGER,
            student_id TEXT UNIQUE
        )
    """)
    
    # Borrowings table
    cursor.execute("""
        CREATE TABLE borrowings (
            id INTEGER PRIMARY KEY,
            student_id INTEGER,
            book_id INTEGER,
            borrow_date DATE DEFAULT CURRENT_DATE,
            due_date DATE,
            return_date DATE,
            FOREIGN KEY(student_id) REFERENCES students(id),
            FOREIGN KEY(book_id) REFERENCES books(id)
        )
    """)
    
    print("Schema created successfully!")
    
    # Insert sample books
    print("Inserting sample books...")
    books_data = [
        ('The Hobbit', 'J.R.R. Tolkien', '978-0547928227', 1937, 'Fantasy', 5, 3),
        ('1984', 'George Orwell', '978-0451524935', 1949, 'Dystopia', 4, 1),
        ('To Kill a Mockingbird', 'Harper Lee', '978-0446310789', 1960, 'Fiction', 6, 4),
        ('Pride and Prejudice', 'Jane Austen', '978-0141439518', 1813, 'Romance', 3, 3),
        ('The Great Gatsby', 'F. Scott Fitzgerald', '978-0743273565', 1925, 'Fiction', 4, 2),
        ('Harry Potter and the Sorcerer\'s Stone', 'J.K. Rowling', '978-0590353427', 1997, 'Fantasy', 8, 5),
        ('The Catcher in the Rye', 'J.D. Salinger', '978-0316769488', 1951, 'Fiction', 3, 0),
        ('Lord of the Flies', 'William Golding', '978-0399501487', 1954, 'Fiction', 4, 4),
        ('Animal Farm', 'George Orwell', '978-0451526342', 1945, 'Dystopia', 5, 3),
        ('Brave New World', 'Aldous Huxley', '978-0060850524', 1932, 'Dystopia', 3, 2),
        ('The Diary of a Young Girl', 'Anne Frank', '978-0553296983', 1947, 'Biography', 4, 4),
        ('Charlotte\'s Web', 'E.B. White', '978-0061124952', 1952, 'Children', 6, 6),
    ]
    
    cursor.executemany("""
        INSERT INTO books (title, author, isbn, published_year, genre, total_copies, available_copies)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, books_data)
    
    print(f"Inserted {len(books_data)} books.")
    
    # Insert sample students
    print("Inserting sample students...")
    students_data = [
        ('Alice Chan', 10, 'S2023001'),
        ('Bob Lee', 11, 'S2023005'),
        ('Carol Martinez', 9, 'S2023012'),
        ('David Kim', 10, 'S2023018'),
        ('Emma Wilson', 12, 'S2023022'),
        ('Frank Zhang', 11, 'S2023030'),
        ('Grace Johnson', 9, 'S2023035'),
        ('Henry Brown', 12, 'S2023041'),
    ]
    
    cursor.executemany("""
        INSERT INTO students (name, grade, student_id)
        VALUES (?, ?, ?)
    """, students_data)
    
    print(f"Inserted {len(students_data)} students.")
    
    # Insert sample borrowings
    print("Inserting sample borrowings...")
    borrowings_data = [
        # Alice Chan (id=1) - currently has The Hobbit
        (1, 1, '2026-01-15', '2026-02-15', None),
        # Alice also borrowed 1984 and returned it
        (1, 2, '2025-12-01', '2025-12-15', '2025-12-14'),
        # Bob Lee (id=2) - currently has 1984 and Great Gatsby
        (2, 2, '2026-01-20', '2026-02-20', None),
        (2, 5, '2026-01-25', '2026-02-25', None),
        # Carol Martinez (id=3) - has The Catcher in the Rye (all copies borrowed)
        (3, 7, '2026-01-10', '2026-02-10', None),
        # David Kim (id=4) - borrowed Harry Potter
        (4, 6, '2026-01-28', '2026-02-28', None),
        # Emma Wilson (id=5) - has 1984 and Brave New World
        (5, 2, '2026-01-18', '2026-02-18', None),
        (5, 10, '2026-01-22', '2026-02-22', None),
        # Frank Zhang (id=6) - borrowed and returned The Hobbit
        (6, 1, '2025-11-01', '2025-11-15', '2025-11-14'),
        # Grace Johnson (id=7) - has Harry Potter and Animal Farm
        (7, 6, '2026-01-30', '2026-03-01', None),
        (7, 9, '2026-01-30', '2026-03-01', None),
        # Henry Brown (id=8) - borrowed The Catcher in the Rye (all 3 copies now out)
        (8, 7, '2026-01-05', '2026-02-05', None),
        (8, 7, '2025-12-20', '2026-01-20', '2026-01-19'),  # previously borrowed and returned
    ]
    
    cursor.executemany("""
        INSERT INTO borrowings (student_id, book_id, borrow_date, due_date, return_date)
        VALUES (?, ?, ?, ?, ?)
    """, borrowings_data)
    
    print(f"Inserted {len(borrowings_data)} borrowing records.")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Database setup complete! Created: {db_path}")
    print("\nSummary:")
    print(f"  - {len(books_data)} books")
    print(f"  - {len(students_data)} students")
    print(f"  - {len(borrowings_data)} borrowing records")


if __name__ == "__main__":
    setup_database()
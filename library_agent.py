"""
School Library Chat Agent
A Python console-based chat agent that answers natural language questions about a school library database.
"""

import sqlite3
import re
from datetime import datetime
from typing import Optional, List, Dict, Any


class LibraryDatabase:
    """Handles all database operations for the school library."""
    
    def __init__(self, db_path: str = "library.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SQL query and return results as a list of dictionaries."""
        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_all_books(self) -> List[Dict]:
        """Get all books in the library."""
        return self.execute_query("SELECT * FROM books")
    
    def get_available_books(self) -> List[Dict]:
        """Get all books that have available copies."""
        return self.execute_query("SELECT * FROM books WHERE available_copies > 0")
    
    def get_unavailable_books(self) -> List[Dict]:
        """Get all books that are completely borrowed out."""
        return self.execute_query("SELECT * FROM books WHERE available_copies = 0")
    
    def search_books_by_title(self, title: str) -> List[Dict]:
        """Search books by title (partial match)."""
        return self.execute_query(
            "SELECT * FROM books WHERE LOWER(title) LIKE LOWER(?)",
            (f"%{title}%",)
        )
    
    def search_books_by_author(self, author: str) -> List[Dict]:
        """Search books by author (partial match)."""
        return self.execute_query(
            "SELECT * FROM books WHERE LOWER(author) LIKE LOWER(?)",
            (f"%{author}%",)
        )
    
    def search_books_by_genre(self, genre: str) -> List[Dict]:
        """Search books by genre (partial match)."""
        return self.execute_query(
            "SELECT * FROM books WHERE LOWER(genre) LIKE LOWER(?)",
            (f"%{genre}%",)
        )
    
    def get_all_students(self) -> List[Dict]:
        """Get all students."""
        return self.execute_query("SELECT * FROM students")
    
    def search_student_by_name(self, name: str) -> List[Dict]:
        """Search students by name (partial match)."""
        return self.execute_query(
            "SELECT * FROM students WHERE LOWER(name) LIKE LOWER(?)",
            (f"%{name}%",)
        )
    
    def get_student_by_id(self, student_id: str) -> Optional[Dict]:
        """Get a student by their student_id (e.g., 'S2023001')."""
        results = self.execute_query(
            "SELECT * FROM students WHERE student_id = ?",
            (student_id,)
        )
        return results[0] if results else None
    
    def get_books_borrowed_by_student(self, student_name: str) -> List[Dict]:
        """Get all books borrowed by a student (by name)."""
        return self.execute_query("""
            SELECT b.title, b.author, br.borrow_date, br.due_date, br.return_date,
                   CASE WHEN br.return_date IS NULL THEN 'Currently Borrowed' ELSE 'Returned' END as status
            FROM borrowings br
            JOIN books b ON br.book_id = b.id
            JOIN students s ON br.student_id = s.id
            WHERE LOWER(s.name) LIKE LOWER(?)
            ORDER BY br.borrow_date DESC
        """, (f"%{student_name}%",))
    
    def get_current_borrowings_by_student(self, student_name: str) -> List[Dict]:
        """Get currently borrowed books by a student."""
        return self.execute_query("""
            SELECT b.title, b.author, br.borrow_date, br.due_date
            FROM borrowings br
            JOIN books b ON br.book_id = b.id
            JOIN students s ON br.student_id = s.id
            WHERE LOWER(s.name) LIKE LOWER(?) AND br.return_date IS NULL
        """, (f"%{student_name}%",))
    
    def get_all_current_borrowings(self) -> List[Dict]:
        """Get all currently borrowed books."""
        return self.execute_query("""
            SELECT s.name as student_name, s.student_id, b.title, b.author, 
                   br.borrow_date, br.due_date
            FROM borrowings br
            JOIN books b ON br.book_id = b.id
            JOIN students s ON br.student_id = s.id
            WHERE br.return_date IS NULL
            ORDER BY br.due_date
        """)
    
    def get_overdue_books(self, current_date: str = None) -> List[Dict]:
        """Get all overdue books."""
        if current_date is None:
            current_date = datetime.now().strftime("%Y-%m-%d")
        return self.execute_query("""
            SELECT s.name as student_name, s.student_id, b.title, b.author,
                   br.borrow_date, br.due_date
            FROM borrowings br
            JOIN books b ON br.book_id = b.id
            JOIN students s ON br.student_id = s.id
            WHERE br.return_date IS NULL AND br.due_date < ?
            ORDER BY br.due_date
        """, (current_date,))
    
    def get_borrowing_history(self) -> List[Dict]:
        """Get complete borrowing history."""
        return self.execute_query("""
            SELECT s.name as student_name, b.title, br.borrow_date, br.due_date, br.return_date
            FROM borrowings br
            JOIN books b ON br.book_id = b.id
            JOIN students s ON br.student_id = s.id
            ORDER BY br.borrow_date DESC
        """)
    
    def get_book_availability(self, title: str) -> List[Dict]:
        """Check availability of a specific book."""
        return self.execute_query("""
            SELECT title, author, total_copies, available_copies,
                   (total_copies - available_copies) as borrowed_copies
            FROM books
            WHERE LOWER(title) LIKE LOWER(?)
        """, (f"%{title}%",))
    
    def get_students_by_grade(self, grade: int) -> List[Dict]:
        """Get all students in a specific grade."""
        return self.execute_query(
            "SELECT * FROM students WHERE grade = ?",
            (grade,)
        )
    
    def get_library_stats(self) -> Dict:
        """Get overall library statistics."""
        total_books = self.execute_query("SELECT COUNT(*) as count FROM books")[0]['count']
        total_copies = self.execute_query("SELECT SUM(total_copies) as total FROM books")[0]['total']
        available_copies = self.execute_query("SELECT SUM(available_copies) as available FROM books")[0]['available']
        total_students = self.execute_query("SELECT COUNT(*) as count FROM students")[0]['count']
        active_borrowings = self.execute_query(
            "SELECT COUNT(*) as count FROM borrowings WHERE return_date IS NULL"
        )[0]['count']
        
        return {
            'total_books': total_books,
            'total_copies': total_copies or 0,
            'available_copies': available_copies or 0,
            'borrowed_copies': (total_copies or 0) - (available_copies or 0),
            'total_students': total_students,
            'active_borrowings': active_borrowings
        }
    
    def close(self):
        """Close the database connection."""
        self.conn.close()


class LibraryChatAgent:
    """
    A simple rule-based chat agent for the school library.
    Uses pattern matching to understand user queries and route them to appropriate database operations.
    """
    
    def __init__(self, db: LibraryDatabase):
        self.db = db
        self.patterns = self._build_patterns()
    
    def _build_patterns(self) -> List[tuple]:
        """Build regex patterns for intent recognition."""
        return [
            # Books borrowed by a student
            (r"(?:what|which) books? (?:did|has|have) (.+?) borrow", self._handle_student_borrowings),
            (r"books? borrowed by (.+)", self._handle_student_borrowings),
            (r"(.+?)(?:'s)? (?:borrowed )?books?", self._handle_student_borrowings),
            
            # Available books
            (r"(?:which|what) books? (?:are|is) (?:currently )?available", self._handle_available_books),
            (r"available books?", self._handle_available_books),
            (r"books? (?:that are )?(?:in stock|available)", self._handle_available_books),
            
            # Unavailable/borrowed out books
            (r"(?:which|what) books? (?:are|is) (?:not available|unavailable|borrowed out)", self._handle_unavailable_books),
            (r"unavailable books?", self._handle_unavailable_books),
            
            # All books
            (r"(?:list|show|get|what are) (?:all )?(?:the )?books?", self._handle_all_books),
            (r"all books?", self._handle_all_books),
            
            # Search by author
            (r"books? (?:written )?by (.+)", self._handle_search_by_author),
            (r"(?:find|search|get) (.+?)(?:'s)? books?", self._handle_search_by_author),
            
            # Search by genre
            (r"(.+?) books?$", self._handle_search_by_genre),
            (r"books? (?:in|of) (?:the )?(.+?) genre", self._handle_search_by_genre),
            
            # Book availability check
            (r"(?:is|are) (.+?) available", self._handle_book_availability),
            (r"(?:check|find) availability (?:of|for) (.+)", self._handle_book_availability),
            (r"(?:do you have|have) (.+)", self._handle_book_availability),
            
            # Current borrowings
            (r"(?:current|active) borrowings?", self._handle_current_borrowings),
            (r"(?:who|which students?) (?:has|have) borrowed", self._handle_current_borrowings),
            (r"(?:what|which) books? (?:are|is) (?:currently )?borrowed", self._handle_current_borrowings),
            
            # Overdue books
            (r"overdue books?", self._handle_overdue_books),
            (r"(?:which|what) books? (?:are|is) overdue", self._handle_overdue_books),
            (r"late (?:returns?|books?)", self._handle_overdue_books),
            
            # All students
            (r"(?:list|show|get|all) students?", self._handle_all_students),
            (r"(?:who are|which) (?:the )?students?", self._handle_all_students),
            
            # Students by grade
            (r"students? in grade (\d+)", self._handle_students_by_grade),
            (r"grade (\d+) students?", self._handle_students_by_grade),
            
            # Library stats
            (r"(?:library )?(?:stats?|statistics|summary|overview)", self._handle_library_stats),
            (r"how many books?", self._handle_library_stats),
            
            # Borrowing history
            (r"borrowing history", self._handle_borrowing_history),
            (r"(?:all )?borrowings?", self._handle_borrowing_history),
            
            # Help
            (r"help|what can you do|commands?", self._handle_help),
        ]
    
    def process_query(self, query: str) -> str:
        """Process a user query and return a response."""
        query = query.strip().lower()
        
        if not query:
            return "Please enter a question about the library."
        
        # Try each pattern
        for pattern, handler in self.patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                try:
                    return handler(match)
                except Exception as e:
                    return f"Sorry, I encountered an error: {str(e)}"
        
        # Default response
        return self._handle_unknown()
    
    def _format_books(self, books: List[Dict], title: str = "Books") -> str:
        """Format a list of books for display."""
        if not books:
            return f"No {title.lower()} found."
        
        result = f"\n📚 {title} ({len(books)} found):\n"
        result += "-" * 50 + "\n"
        for book in books:
            result += f"  • {book['title']} by {book['author']}"
            if 'available_copies' in book and 'total_copies' in book:
                result += f" [{book['available_copies']}/{book['total_copies']} available]"
            if 'genre' in book and book['genre']:
                result += f" ({book['genre']})"
            result += "\n"
        return result
    
    def _format_borrowings(self, borrowings: List[Dict], title: str = "Borrowings") -> str:
        """Format borrowing records for display."""
        if not borrowings:
            return f"No {title.lower()} found."
        
        result = f"\n📖 {title} ({len(borrowings)} found):\n"
        result += "-" * 50 + "\n"
        for b in borrowings:
            result += f"  • {b.get('title', 'Unknown')}"
            if 'student_name' in b:
                result += f" - {b['student_name']}"
            result += f"\n    Borrowed: {b.get('borrow_date', 'N/A')}"
            result += f" | Due: {b.get('due_date', 'N/A')}"
            if 'status' in b:
                result += f" | Status: {b['status']}"
            if 'return_date' in b and b['return_date']:
                result += f" | Returned: {b['return_date']}"
            result += "\n"
        return result
    
    def _format_students(self, students: List[Dict], title: str = "Students") -> str:
        """Format a list of students for display."""
        if not students:
            return f"No {title.lower()} found."
        
        result = f"\n🎓 {title} ({len(students)} found):\n"
        result += "-" * 50 + "\n"
        for s in students:
            result += f"  • {s['name']} (ID: {s['student_id']}, Grade: {s['grade']})\n"
        return result
    
    def _handle_student_borrowings(self, match) -> str:
        """Handle queries about books borrowed by a student."""
        student_name = match.group(1).strip()
        # Clean up common words
        student_name = re.sub(r'\b(currently|borrow|borrowed|has|have|did)\b', '', student_name).strip()
        
        if not student_name or len(student_name) < 2:
            return "Please specify a student name."
        
        borrowings = self.db.get_books_borrowed_by_student(student_name)
        return self._format_borrowings(borrowings, f"Books borrowed by '{student_name}'")
    
    def _handle_available_books(self, match) -> str:
        """Handle queries about available books."""
        books = self.db.get_available_books()
        return self._format_books(books, "Available Books")
    
    def _handle_unavailable_books(self, match) -> str:
        """Handle queries about unavailable books."""
        books = self.db.get_unavailable_books()
        return self._format_books(books, "Unavailable Books (All copies borrowed)")
    
    def _handle_all_books(self, match) -> str:
        """Handle queries for all books."""
        books = self.db.get_all_books()
        return self._format_books(books, "All Library Books")
    
    def _handle_search_by_author(self, match) -> str:
        """Handle queries for books by an author."""
        author = match.group(1).strip()
        books = self.db.search_books_by_author(author)
        return self._format_books(books, f"Books by '{author}'")
    
    def _handle_search_by_genre(self, match) -> str:
        """Handle queries for books by genre."""
        genre = match.group(1).strip()
        # Skip common non-genre words
        skip_words = ['all', 'the', 'list', 'show', 'available', 'borrowed']
        if genre.lower() in skip_words:
            return self._handle_all_books(match)
        
        books = self.db.search_books_by_genre(genre)
        if books:
            return self._format_books(books, f"'{genre.title()}' Books")
        else:
            # Maybe they meant to search by title
            books = self.db.search_books_by_title(genre)
            if books:
                return self._format_books(books, f"Books matching '{genre}'")
            return f"No books found for genre or title '{genre}'."
    
    def _handle_book_availability(self, match) -> str:
        """Handle queries about specific book availability."""
        title = match.group(1).strip()
        books = self.db.get_book_availability(title)
        
        if not books:
            return f"No book found matching '{title}'."
        
        result = f"\n📚 Availability for '{title}':\n"
        result += "-" * 50 + "\n"
        for book in books:
            status = "✅ Available" if book['available_copies'] > 0 else "❌ Not Available"
            result += f"  • {book['title']} by {book['author']}\n"
            result += f"    {status} ({book['available_copies']}/{book['total_copies']} copies)\n"
        return result
    
    def _handle_current_borrowings(self, match) -> str:
        """Handle queries about current borrowings."""
        borrowings = self.db.get_all_current_borrowings()
        return self._format_borrowings(borrowings, "Current Borrowings")
    
    def _handle_overdue_books(self, match) -> str:
        """Handle queries about overdue books."""
        borrowings = self.db.get_overdue_books()
        if not borrowings:
            return "✅ No overdue books! All borrowed books are within their due dates."
        return self._format_borrowings(borrowings, "⚠️ Overdue Books")
    
    def _handle_all_students(self, match) -> str:
        """Handle queries for all students."""
        students = self.db.get_all_students()
        return self._format_students(students, "All Students")
    
    def _handle_students_by_grade(self, match) -> str:
        """Handle queries for students by grade."""
        grade = int(match.group(1))
        students = self.db.get_students_by_grade(grade)
        return self._format_students(students, f"Grade {grade} Students")
    
    def _handle_library_stats(self, match) -> str:
        """Handle queries for library statistics."""
        stats = self.db.get_library_stats()
        
        result = "\n📊 Library Statistics:\n"
        result += "-" * 50 + "\n"
        result += f"  📚 Total unique books: {stats['total_books']}\n"
        result += f"  📖 Total copies: {stats['total_copies']}\n"
        result += f"  ✅ Available copies: {stats['available_copies']}\n"
        result += f"  📤 Borrowed copies: {stats['borrowed_copies']}\n"
        result += f"  🎓 Total students: {stats['total_students']}\n"
        result += f"  📋 Active borrowings: {stats['active_borrowings']}\n"
        return result
    
    def _handle_borrowing_history(self, match) -> str:
        """Handle queries for borrowing history."""
        borrowings = self.db.get_borrowing_history()
        return self._format_borrowings(borrowings, "Borrowing History")
    
    def _handle_help(self, match) -> str:
        """Handle help queries."""
        return """
📚 School Library Chat Agent - Help
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

I can help you with the following queries:

📖 BOOKS:
  • "What books are available?"
  • "Show all books"
  • "Books by [author name]"
  • "Fantasy books" (search by genre)
  • "Is [book title] available?"

👤 STUDENTS:
  • "List all students"
  • "Students in grade 10"

📋 BORROWINGS:
  • "What books did Alice Chan borrow?"
  • "Current borrowings"
  • "Overdue books"
  • "Borrowing history"

📊 OTHER:
  • "Library stats" - Get overall statistics
  • "help" - Show this help message

Type 'quit' or 'exit' to leave the chat.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    def _handle_unknown(self) -> str:
        """Handle unknown queries."""
        return """
🤔 I'm not sure how to answer that question.

Try asking things like:
  • "What books are available?"
  • "What books did Alice Chan borrow?"
  • "Show all students"
  • "Library stats"

Type 'help' for more options.
"""


def main():
    """Main function to run the chat agent."""
    print("\n" + "=" * 60)
    print("📚 Welcome to the School Library Chat Agent!")
    print("=" * 60)
    print("I can help you find books, check borrowings, and more.")
    print("Type 'help' for a list of commands, or 'quit' to exit.")
    print("=" * 60 + "\n")
    
    # Initialize database and agent
    db = LibraryDatabase("library.db")
    agent = LibraryChatAgent(db)
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                print("\n👋 Goodbye! Thank you for using the Library Chat Agent.\n")
                break
            
            response = agent.process_query(user_input)
            print(f"\nAgent: {response}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")
    
    db.close()


if __name__ == "__main__":
    main()
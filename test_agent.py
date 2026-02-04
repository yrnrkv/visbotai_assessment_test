"""
Test suite for the School Library Chat Agent.
Run this to verify the agent is working correctly.
"""

import unittest
from library_agent import LibraryDatabase, LibraryChatAgent
from setup_database import setup_database


class TestLibraryAgent(unittest.TestCase):
    """Test cases for the Library Chat Agent."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database once for all tests."""
        setup_database("test_library.db")
        cls.db = LibraryDatabase("test_library.db")
        cls.agent = LibraryChatAgent(cls.db)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests."""
        cls.db.close()
        import os
        if os.path.exists("test_library.db"):
            os.remove("test_library.db")
    
    def test_available_books(self):
        """Test query for available books."""
        response = self.agent.process_query("What books are available?")
        self.assertIn("Available Books", response)
        self.assertIn("The Hobbit", response)
    
    def test_all_books(self):
        """Test query for all books."""
        response = self.agent.process_query("Show all books")
        self.assertIn("All Library Books", response)
        self.assertIn("12 found", response)
    
    def test_student_borrowings(self):
        """Test query for books borrowed by a student."""
        response = self.agent.process_query("What books did Alice Chan borrow?")
        self.assertIn("Alice Chan", response)
        self.assertIn("The Hobbit", response)
    
    def test_books_by_author(self):
        """Test query for books by an author."""
        response = self.agent.process_query("Books by George Orwell")
        self.assertIn("1984", response)
        self.assertIn("Animal Farm", response)
    
    def test_book_availability(self):
        """Test checking specific book availability."""
        response = self.agent.process_query("Is The Hobbit available?")
        self.assertIn("Availability", response)
        self.assertIn("The Hobbit", response)
    
    def test_current_borrowings(self):
        """Test query for current borrowings."""
        response = self.agent.process_query("Show current borrowings")
        self.assertIn("Current Borrowings", response)
    
    def test_all_students(self):
        """Test query for all students."""
        response = self.agent.process_query("List all students")
        self.assertIn("All Students", response)
        self.assertIn("Alice Chan", response)
        self.assertIn("Bob Lee", response)
    
    def test_students_by_grade(self):
        """Test query for students by grade."""
        response = self.agent.process_query("Students in grade 10")
        self.assertIn("Grade 10", response)
        self.assertIn("Alice Chan", response)
    
    def test_library_stats(self):
        """Test library statistics query."""
        response = self.agent.process_query("Library stats")
        self.assertIn("Library Statistics", response)
        self.assertIn("Total unique books", response)
    
    def test_genre_search(self):
        """Test searching books by genre."""
        response = self.agent.process_query("Fantasy books")
        self.assertIn("The Hobbit", response)
        self.assertIn("Harry Potter", response)
    
    def test_help(self):
        """Test help command."""
        response = self.agent.process_query("help")
        self.assertIn("Help", response)
        self.assertIn("BOOKS", response)
        self.assertIn("STUDENTS", response)
    
    def test_unknown_query(self):
        """Test handling of unknown queries."""
        response = self.agent.process_query("xyzabc123")
        self.assertIn("not sure", response)


class TestLibraryDatabase(unittest.TestCase):
    """Test cases for the LibraryDatabase class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database."""
        setup_database("test_db_only.db")
        cls.db = LibraryDatabase("test_db_only.db")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up."""
        cls.db.close()
        import os
        if os.path.exists("test_db_only.db"):
            os.remove("test_db_only.db")
    
    def test_get_all_books(self):
        """Test getting all books."""
        books = self.db.get_all_books()
        self.assertEqual(len(books), 12)
    
    def test_get_available_books(self):
        """Test getting available books."""
        books = self.db.get_available_books()
        self.assertGreater(len(books), 0)
        for book in books:
            self.assertGreater(book['available_copies'], 0)
    
    def test_search_by_author(self):
        """Test searching books by author."""
        books = self.db.search_books_by_author("Orwell")
        self.assertEqual(len(books), 2)
    
    def test_get_library_stats(self):
        """Test getting library statistics."""
        stats = self.db.get_library_stats()
        self.assertEqual(stats['total_books'], 12)
        self.assertIn('total_copies', stats)
        self.assertIn('available_copies', stats)


def run_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Running Library Chat Agent Tests")
    print("=" * 60 + "\n")
    
    # Run tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestLibraryAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestLibraryDatabase))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed.")
    print("=" * 60 + "\n")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_tests()
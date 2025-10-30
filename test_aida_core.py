import unittest
import time
import sys
import os

# Ensure aida package is in path if running from root
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from aida.osquery_rag import rag_engine, query_osquery_schema
from aida.query_library import search_query_library

class TestAidaCore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n[Setup] Initializing RAG Engine for tests (this may take a few seconds)...")
        start_time = time.time()
        rag_engine.initialize()
        print(f"[Setup] RAG Engine initialized in {time.time() - start_time:.2f}s")

    def test_01_rag_singleton(self):
        """Verify RAG engine acts as a singleton and doesn't re-initialize."""
        print("\nTesting RAG Singleton...")
        start_time = time.time()
        rag_engine.initialize() # Should be instant
        duration = time.time() - start_time
        self.assertTrue(rag_engine._initialized)
        self.assertLess(duration, 0.1, "Subsequent initialization should be near-instant")
        print("RAG Singleton test passed.")

    def test_02_schema_retrieval(self):
        """Verify standard RAG schema retrieval works."""
        print("\nTesting Schema Retrieval ('processes')...")
        start_time = time.time()
        results = query_osquery_schema("processes")
        duration = time.time() - start_time
        
        self.assertIn("processes", results)
        # It might return 'process_memory_map' or similar too, but 'pid' should be in standard processes table def
        self.assertIn("pid", results.lower()) 
        print(f"Schema retrieval test passed in {duration:.2f}s.")

    def test_03_query_library_exact(self):
        """Verify query library finds exact matches."""
        print("\nTesting Query Library (exact match 'launchd'வுகளை...)")
        results = search_query_library("launchd")
        self.assertIn("launchd", results)
        # Case insensitive check for SQL just in case
        self.assertTrue("select * from launchd" in results.lower())
        print("Query library exact match test passed.")

    def test_04_query_library_fuzzy(self):
        """Verify query library finds loose matches via FTS OR."""
        print("\nTesting Query Library (fuzzy match 'find malware'வுகளை...)")
        results = search_query_library("find malware")
        # Should find things with 'malware' even if 'find' isn't next to it
        self.assertIn("malware", results.lower())
        print("Query library fuzzy match test passed.")

    def test_05_query_library_no_results(self):
        """Verify graceful handling of no results."""
        print("\nTesting Query Library (no results)...")
        results = search_query_library("definitely_not_a_real_query_term_xyz")
        self.assertIn("No queries found", results)
        print("Query library no-results test passed.")

if __name__ == '__main__':
    unittest.main()

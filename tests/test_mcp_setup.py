"""
Pytest test suite for MCP server and database setup
Tests database connectivity, MCP server startup, and data access
"""

import pytest
import psycopg2
import subprocess
import time
import os
from dotenv import load_dotenv


class TestDatabaseConnection:
    """Test database connectivity and basic operations"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Load environment variables before each test"""
        load_dotenv('.env')
        self.db_url = os.getenv("DATABASE_URL")
        assert self.db_url, "DATABASE_URL not found in .env"
    
    def test_database_connection(self):
        """Test basic database connection"""
        conn = psycopg2.connect(self.db_url)
        assert conn is not None
        conn.close()
    
    def test_database_version(self):
        """Test database version query"""
        with psycopg2.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version()")
                version = cur.fetchone()[0]
                assert "PostgreSQL" in version
                assert "17" in version  # Should be PostgreSQL 17
    
    def test_nyc_table_exists(self):
        """Test that NYC property sales table exists"""
        with psycopg2.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'nyc_property_sales'
                """)
                count = cur.fetchone()[0]
                assert count == 1, "nyc_property_sales table not found"
    
    def test_nyc_table_structure(self):
        """Test NYC table has expected columns"""
        with psycopg2.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'nyc_property_sales' 
                    ORDER BY ordinal_position
                """)
                columns = cur.fetchall()
                
                # Check we have the expected number of columns
                assert len(columns) >= 20, f"Expected at least 20 columns, got {len(columns)}"
                
                # Check for key columns
                column_names = [col[0] for col in columns]
                required_columns = ['HOME_ID', 'BOROUGH', 'NEIGHBORHOOD', 'SALE PRICE', 'SALE DATE']
                for col in required_columns:
                    assert col in column_names, f"Required column {col} not found"
    
    def test_nyc_data_count(self):
        """Test NYC data has expected number of records"""
        with psycopg2.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM nyc_property_sales")
                count = cur.fetchone()[0]
                assert count > 10000, f"Expected >10k records, got {count}"
                assert count < 20000, f"Expected <20k records, got {count}"
    
    def test_nyc_data_quality(self):
        """Test data quality - no null prices, valid dates"""
        with psycopg2.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                # Test that we have valid price data
                cur.execute("""
                    SELECT COUNT(*) 
                    FROM nyc_property_sales 
                    WHERE "SALE PRICE" IS NOT NULL 
                    AND "SALE PRICE" != ''
                    AND CAST("SALE PRICE" AS NUMERIC) > 0
                """)
                valid_prices = cur.fetchone()[0]
                assert valid_prices > 1000, f"Expected >1k valid prices, got {valid_prices}"
                
                # Test that we have valid dates
                cur.execute("""
                    SELECT COUNT(*) 
                    FROM nyc_property_sales 
                    WHERE "SALE DATE" IS NOT NULL
                """)
                valid_dates = cur.fetchone()[0]
                assert valid_dates > 1000, f"Expected >1k valid dates, got {valid_dates}"
    
    def test_nyc_sample_query(self):
        """Test sample data query works"""
        with psycopg2.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT "HOME_ID", "BOROUGH", "NEIGHBORHOOD", "SALE PRICE", "SALE DATE"
                    FROM nyc_property_sales 
                    ORDER BY "SALE DATE" DESC 
                    LIMIT 5
                """)
                sales = cur.fetchall()
                assert len(sales) == 5, f"Expected 5 records, got {len(sales)}"
                
                # Check that we got actual data
                for sale in sales:
                    assert sale[0] is not None, "HOME_ID should not be null"
                    assert sale[1] is not None, "BOROUGH should not be null"
                    assert sale[2] is not None, "NEIGHBORHOOD should not be null"


class TestMCPServer:
    """Test MCP server startup and basic functionality"""
    
    def test_mcp_server_script_exists(self):
        """Test that MCP server script exists and is executable"""
        script_path = "./scripts/start-supabase-mcp-server.sh"
        assert os.path.exists(script_path), "MCP server script not found"
        assert os.access(script_path, os.X_OK), "MCP server script not executable"
    
    def test_mcp_server_environment_variables(self):
        """Test that required environment variables are set"""
        load_dotenv('.env')
        
        token = os.getenv("SUPABASE_ACCESS_TOKEN")
        project_ref = os.getenv("SUPABASE_PROJECT_REF")
        
        assert token, "SUPABASE_ACCESS_TOKEN not set"
        assert token != "your_personal_access_token_here", "SUPABASE_ACCESS_TOKEN not updated"
        assert project_ref, "SUPABASE_PROJECT_REF not set"
        assert project_ref == "ndnpuuoxalxwsqnlxdlk", "SUPABASE_PROJECT_REF incorrect"
    
    def test_mcp_server_startup(self):
        """Test that MCP server can start without errors"""
        # Start the server
        process = subprocess.Popen(
            ["./scripts/start-supabase-mcp-server.sh"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give it time to start and check for errors
        time.sleep(2)
        
        # Check if it started successfully (either still running or exited cleanly)
        return_code = process.poll()
        if return_code is not None:
            # Server exited, check for errors
            stdout, stderr = process.communicate()
            assert return_code == 0, f"MCP server failed with return code {return_code}. stderr: {stderr}"
            assert "Error" not in stderr, f"MCP server had errors: {stderr}"
        else:
            # Server is still running, which is good
            process.terminate()
            process.wait()
    
    def test_mcp_server_readonly_mode(self):
        """Test that MCP server runs in read-only mode"""
        # Check that the script contains the --read-only flag
        with open("./scripts/start-supabase-mcp-server.sh", "r") as f:
            content = f.read()
            assert "--read-only" in content, "MCP server not configured for read-only mode"


class TestDataAccess:
    """Test data access patterns that an AI agent would use"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Load environment variables before each test"""
        load_dotenv('.env')
        self.db_url = os.getenv("DATABASE_URL")
    
    def test_borough_query(self):
        """Test querying by borough (common AI agent query)"""
        with psycopg2.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT COUNT(*) 
                    FROM nyc_property_sales 
                    WHERE "BOROUGH" = 1
                """)
                manhattan_sales = cur.fetchone()[0]
                assert manhattan_sales > 0, "No Manhattan sales found"
    
    def test_neighborhood_query(self):
        """Test querying by neighborhood (common AI agent query)"""
        with psycopg2.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT "NEIGHBORHOOD", COUNT(*) as sales_count
                    FROM nyc_property_sales 
                    GROUP BY "NEIGHBORHOOD"
                    ORDER BY sales_count DESC
                    LIMIT 5
                """)
                neighborhoods = cur.fetchall()
                assert len(neighborhoods) == 5, f"Expected 5 neighborhoods, got {len(neighborhoods)}"
                assert all(neighborhood[1] > 0 for neighborhood in neighborhoods), "All neighborhoods should have sales"
    
    def test_price_range_query(self):
        """Test price range queries (common AI agent query)"""
        with psycopg2.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        COUNT(*) as total_sales,
                        MIN(CAST("SALE PRICE" AS NUMERIC)) as min_price,
                        MAX(CAST("SALE PRICE" AS NUMERIC)) as max_price,
                        AVG(CAST("SALE PRICE" AS NUMERIC)) as avg_price
                    FROM nyc_property_sales 
                    WHERE "SALE PRICE" IS NOT NULL 
                    AND "SALE PRICE" != ''
                    AND CAST("SALE PRICE" AS NUMERIC) > 0
                """)
                stats = cur.fetchone()
                assert stats[0] > 0, "No valid sales found"
                assert stats[1] > 0, "Min price should be positive"
                assert stats[2] > stats[1], "Max price should be greater than min price"
                assert stats[3] > 0, "Average price should be positive"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

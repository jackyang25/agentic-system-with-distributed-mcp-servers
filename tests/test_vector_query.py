import json
import os
import openai
from dotenv import load_dotenv

load_dotenv()


class VectorSearchTester:
    def __init__(self, openai_api_key: str = None):
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable."
            )

        openai.api_key = self.api_key
        self.embedding_model = "text-embedding-3-small"

    def format_query_for_embedding(self, query: str) -> str:
        return f"""Program: {query}
        Type: 
        Location: 
        Benefit: """

    def generate_query_embedding(self, query: str) -> list:
        formatted_query = self.format_query_for_embedding(query)

        try:
            response = openai.embeddings.create(
                model=self.embedding_model, input=formatted_query
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise

    def test_queries(self):
        test_queries = [
            "veteran mortgage assistance",
            "down payment help for first time buyers",
            "low interest rate home loans",
            "renovation financing programs",
            "affordable housing programs",
        ]

        print("Testing Vector Search Queries")
        print("=" * 50)

        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Query: '{query}'")
            print("-" * 30)

            try:
                embedding = self.generate_query_embedding(query)
                print(f"   Embedding generated: {len(embedding)} dimensions")
                print(f"   First 5 values: {embedding[:5]}")
                print(f"   Last 5 values: {embedding[-5:]}")

                formatted = self.format_query_for_embedding(query)
                print("   Formatted query:")
                print(f"   {formatted}")

            except Exception as e:
                print(f"   Error: {e}")

        print("\n" + "=" * 50)
        print("Copy any of these embeddings to test in Supabase!")

    def generate_supabase_query(self, query: str):
        embedding = self.generate_query_embedding(query)
        embedding_str = json.dumps(embedding)

        sql_query = f"""
        -- Test query for: "{query}"
        SELECT 
            program_name, 
            assistance_type, 
            max_benefit,
            jurisdiction,
            embedding_vector <-> '{embedding_str}' as distance
        FROM nyc_programs_rag 
        ORDER BY embedding_vector <-> '{embedding_str}'
        LIMIT 5;
        """

        print(f"Supabase SQL Query for: '{query}'")
        print("=" * 60)
        print(sql_query)
        return sql_query


def main():
    try:
        tester = VectorSearchTester()
        tester.test_queries()

        print("\n" + "=" * 60)
        print("GENERATING SUPABASE QUERY")
        print("=" * 60)

        test_query = "veteran, graduate, new york"
        tester.generate_supabase_query(test_query)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()

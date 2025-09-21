#!/usr/bin/env python3
"""
NY Programs Embedder

This script generates embeddings for NY programs data and saves them to CSV format
for use with pgvector in Supabase.
"""

import json
import csv
import os
from typing import List, Dict, Any
from pathlib import Path
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class NYProgramsEmbedder:
    def __init__(self, openai_api_key: str = None):
        """Initialize the embedder with OpenAI API key."""
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        openai.api_key = self.api_key
        self.embedding_model = "text-embedding-3-small"  # Cost-effective model
    
    def format_program_for_embedding(self, program: Dict[str, Any]) -> str:
        """Format a program dictionary into structured text for embedding."""
        return f"""Program: {program.get('Program Name', '')}
Type: {program.get('Assistance Type', '')}
Location: {program.get('Jurisdiction', '')}
Benefit: {program.get('Max Benefit', '')}"""
    
    def format_query_for_embedding(self, query: str) -> str:
        """Format a user query to match the program structure."""
        return f"""Program: {query}
Type: 
Location: 
Benefit: """
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for the given text."""
        try:
            response = openai.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise
    
    def load_programs(self, json_file_path: str) -> List[Dict[str, Any]]:
        """Load programs from JSON file."""
        with open(json_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def process_programs(self, programs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process all programs and generate embeddings."""
        processed_programs = []
        
        print(f"Processing {len(programs)} programs...")
        
        for i, program in enumerate(programs):
            try:
                # Format the program for embedding
                formatted_text = self.format_program_for_embedding(program)
                
                # Generate embedding
                embedding = self.generate_embedding(formatted_text)
                
                # Create processed program entry
                processed_program = {
                    'program_id': i + 1,
                    'program_name': program.get('Program Name', ''),
                    'formatted_text': formatted_text,
                    'embedding_vector': embedding,
                    'original_data': program
                }
                
                processed_programs.append(processed_program)
                
                if (i + 1) % 10 == 0:
                    print(f"Processed {i + 1}/{len(programs)} programs...")
                    
            except Exception as e:
                print(f"Error processing program {i + 1}: {e}")
                continue
        
        print(f"Successfully processed {len(processed_programs)} programs")
        return processed_programs
    
    def save_to_csv(self, processed_programs: List[Dict[str, Any]], output_file: str):
        """Save processed programs to CSV file."""
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'program_id',
                'program_name', 
                'formatted_text',
                'embedding_vector',
                'jurisdiction',
                'assistance_type',
                'max_benefit',
                'eligibility',
                'source'
            ])
            
            # Write data
            for program in processed_programs:
                original = program['original_data']
                writer.writerow([
                    program['program_id'],
                    program['program_name'],
                    program['formatted_text'],
                    json.dumps(program['embedding_vector']),  # Store as JSON string
                    original.get('Jurisdiction', ''),
                    original.get('Assistance Type', ''),
                    original.get('Max Benefit', ''),
                    original.get('Eligibility', ''),
                    original.get('Source', '')
                ])
        
        print(f"Saved {len(processed_programs)} programs to {output_file}")
    
    def save_embeddings_only(self, processed_programs: List[Dict[str, Any]], output_file: str):
        """Save just the embeddings in a format suitable for pgvector."""
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(['program_id', 'embedding_vector'])
            
            # Write data
            for program in processed_programs:
                writer.writerow([
                    program['program_id'],
                    json.dumps(program['embedding_vector'])
                ])
        
        print(f"Saved embeddings to {output_file}")

def main():
    """Main function to run the embedder."""
    # Paths
    script_dir = Path(__file__).parent
    json_file = script_dir / "ny_programs.json"
    output_csv = script_dir / "ny_programs_embeddings.csv"
    embeddings_csv = script_dir / "ny_programs_embeddings_only.csv"
    
    # Check if JSON file exists
    if not json_file.exists():
        print(f"Error: {json_file} not found!")
        return
    
    try:
        # Initialize embedder
        embedder = NYProgramsEmbedder()
        
        # Load programs
        print("Loading programs from JSON...")
        programs = embedder.load_programs(str(json_file))
        
        # Process programs
        processed_programs = embedder.process_programs(programs)
        
        # Save results
        embedder.save_to_csv(processed_programs, str(output_csv))
        embedder.save_embeddings_only(processed_programs, str(embeddings_csv))
        
        print("\nEmbedding generation complete!")
        print(f"Full data: {output_csv}")
        print(f"Embeddings only: {embeddings_csv}")
        print(f"Total programs processed: {len(processed_programs)}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

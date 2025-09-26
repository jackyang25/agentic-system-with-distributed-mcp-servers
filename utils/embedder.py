#!/usr/bin/env python3
"""
NY Programs Embedder

This script generates embeddings for NY programs data and saves them to CSV format
for use with pgvector in Supabase.
"""

import csv
import json
import os
from typing import Any

import openai
from openai.types.create_embedding_response import CreateEmbeddingResponse

from utils.convenience import load_secrets

# Load environment variables
load_secrets()


class NYProgramsEmbedder:
    def __init__(self) -> None:
        """Initialize the embedder."""
        self.api_key: str = os.getenv(key="OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable."
            )

        openai.api_key = self.api_key
        self.embedding_model: str = "text-embedding-3-small"  # Cost-effective model

    def format_program_for_embedding(self, program: dict[str, Any]) -> str:
        """Format a program dictionary into structured text for embedding."""

        format_program_string: str = f"""Program: {program.get("Program Name", "")}
Type: {program.get("Assistance Type", "")}
Location: {program.get("Jurisdiction", "")}
Benefit: {program.get("Max Benefit", "")}"""

        return format_program_string

    def format_query_for_embedding(self, query: str) -> str:
        """Format a user query to match the program structure."""

        embedding_query_string: str = f"""Program: {query}
Type: 
Location: 
Benefit: """

        return embedding_query_string

    def generate_embedding(self, text: str) -> list[float]:
        """Generate embedding for the given text."""
        try:
            response: CreateEmbeddingResponse = openai.embeddings.create(
                model=self.embedding_model, input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise

    def load_programs(self, json_file_path: str) -> list[dict[str, Any]]:
        """Load programs from JSON file."""
        if not os.path.exists(json_file_path):
            raise FileNotFoundError(f"File not found: {json_file_path}")
        with open(file=json_file_path, mode="r", encoding="utf-8") as f:
            return json.load(f)

    def process_programs(self, programs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Process all programs and generate embeddings."""
        processed_programs: list[Any] = []

        print(f"Processing {len(programs)} programs...")

        for i, program in enumerate(programs):
            try:
                # Format the program for embedding
                formatted_text: str = self.format_program_for_embedding(program=program)

                # Generate embedding
                embedding: list[float] = self.generate_embedding(text=formatted_text)

                # Create processed program entry
                processed_program: dict[str, Any] = {
                    "program_id": i + 1,
                    "program_name": program.get("Program Name", ""),
                    "formatted_text": formatted_text,
                    "embedding_vector": embedding,
                    "original_data": program,
                }

                processed_programs.append(processed_program)

                if (i + 1) % 10 == 0:
                    print(f"Processed {i + 1}/{len(programs)} programs...")

            except Exception as e:
                print(f"Error processing program {i + 1}: {e}")
                continue

        print(f"Successfully processed {len(processed_programs)} programs")
        return processed_programs

    def save_to_csv(
        self, processed_programs: list[dict[str, Any]], output_file: str
    ) -> None:
        """Save processed programs to CSV file."""
        with open(file=output_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow(
                row=[
                    "program_id",
                    "program_name",
                    "formatted_text",
                    "embedding_vector",
                    "jurisdiction",
                    "assistance_type",
                    "max_benefit",
                    "eligibility",
                    "source",
                ]
            )

            # Write data
            for program in processed_programs:
                original: dict[str, Any] = program["original_data"]
                writer.writerow(
                    row=[
                        program["program_id"],
                        program["program_name"],
                        program["formatted_text"],
                        json.dumps(program["embedding_vector"]),  # Store as JSON string
                        original.get("Jurisdiction", ""),
                        original.get("Assistance Type", ""),
                        original.get("Max Benefit", ""),
                        original.get("Eligibility", ""),
                        original.get("Source", ""),
                    ]
                )

        print(f"Saved {len(processed_programs)} programs to {output_file}")

    def save_embeddings_only(
        self, processed_programs: list[dict[str, Any]], output_file: str
    ) -> None:
        """Save just the embeddings in a format suitable for pgvector."""
        with open(file=output_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow(row=["program_id", "embedding_vector"])

            # Write data
            for program in processed_programs:
                writer.writerow(
                    row=[program["program_id"], json.dumps(program["embedding_vector"])]
                )

        print(f"Saved embeddings to {output_file}")

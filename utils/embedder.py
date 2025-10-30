import csv
import json
import os
import openai
from typing import Any
from openai.types.create_embedding_response import CreateEmbeddingResponse
from utils.convenience import load_secrets

load_secrets()


class NYProgramsEmbedder:
    def __init__(self) -> None:
        self.api_key: str = os.getenv(key="OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable."
            )

        openai.api_key = self.api_key
        self.embedding_model: str = "text-embedding-3-small"

    def format_program_for_embedding(self, program: dict[str, Any]) -> str:
        format_program_string: str = f"""Program: {program.get("Program Name", "")}
        Type: {program.get("Assistance Type", "")}
        Location: {program.get("Jurisdiction", "")}
        Benefit: {program.get("Max Benefit", "")}"""

        return format_program_string

    def format_query_for_embedding(self, query: str) -> str:
        embedding_query_string: str = f"""Program: {query}
        Type: 
        Location: 
        Benefit: """

        return embedding_query_string

    def generate_embedding(self, text: str) -> list[float]:
        try:
            response: CreateEmbeddingResponse = openai.embeddings.create(
                model=self.embedding_model, input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise

    def load_programs(self, json_file_path: str) -> list[dict[str, Any]]:
        if not os.path.exists(json_file_path):
            raise FileNotFoundError(f"File not found: {json_file_path}")
        with open(file=json_file_path, mode="r", encoding="utf-8") as f:
            return json.load(f)

    def process_programs(self, programs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        processed_programs: list[Any] = []

        print(f"Processing {len(programs)} programs...")

        for i, program in enumerate(programs):
            try:
                formatted_text: str = self.format_program_for_embedding(program=program)

                embedding: list[float] = self.generate_embedding(text=formatted_text)

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
        with open(file=output_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

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

            for program in processed_programs:
                original: dict[str, Any] = program["original_data"]
                writer.writerow(
                    row=[
                        program["program_id"],
                        program["program_name"],
                        program["formatted_text"],
                        json.dumps(program["embedding_vector"]),
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
        with open(file=output_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            writer.writerow(row=["program_id", "embedding_vector"])

            for program in processed_programs:
                writer.writerow(
                    row=[program["program_id"], json.dumps(program["embedding_vector"])]
                )

        print(f"Saved embeddings to {output_file}")

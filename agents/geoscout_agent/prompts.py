"""Prompts for the GeoScout agent workflow."""

from typing import Any

from pydantic import BaseModel, Field


class CommuteStructure(BaseModel):
    transit_score: int = Field(description="The transit score for the area")
    transit_summary: str = Field(
        description="A summary of the transit situation in the area"
    )


class CrimeStructure(BaseModel):
    crime_score: int = Field(description="The crime score for the area")
    crime_summary: str = Field(
        description="A summary of the crime situation in the area"
    )


def get_transit_score_prompt(zipcode: int, commute_result: dict[str, Any]) -> str:
    """Prompt for transit score node"""
    return f"""
    User zip code: {zipcode}
    Transit Score Result: {commute_result}

    Provide a summary of what this transit means for property search.

    Return your response in the following JSON format:
    {{
        "transit_score": int,  # A score from 1 (poor) to 10 (excellent)
        "transit_summary": str  # A brief summary of the transit situation in the area
    }}
    """


def get_crime_score_prompt(zipcode: int) -> str:
    """Prompt for crime rate node"""
    return f"""
    Zip Code: {zipcode}

    Provide a summary of what this crime rate means for property search.
    Find crime statistics for a given U.S. ZIP code.
    Return a score from 1 (very low) to 4 (high) based on the latest reliable data.
    Include a summary of the crime situation in the area.
    Cite the source. If no data exists, say so.

    Use the crime index:
    1 - Very Low
    2 - Low
    3 - Moderate
    4 - High

    Return your response in the following JSON format:
    {{
        "crime_score": int,  # A score from 1 (very low) to 4 (high)
        "crime_summary": str  # A brief summary of the crime situation in the area
    }}
    """


def get_synthesizer_prompt(commute_state: dict[str, Any]) -> str:
    """Prompt for synthesis node"""
    return f"""
    I have completed the commute analysis with the following results:
    {commute_state}

    Please format this into a clean, final output that includes:
    1. Commute analysis summary
    2. Crime details summary
    3. Key recommendations

    Make it user-friendly and actionable.
    """

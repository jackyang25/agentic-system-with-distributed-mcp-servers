"""Create server_name server."""

from typing import Any

from fastmcp import FastMCP

math_mcp: FastMCP[Any] = FastMCP(name="EnhancedMathServer")


@math_mcp.tool(name="Addition Function")
def add_numbers(a: float, b: float) -> dict[str, Any]:
    """Add two numbers and return detailed result information.

    This tool provides addition with comprehensive metadata that helps
    AI agents understand the operation and verify results.

    Args:
        a: First number (any real number)
        b: Second number (any real number)

    Returns:
        Dictionary with operation details, result, and metadata
    """
    result: float = a + b
    return {
        "operation": "addition",
        "expression": f"{a} + {b}",
        "result": result,
        "operands": {"a": a, "b": b},
        "operation_type": "arithmetic",
        "properties": {
            "commutative": True,  # a + b = b + a
            "associative": True,  # (a + b) + c = a + (b + c)
            "identity_element": 0,  # a + 0 = a
        },
    }


@math_mcp.tool()
def multiply_numbers(a: float, b: float) -> dict[str, Any]:
    """Multiply two numbers with comprehensive result analysis.

    Args:
        a: First number (multiplicand)
        b: Second number (multiplier)

    Returns:
        Dictionary with multiplication details and mathematical properties
    """
    result = a * b

    # Analyze the result
    analysis = {
        "is_positive": result > 0,
        "is_negative": result < 0,
        "is_zero": result == 0,
        "magnitude": abs(result),
    }

    # Special cases
    special_cases: list[str] = []
    if a == 0 or b == 0:
        special_cases.append("multiplication_by_zero")
    if a == 1:
        special_cases.append("multiplication_by_identity")
    if b == 1:
        special_cases.append("multiplication_by_identity")
    if a == -1:
        special_cases.append("multiplication_by_negative_one")
    if b == -1:
        special_cases.append("multiplication_by_negative_one")

    return {
        "operation": "multiplication",
        "expression": f"{a} × {b}",
        "result": result,
        "operands": {"multiplicand": a, "multiplier": b},
        "analysis": analysis,
        "special_cases": special_cases,
        "properties": {
            "commutative": True,  # a × b = b × a
            "associative": True,  # (a × b) × c = a × (b × c)
            "identity_element": 1,  # a × 1 = a
        },
    }


@math_mcp.tool()
def calculate_percentage(value: float, percentage: float) -> dict[str, Any]:
    """Calculate what percentage of a value represents, with validation.

    Args:
        value: The base value (any real number)
        percentage: The percentage (0-100 for normal percentages)

    Returns:
        Dictionary with percentage calculation and interpretations
    """
    # Validate percentage range (allow negative for calculations)
    if percentage < -1000 or percentage > 1000:
        return {
            "error": "Percentage out of reasonable range (-1000% to 1000%)",
            "provided_percentage": percentage,
            "valid_range": "Typically 0-100, extended range -1000 to 1000 allowed",
        }

    percentage_value: float = (value * percentage) / 100

    # Provide multiple interpretations
    interpretations = {
        "percentage_of_value": f"{percentage}% of {value} is {percentage_value}",
        "fraction_form": f"{percentage}/100 × {value} = {percentage_value}",
        "decimal_form": f"{percentage / 100} × {value} = {percentage_value}",
    }

    # Context about the calculation
    context = {
        "is_increase": percentage > 0 and value > 0,
        "is_decrease": percentage < 0 and value > 0,
        "percentage_greater_than_100": percentage > 100,
        "calculated_value_larger_than_original": abs(percentage_value) > abs(value),
    }

    return {
        "operation": "percentage_calculation",
        "expression": f"{percentage}% of {value}",
        "result": percentage_value,
        "inputs": {"value": value, "percentage": percentage},
        "interpretations": interpretations,
        "context": context,
    }


@math_mcp.resource(uri="resource://server-capabilities")
def get_server_capabilities() -> dict:
    """Get information about this MCP server's mathematical capabilities.

    Returns:
        Dictionary describing available operations and server metadata
    """
    return {
        "server_name": "EnhancedMathServer",
        "version": "1.0.0",
        "capabilities": {
            "basic_arithmetic": ["addition", "multiplication"],
            "percentage_calculations": ["percentage_of_value"],
            "advanced_features": [
                "detailed_operation_metadata",
                "mathematical_property_analysis",
                "input_validation_and_error_handling",
                "special_case_detection",
            ],
        },
        "supported_number_types": ["integers", "floating_point", "negative_numbers"],
        "output_format": "structured_json_with_metadata",
        "error_handling": "graceful_with_detailed_messages",
        "mathematical_properties": {
            "addition": {"commutative": True, "associative": True, "identity": 0},
            "multiplication": {"commutative": True, "associative": True, "identity": 1},
        },
    }


if __name__ == "__main__":
    math_mcp.run(transport="streamable-http", host="0.0.0.0", port=5050)

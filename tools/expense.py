import re
from utils.expensecal import Calculator
from typing import Any, List, Union
from langchain.tools import tool


def _as_float(x: Any) -> float:
    """Coerce tool args: models often send numbers as strings or '$1,200.50'."""
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        cleaned = re.sub(r"[^\d.\-]", "", x.replace(",", ""))
        if cleaned in ("", "-", ".", "-."):
            return 0.0
        return float(cleaned)
    return float(x)


class CalculatorTool:
    def __init__(self):
        self.calculator = Calculator()
        self.calculator_tool_list = self._setup_tools()

    def _setup_tools(self) -> List:
        """Setup all tools for the calculator tool"""

        @tool
        def estimate_total_hotel_cost(
            price_per_night: Union[str, float], total_days: Union[str, float]
        ) -> float:
            """Calculate total hotel cost: nightly rate × nights (accepts numbers or strings like 120 or $120)."""
            p = _as_float(price_per_night)
            d = _as_float(total_days)
            return p * d

        @tool
        def calculate_total_expense(costs: List[Union[str, float]]) -> float:
            """Calculate total expense of the trip from a list of individual costs."""
            return self.calculator.calculate_total(*(_as_float(c) for c in costs))

        @tool
        def calculate_daily_expense_budget(
            total_cost: Union[str, float], days: Union[str, int, float]
        ) -> float:
            """
            Calculate daily expense.
            Requires the total_cost and the number of days.
            """
            return self.calculator.calculate_daily_budget(
                _as_float(total_cost), int(_as_float(days))
            )

        return [
            estimate_total_hotel_cost, 
            calculate_total_expense, 
            calculate_daily_expense_budget
        ]

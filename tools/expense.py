from utils.expensecal import Calculator
from typing import List
from langchain.tools import tool

class CalculatorTool:
    def __init__(self):
        self.calculator = Calculator()
        self.calculator_tool_list = self._setup_tools()

    def _setup_tools(self) -> List:
        """Setup all tools for the calculator tool"""

        @tool
        def estimate_total_hotel_cost(price_per_night: float, total_days: float) -> float:
            """
            Calculate total hotel cost.
            Requires price_per_night and total_days as floats.
            """
            return self.calculator.multiply(price_per_night, total_days)

        @tool
        def calculate_total_expense(costs: List[float]) -> float:
            """
            Calculate total expense of the trip. 
            Provide a list of all individual costs as the 'costs' parameter.
            """
            # We unpack the list using *costs because your Calculator class 
            # likely uses *args in its calculate_total method.
            return self.calculator.calculate_total(*costs)

        @tool
        def calculate_daily_expense_budget(total_cost: float, days: int) -> float:
            """
            Calculate daily expense.
            Requires the total_cost and the number of days.
            """
            return self.calculator.calculate_daily_budget(total_cost, days)

        return [
            estimate_total_hotel_cost, 
            calculate_total_expense, 
            calculate_daily_expense_budget
        ]

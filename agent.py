from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict
import statistics


# --- State Definition ---
class BusinessState(TypedDict):
    daily_data: List[Dict]
    profit: float
    cac_today: float
    cac_yesterday: float
    avg_revenue: float
    avg_cost: float
    alerts: List[str]
    recommendations: List[str]


# --- Input Node ---
def input_node(state: dict) -> BusinessState:
    return {
        "daily_data": state["daily_data"],
        "profit": 0.0,
        "cac_today": 0.0,
        "cac_yesterday": 0.0,
        "avg_revenue": 0.0,
        "avg_cost": 0.0,
        "alerts": [],
        "recommendations": []
    }


# --- Processing Node ---
def processing_node(state: BusinessState) -> BusinessState:
    data = state["daily_data"]
    if len(data) < 2:
        raise ValueError("At least 2 days of data are required")

    today = data[-1]
    yesterday = data[-2]

    # Profit
    profit = today["revenue"] - today["cost"]

    # CAC
    cac_today = today["cost"] / today["customers"]
    cac_yesterday = yesterday["cost"] / yesterday["customers"]
    cac_change = ((cac_today - cac_yesterday) / cac_yesterday) * 100

    # Average revenue and cost (excluding today)
    avg_revenue = statistics.mean([d["revenue"] for d in data[:-1]])
    avg_cost = statistics.mean([d["cost"] for d in data[:-1]])

    alerts = []
    if cac_change > 20:
        alerts.append(f"CAC increased by {cac_change:.2f}%")

    return {
        **state,
        "profit": profit,
        "cac_today": cac_today,
        "cac_yesterday": cac_yesterday,
        "avg_revenue": avg_revenue,
        "avg_cost": avg_cost,
        "alerts": alerts,
    }


# --- Recommendation Node ---
def recommendation_node(state: BusinessState) -> BusinessState:
    today = state["daily_data"][-1]
    recommendations = []

    if state["profit"] < 0:
        recommendations.append("Reduce costs if profit is negative")

    if state["cac_today"] > state["cac_yesterday"] * 1.2:
        recommendations.append("Review marketing campaigns due to rising CAC")

    if today["revenue"] > state["avg_revenue"]:
        recommendations.append("Consider increasing advertising budget as sales trend is growing")

    return {
        **state,
        "recommendations": recommendations
    }


# --- Build LangGraph ---
def build_graph():
    builder = StateGraph(BusinessState)
    builder.add_node("input", input_node)
    builder.add_node("processing", processing_node)
    builder.add_node("recommendation", recommendation_node)

    builder.set_entry_point("input")
    builder.add_edge("input", "processing")
    builder.add_edge("processing", "recommendation")
    builder.add_edge("recommendation", END)

    return builder.compile()

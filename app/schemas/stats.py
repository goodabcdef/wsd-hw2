# app/schemas/stats.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class DailySalesResponse(BaseModel):
    date: str
    total_sales: float
    order_count: int

class TopSellerResponse(BaseModel):
    title: str
    total_sold: int
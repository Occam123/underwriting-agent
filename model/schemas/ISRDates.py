from typing import List
from pydantic import BaseModel


class Date(BaseModel):
    value: str
    context: str


class QuotationDate(BaseModel):
    date: Date
    reasoning_steps: List[str]


class InceptionDate(BaseModel):
    date: Date
    reasoning_steps: List[str]


class ISRDates(BaseModel):
    quotation_date: QuotationDate
    inception_date: InceptionDate

from pydantic import BaseModel


class Date(BaseModel):
    value: str
    source: str


class ISRDates(BaseModel):
    quotation_date: Date
    inception_date: Date

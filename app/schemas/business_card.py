from pydantic import BaseModel


class BusinessCardCreate(BaseModel):
    subdomain: str
    title: str
    description: str
    links: str


class BusinessCardResponse(BaseModel):
    subdomain: str
    title: str
    description: str
    links: str

    class Config:
        orm_mode = True
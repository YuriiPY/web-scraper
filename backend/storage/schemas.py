from sqlalchemy import Column, Integer, String, Text
from storage.database import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    author = Column(String)
    link = Column(String)
    published_date = Column(String)
    content = Column(Text)
    pdf_path = Column(String)

    @property
    def as_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "link": self.link,
            "published_date": self.published_date,
            "content": self.content,
            "pdf_path": self.pdf_path
        }

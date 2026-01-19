from sqlalchemy import and_
from storage.database import SessionLocal
from storage.schemas import Article


def process_article_data(article_data, content_text, pdf_path):
    with SessionLocal() as session:
        existing_article = session.query(Article).filter(
            and_(
                Article.title == article_data.get("title"),
                Article.author == article_data.get("author"),
                Article.published_date == article_data.get("published_date"),
            )
        ).first()

        if existing_article:
            return existing_article.as_dict
        new_article = Article(
            title=article_data.get("title"),
            author=article_data.get("author"),
            link=article_data.get("link"),
            published_date=article_data.get("published_date"),
            content=content_text,
            pdf_path=pdf_path
        )
        
        session.add(new_article)
        session.commit()
        session.refresh(new_article)

        return new_article.as_dict

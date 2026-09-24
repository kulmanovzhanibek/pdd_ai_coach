from pgvector.sqlalchemy import Vector
from sqlalchemy import Computed, ForeignKey, Index
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class RuleRow(Base):
    __tablename__ = "rules"
    __table_args__ = (Index("ix_rules_tsv", "tsv", postgresql_using="gin"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(unique=True)
    text: Mapped[str]
    chapter_number: Mapped[int]
    chapter_title: Mapped[str]
    note: Mapped[str] = mapped_column(default="")
    tsv: Mapped[str] = mapped_column(
        TSVECTOR,
        Computed("to_tsvector('russian', text)", persisted=True),
    )
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536), nullable=True)

class RuleChunk(Base):
    __tablename__ = "rule_chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    rule_id: Mapped[int] = mapped_column(ForeignKey("rules.id", ondelete="CASCADE"))
    position: Mapped[int]
    text: Mapped[str]
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536), nullable=True)
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Text, BigInteger, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class ModelInfo(Base):
    __tablename__ = "model_info"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    file_path: Mapped[str] = mapped_column(String(256), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class UserCurrentModel(Base):
    __tablename__ = "user_current_model"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    model_id: Mapped[int] = mapped_column(ForeignKey("model_info.id"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)


class DetectionRecord(Base):
    __tablename__ = "detection_records"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    image_url: Mapped[str] = mapped_column(String(256), nullable=False)
    result_image_url: Mapped[str] = mapped_column(String(256), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    defects: Mapped[list["Defect"]] = relationship(back_populates="record", cascade="all, delete-orphan")


class Defect(Base):
    __tablename__ = "defects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    record_id: Mapped[str] = mapped_column(String(32), ForeignKey("detection_records.id"), nullable=False)
    class_name: Mapped[str] = mapped_column("class", String(64), nullable=False)
    confidence: Mapped[float] = mapped_column(nullable=False)
    bbox_x: Mapped[float] = mapped_column(nullable=False)
    bbox_y: Mapped[float] = mapped_column(nullable=False)
    bbox_width: Mapped[float] = mapped_column(nullable=False)
    bbox_height: Mapped[float] = mapped_column(nullable=False)

    record: Mapped["DetectionRecord"] = relationship(back_populates="defects")

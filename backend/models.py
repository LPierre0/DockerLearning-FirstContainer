from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    theme_key = Column(String, nullable=False)  # "pierre" | "partner"
    target_weight_kg = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    workouts = relationship("Workout", back_populates="user")
    custom_exercises = relationship("Exercise", back_populates="creator")
    sent_boosts = relationship("Boost", foreign_keys="Boost.from_user_id", back_populates="sender")
    received_boosts = relationship("Boost", foreign_keys="Boost.to_user_id", back_populates="recipient")
    favorite_templates = relationship("FavoriteTemplate", back_populates="user")
    body_measurements = relationship("BodyMeasurement", back_populates="user")


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    muscle_group = Column(String, nullable=False)
    is_custom = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    photo_filename = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship("User", back_populates="custom_exercises")
    sets = relationship("WorkoutSet", back_populates="exercise")


class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False)  # Push/Pull/Legs/Full Body/Cardio/Custom
    name = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="workouts")
    sets = relationship("WorkoutSet", back_populates="workout", cascade="all, delete-orphan")


class WorkoutSet(Base):
    __tablename__ = "workout_sets"

    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(Integer, ForeignKey("workouts.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    set_number = Column(Integer, nullable=False)
    weight_kg = Column(Float, nullable=True)
    reps = Column(Integer, nullable=True)
    rpe = Column(Integer, nullable=True)  # 1-10
    status = Column(String, default="pending")  # pending | done | failed
    logged_at = Column(DateTime, default=datetime.utcnow)
    # Cardio-specific fields
    duration_seconds = Column(Integer, nullable=True)
    resistance = Column(Integer, nullable=True)
    calories = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)

    workout = relationship("Workout", back_populates="sets")
    exercise = relationship("Exercise", back_populates="sets")


class BodyWeight(Base):
    __tablename__ = "body_weights"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    weight_kg = Column(Float, nullable=False)
    logged_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")


class BodyMeasurement(Base):
    __tablename__ = "body_measurements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    chest_cm = Column(Float, nullable=True)
    waist_cm = Column(Float, nullable=True)
    hips_cm = Column(Float, nullable=True)
    arm_cm = Column(Float, nullable=True)
    thigh_cm = Column(Float, nullable=True)
    calf_cm = Column(Float, nullable=True)
    logged_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="body_measurements")


class Boost(Base):
    __tablename__ = "boosts"

    id = Column(Integer, primary_key=True, index=True)
    from_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    to_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(String, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)

    sender = relationship("User", foreign_keys=[from_user_id], back_populates="sent_boosts")
    recipient = relationship("User", foreign_keys=[to_user_id], back_populates="received_boosts")


class FavoriteTemplate(Base):
    __tablename__ = "favorite_templates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    workout_type = Column(String, nullable=False)  # Push/Pull/Legs/Full Body/Cardio/Custom
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="favorite_templates")

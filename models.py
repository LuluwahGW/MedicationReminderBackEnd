from sqlalchemy import Column,String,Integer,Float,func,Table,ForeignKey,Boolean,DateTime,Enum
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime


Base = declarative_base()


class FrequencyEnum(Enum):
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

user_caregiver = Table(
    'user_caregiver',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('cg_id', Integer, ForeignKey('caregivers.id'))
)


class User(Base):
    __tablename__ = 'users'
    id= Column(Integer, primary_key=True, index=True)
    email = Column(String(50), unique=True, nullable=False)
    password = Column(String(50), nullable=False)
    created_at = Column(datetime(timezone=True), server_default=func.now())
    updated_at = Column(datetime(timezone=True),onupdate=func.now())
    
    caregivers = relationship("CareGiver", secondary=user_caregiver, back_populates="users")
    medication = relationship("Medication", back_populates="user")
    reminders = relationship("Reminder", back_populates="user")

class CareGiver(Base):
    __tablename__ = 'caregivers'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer,ForeignKey('users.id'),nullable=False)
    cg_id = Column(Integer,ForeignKey('users.id'),nullable=False)

    user = relationship("User",foreign_keys=[user_id],backref="assigned-caregiver")
    caregiver = relationship("User",foreign_keys=[cg_id],backref="assigned_users")


class Medication(Base):
    __tablename__ = 'medications'  

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    name = Column(String(50), nullable=False)
    dosage = Column(String(10), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    archived = Column(Boolean, default=False)

    user = relationship("User", foreign_keys=[user_id],back_populates="medications")

class Reminder(Base):
    __tablename__ = 'reminders'
    id = Column(Integer,primary_key=True,index=True)
    medication_id = Column(Integer,ForeignKey('medications.id'),nullable=False)
    user_id = Column(Integer,ForeignKey('users.id'),nullable=False)
    name = Column(String(50), nullable=False)
    reminder_time = Column(DateTime,nullable=False)
    frequency = Column(Enum(FrequencyEnum), nullable=False,default=FrequencyEnum.ONCE)
    message = Column(String(100),nullable=False)
    isTaken = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True),onupdate=func.now())

    medication = relationship("Medication", foreign_keys=[medication_id])
    user = relationship("User", foreign_keys=[user_id], back_populates="reminders")

class MotivationText(Base):
   __tablename__ ='motivation_text'
   message_id = Column(Integer,primary_key=True,nullable=False)
   message_text = Column(String(255),nullable=False)

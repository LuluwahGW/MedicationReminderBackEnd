from sqlalchemy import Column,String,Integer,func,ForeignKey,Boolean,DateTime
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SqlEnum
import enum
from database_utilis_related.database import Base 





class FrequencyEnum(enum.Enum):
    ONCE = "ONCE"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"



class CaregiverStatus(enum.Enum):
    PENDING = "PENDING"    # patient sent an invitation, caregiver has not answered
    ACCEPTED = "ACCEPTED"  # caregiver agreed; they can now view the patient's medications


class User(Base):
    __tablename__ = 'users'
    id= Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(30))
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True),onupdate=func.now())
    
   
    medications = relationship("Medication", back_populates="user")
    reminders = relationship("Reminder", back_populates="user")

class CareGiver(Base):
    __tablename__ = 'caregivers'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer,ForeignKey('users.id'),nullable=False)
    cg_id = Column(Integer,ForeignKey('users.id'),nullable=False)
    status = Column(SqlEnum(CaregiverStatus), nullable=False,
                    default=CaregiverStatus.PENDING, server_default=CaregiverStatus.PENDING.name)

    user = relationship("User",foreign_keys=[user_id],backref="assigned_caregiver")
    caregiver = relationship("User",foreign_keys=[cg_id],backref="assigned_users")


class CaregiverInvite(Base):
    """A shareable, single-use link a patient hands to someone they want as caregiver.

    Only a SHA-256 hash of the token is stored, so a copy of the database can't
    be used to accept invitations. The caregiver gets access only after they
    sign in and explicitly accept.
    """
    __tablename__ = 'caregiver_invites'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    token_hash = Column(String(64), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True))

    patient = relationship("User", foreign_keys=[patient_id])


class Medication(Base):
    __tablename__ = 'medications'  

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    name = Column(String(50), nullable=False)
    dosage = Column(String(10), nullable=False)
    archived = Column(Boolean, default=False)

    user = relationship("User", back_populates="medications")
    reminders = relationship("Reminder", back_populates="medication", cascade="all, delete")

class Reminder(Base):
    __tablename__ = 'reminders'
    id = Column(Integer,primary_key=True,index=True)
    medication_id = Column(Integer,ForeignKey('medications.id'),nullable=False)
    user_id = Column(Integer,ForeignKey('users.id'),nullable=False)
    name = Column(String(50), nullable=False)
    reminder_time = Column(DateTime,nullable=False)
    frequency = Column(SqlEnum(FrequencyEnum), nullable=False,default=FrequencyEnum.ONCE)
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



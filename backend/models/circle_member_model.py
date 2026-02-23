from sqlalchemy import Column, Integer, Enum as SQLEnum, ForeignKey
from database import Base
import enum
class Role(str, enum.Enum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"  # Note: spec has "MEMBER" -- was MEMER
class CircleMember(Base):
    __tablename__ = "circle_members"
    id = Column(Integer, primary_key=True, index=True)
    circle_id = Column(Integer, ForeignKey("support_circles.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(SQLEnum(Role), default=Role.MEMBER)
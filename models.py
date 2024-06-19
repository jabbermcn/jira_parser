from sqlalchemy import (
    Column,
    SMALLINT,
    VARCHAR,
    Enum,
    CheckConstraint,
    ForeignKey,
    Date,
    inspect,
    ForeignKeyConstraint,
    text,
    BIGINT,
    BOOLEAN, DateTime,
)
from sqlalchemy.dialects.postgresql import INTERVAL
from sqlalchemy.orm import DeclarativeBase, relationship

from enums import IssueStatus, IssueType, IssuePriority, UserRole, CalendarType

__all__ = [
    "Base",
    "UserProject",
    "DirectionProject",
    "User",
    "Position",
    "Grade",
    "Department",
    "Project",
    "Issue",
    "UserProjectLoad",
    "EmploymentCalendar",
    "Worklog",
    "IssueStatusLog"
]


class Base(DeclarativeBase):
    pass


class UserProject(Base):
    __tablename__ = "user_projects"

    user_id = Column(
        SMALLINT,
        ForeignKey(column="users.id", ondelete="RESTRICT", onupdate="CASCADE"),
        primary_key=True,
        index=True
    )
    project_id = Column(
        SMALLINT,
        ForeignKey(column="projects.id", ondelete="RESTRICT", onupdate="CASCADE"),
        primary_key=True,
        index=True
    )


class DirectionProject(Base):
    __tablename__ = "direction_projects"

    direction_id = Column(
        SMALLINT,
        ForeignKey(column="directions.id", ondelete="RESTRICT", onupdate="CASCADE"),
        primary_key=True,
        index=True
    )
    project_id = Column(
        SMALLINT,
        ForeignKey(column="projects.id", ondelete="RESTRICT", onupdate="CASCADE"),
        primary_key=True,
        index=True
    )


class Department(Base):
    __tablename__ = "departments"
    __table_args__ = (
        CheckConstraint(sqltext="length(name) >= 2", name="name_min_length"),
    )

    id = Column(SMALLINT, primary_key=True, index=True)
    name = Column(VARCHAR(length=128), nullable=False)

    directions = relationship(argument="Direction", back_populates="department")

    def __str__(self):
        return self.name


class Direction(Base):
    __tablename__ = "directions"
    __table_args__ = (
        CheckConstraint(sqltext="length(name) >= 2", name="name_min_length"),
    )

    id = Column(SMALLINT, primary_key=True)
    name = Column(VARCHAR(length=128), nullable=False, unique=True)
    department_id = Column(
        SMALLINT,
        ForeignKey(column="departments.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        index=True
    )

    projects = relationship(
        argument="Project",
        secondary=inspect(DirectionProject).local_table,
        back_populates="directions"
    )
    department = relationship(argument="Department", back_populates="directions")
    positions = relationship(argument="Position", back_populates="direction")

    def __str__(self):
        return self.name


class Position(Base):
    __tablename__ = "positions"
    __table_args__ = (
        CheckConstraint(sqltext="length(name) >= 2", name="name_min_length"),
    )

    id = Column(SMALLINT, primary_key=True)
    name = Column(VARCHAR(length=128), nullable=False, unique=True)
    direction_id = Column(
        SMALLINT,
        ForeignKey(column="directions.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        index=True
    )

    direction = relationship(argument="Direction", back_populates="positions")
    users = relationship(argument="User", back_populates="position")

    def __str__(self) -> str:
        return self.name


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(sqltext="length(first_name) >= 2", name="first_name_min_length"),
        CheckConstraint(sqltext="length(last_name) >= 2", name="last_name_min_length"),
        CheckConstraint(sqltext="length(email) >= 5", name="email_min_length"),
    )

    id = Column(SMALLINT, primary_key=True)
    email = Column(VARCHAR(length=128), nullable=False, unique=True)
    first_name = Column(VARCHAR(length=128), nullable=False)
    last_name = Column(VARCHAR(length=128), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.USER)
    position_id = Column(
        SMALLINT,
        ForeignKey(column="positions.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        index=True
    )
    grade_id = Column(
        SMALLINT,
        ForeignKey(column="grades.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=True,
        index=True
    )
    photo = Column(VARCHAR, nullable=True)
    telegram_id = Column(BIGINT, nullable=False, unique=True)
    tg_first_name = Column(VARCHAR(length=128), nullable=True)
    tg_last_name = Column(VARCHAR(length=128), nullable=True)
    tg_username = Column(VARCHAR(length=128), nullable=True)
    is_new = Column(BOOLEAN, default=True, nullable=False)

    position = relationship(argument="Position", back_populates="users")
    grade = relationship(argument="Grade", back_populates="users")
    developer_issues = relationship(argument="Issue", foreign_keys="Issue.developer_id", back_populates="developer")
    reviewer_issues = relationship(argument="Issue", foreign_keys="Issue.reviewer_id", back_populates="reviewer")
    qa_issues = relationship(argument="Issue", foreign_keys="Issue.qa_id", back_populates="qa")
    worklog = relationship(argument="Worklog", back_populates="user")
    projects = relationship(argument="Project", secondary=inspect(UserProject).local_table, back_populates="users")
    loads = relationship(
        argument="UserProjectLoad",
        secondary=UserProject.__table__,
        viewonly=True,
        uselist=True,
        overlaps="projects",
        primaryjoin="User.id == UserProject.user_id",
        secondaryjoin="and_(UserProjectLoad.user_id == UserProject.user_id, "
                      "UserProjectLoad.project_id == UserProject.project_id)"
    )
    employment_calendars = relationship(argument="EmploymentCalendar", back_populates="user")

    def __str__(self) -> str:
        return self.full_name

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Grade(Base):
    __tablename__ = "grades"
    __table_args__ = (
        CheckConstraint(sqltext="length(name) >= 2", name="name_min_length"),
    )

    id = Column(SMALLINT, primary_key=True)
    name = Column(VARCHAR(length=128), nullable=False, unique=True)

    users = relationship(argument="User", back_populates="grade")

    def __str__(self):
        return self.name


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = (
        CheckConstraint(sqltext="length(name) >= 2", name="name_min_length"),
        CheckConstraint(sqltext="length(key) >= 2", name="key_min_length"),
    )

    id = Column(SMALLINT, primary_key=True)
    key = Column(VARCHAR(length=128), nullable=False, unique=True)
    name = Column(VARCHAR(length=128), nullable=False, unique=True)
    is_active = Column(BOOLEAN, default=False, nullable=False)
    priority = Column(SMALLINT, default=1, nullable=False)

    users = relationship(
        argument="User",
        secondary=inspect(UserProject).local_table,
        back_populates="projects",
        primaryjoin="Project.id == UserProject.project_id",
        secondaryjoin="UserProject.user_id == User.id",
        overlaps="loads"
    )
    directions = relationship(
        argument="Direction",
        secondary=inspect(DirectionProject).local_table,
        back_populates="projects"
    )
    issues = relationship(argument="Issue", back_populates="project")

    def __str__(self):
        return self.name


class Issue(Base):
    __tablename__ = "issues"
    __table_args__ = (
        CheckConstraint(sqltext="length(key) >= 2", name="key_min_length"),
    )

    id = Column(BIGINT, primary_key=True)
    name = Column(VARCHAR, nullable=False, unique=False)
    key = Column(VARCHAR(length=128), nullable=False, unique=True)
    type = Column(Enum(IssueType), default=IssueType.TASK, nullable=False, server_default="TASK")
    priority = Column(Enum(IssuePriority), default=IssuePriority.LOW, nullable=False, server_default="LOW")
    developer_id = Column(
        SMALLINT,
        ForeignKey(column="users.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=True,
        index=True
    )
    reviewer_id = Column(
        SMALLINT,
        ForeignKey(column="users.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=True,
        index=True
    )
    qa_id = Column(
        SMALLINT,
        ForeignKey(column="users.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=True,
        index=True
    )
    status = Column(Enum(IssueStatus), default=IssueStatus.DONE, nullable=False, server_default="DONE")
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    project_id = Column(
        SMALLINT,
        ForeignKey(column=Project.id, onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False
    )
    parent_issue_id = Column(
        BIGINT,
        ForeignKey(column="issues.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=True,
        index=True
    )

    developer = relationship(
        argument="User", foreign_keys=[developer_id], remote_side=User.id, back_populates="developer_issues"  # noqa
    )
    reviewer = relationship(
        argument="User", foreign_keys=[reviewer_id], remote_side=User.id, back_populates="reviewer_issues"  # noqa
    )
    qa = relationship(
        argument="User", foreign_keys=[qa_id], remote_side=User.id, back_populates="qa_issues"  # noqa
    )
    worklog = relationship(argument="Worklog", back_populates="issue")
    project = relationship(argument=Project, back_populates="issues")
    parent_issue = relationship(argument="Issue", remote_side=[id], back_populates="bugs")  # noqa
    bugs = relationship(argument="Issue", back_populates="parent_issue")
    status_logs = relationship(argument="IssueStatusLog", back_populates="issue")

    def __str__(self):
        return self.key


class IssueStatusLog(Base):
    __tablename__ = "issue_status_logs"

    id = Column(SMALLINT, primary_key=True)
    issue_id = Column(
        BIGINT,
        ForeignKey(column="issues.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True
    )
    status = Column(Enum(IssueStatus), default=IssueStatus.DONE, nullable=False, server_default="DONE")
    changed_at = Column(DateTime, nullable=False)

    issue = relationship(argument="Issue", back_populates="status_logs")


class Worklog(Base):
    __tablename__ = "worklog"
    __table_args__ = (
        CheckConstraint(
            text("EXTRACT(EPOCH FROM hour) >= 0"),
            name="hour_greater_than_zero"
        ),
    )

    id = Column(SMALLINT, primary_key=True)
    issue_id = Column(
        BIGINT,
        ForeignKey(column="issues.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        index=True
    )
    user_id = Column(
        SMALLINT,
        ForeignKey(column="users.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        index=True
    )
    hour = Column(INTERVAL, nullable=False)
    date_created = Column(Date, nullable=False)

    issue = relationship(argument="Issue", back_populates="worklog")
    user = relationship(argument="User", back_populates="worklog")


class EmploymentCalendar(Base):
    __tablename__ = "employment_calendars"

    id = Column(SMALLINT, primary_key=True)
    user_id = Column(
        SMALLINT,
        ForeignKey(column="users.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        index=True
    )
    day = Column(Date, nullable=False)
    hour = Column(INTERVAL, nullable=False)
    type = Column(Enum(CalendarType), nullable=True)

    user = relationship(argument="User", back_populates="employment_calendars")

    def __str__(self):
        return self.id


class UserProjectLoad(Base):
    __tablename__ = "user_project_loads"
    __table_args__ = (
        CheckConstraint(sqltext="load >= 0 AND load <= 280", name="load_range"),
        ForeignKeyConstraint(
            columns=["user_id", "project_id"],
            refcolumns=[UserProject.user_id, UserProject.project_id],
            onupdate="CASCADE",
            ondelete="RESTRICT"
        )
    )

    id = Column(SMALLINT, primary_key=True)
    user_id = Column(
        SMALLINT,
        nullable=False,
        index=True
    )
    project_id = Column(
        SMALLINT,
        nullable=False,
        index=True
    )
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    load = Column(SMALLINT, nullable=False)

    project = relationship(
        argument=Project,
        secondary=UserProject.__table__,
        primaryjoin="UserProjectLoad.project_id == UserProject.project_id",
        secondaryjoin="Project.id == UserProject.project_id",
        viewonly=True,
        uselist=False
    )

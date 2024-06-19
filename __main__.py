import json
from datetime import datetime, timedelta

from sqlalchemy import select, insert, update
from sqlalchemy.orm import Session

from models import Issue, User, Worklog
from settings import jira_client, session_maker
from utils import get_valid_status, change_to_valid_email


def data_from_json(file_name):
    with open(file_name, "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    issues_data = data_from_json("csvjson (10).json")
    issues_count = len(issues_data)
    print(f"issues count - {issues_count}")
    remaining_issues = issues_count
    for _ in issues_data:
        with session_maker() as session:  # type: Session
            issue = session.scalar(statement=select(Issue).filter(Issue.key == _.get("Key")))
            print(issue.id if issue else None)
            if issue:
                issue_worklogs = session.scalars(
                    statement=select(
                        Worklog.id,
                        Worklog.date_created,
                        Worklog.hour
                    ).filter(Worklog.issue_id == issue.id)
                ).unique().all()
                print(f"issue_worklogs from db - {issue_worklogs}")
            else:
                issue_worklogs = []
            response = jira_client.client.request(
                method="GET",
                url=f"/rest/api/3/issue/{_.get("Key")}"
            )
            issue_data = response.json()
            parent_issue_id = None
            if issue_data.get("fields"):
                parent = issue_data.get("fields").get("parent")

                if parent and parent.get("id"):
                    parent_issue_id = int(parent.get("id"))

                    issuetype_name = parent.get("fields", {}).get("issuetype", {}).get("name", "")
                    if issuetype_name.upper() in {"ЭПИК", "EPIC"}:
                        parent_issue_id = int(parent.get("id"))

            if issue is None:

                try:
                    session.execute(
                        insert(Issue).values(
                            id=int(issue_data.get("id")),
                            name=issue_data.get("fields").get("summary"),
                            key=issue_data.get("key"),
                            type="TASK" if issue_data.get("fields").get("issuetype").get("name").upper() in {
                                "ЗАДАЧА", "TASK"
                            } else "BUG",
                            priority=issue_data.get("fields").get("priority").get("name").upper(),
                            developer_id=select(User.id).filter(
                                User.email == issue_data.get("fields").get("assignee").get("emailAddress")
                            ).scalar_subquery() if issue_data.get("fields").get("assignee") else None,
                            status=get_valid_status(status=issue_data.get("fields").get("status").get("name")),
                            start_date=datetime.fromisoformat(issue_data.get("fields").get("created")).date(),
                            end_date=datetime.fromisoformat(
                                issue_data.get("fields").get("duedate")
                            ).date() if issue_data.get("fields").get("duedate") else None,
                            project_id=int(issue_data.get("fields").get("project").get("id")),
                            parent_issue_id=parent_issue_id
                        )
                    )
                    session.commit()
                    print("Issue inserted successful!")
                except Exception as e:
                    print(e)
                finally:
                    session.close()

                response = jira_client.client.request(
                    method="GET",
                    url=f"/rest/api/3/issue/{_.get("Key")}/worklog"
                )
                worklogs_data = response.json()
                worklogs = worklogs_data.get("worklogs")
                if worklogs is not None:
                    print(f"worklogs from response - {worklogs}")
                    worklog_values = []
                    for worklog in worklogs:
                        email = change_to_valid_email(data=worklog)
                        if email is not None and worklog.get("timeSpentSeconds") != 0:
                            if int(worklog.get("id")) not in issue_worklogs:
                                worklog_data = {
                                    "id": int(worklog.get("id")),
                                    "issue_id": int(worklog.get("issueId")),
                                    "user_id": select(User.id).filter(User.email == email).scalar_subquery(),
                                    "hour": timedelta(seconds=worklog.get("timeSpentSeconds")),
                                    "date_created": datetime.fromisoformat(worklog.get("started")).date()
                                }
                                worklog_values.append(worklog_data)
                            else:
                                print(f"worklog id: {int(worklog.get("id"))} already exists")
                    if worklog_values:
                        try:
                            session.execute(statement=insert(Worklog).values(worklog_values))
                            session.commit()
                            print(f"worklogs inserted successful: {worklog_values}")
                        except Exception as e:
                            print(e)
                        finally:
                            session.close()
                    worklog_values.clear()
            else:
                try:
                    session.execute(
                        update(Issue).values(parent_issue_id=parent_issue_id).where(Issue.id == issue.id)
                    )
                except Exception as e:
                    print(e)
                finally:
                    session.close()
                response = jira_client.client.request(
                    method="GET",
                    url=f"/rest/api/3/issue/{_.get("Key")}/worklog"
                )
                worklogs_data = response.json()
                worklogs = worklogs_data.get("worklogs")
                print(f"worklogs from response - {worklogs}")
                worklog_values = []
                for worklog in worklogs:
                    email = change_to_valid_email(data=worklog)
                    if email is not None and worklog.get("timeSpentSeconds"):
                        if int(worklog.get("id")) not in issue_worklogs:
                            worklog_data = {
                                "id": int(worklog.get("id")),
                                "issue_id": int(worklog.get("issueId")),
                                "user_id": select(User.id).filter(User.email == email).scalar_subquery(),
                                "hour": timedelta(seconds=worklog.get("timeSpentSeconds")),
                                "date_created": datetime.fromisoformat(worklog.get("started")).date()
                            }
                            worklog_values.append(worklog_data)
                        else:
                            print(f"worklog id: {int(worklog.get("id"))} already exists")
                if worklog_values:
                    try:
                        session.execute(statement=insert(Worklog).values(worklog_values))
                        session.commit()
                        print(f"worklogs inserted successful: {worklog_values}")
                    except Exception as e:
                        print(e)
                    finally:
                        session.close()
                worklog_values.clear()

        print(f"Remaining issues: {remaining_issues - 1}")
        remaining_issues -= 1


def add_users_in_db():
    with session_maker() as session:  # type: Session
        session.execute(
            insert(User).values(
                email="a.krasnova@atomgroup.io",
                first_name="Aliaksandra",
                last_name="Krasnova",
                role="USER",
                position_id=8,
                telegram_id=11,
                is_new=False
            )
        )
        session.commit()
        print("Users added successful")


if __name__ == '__main__':
    main()
    # add_users_in_db()

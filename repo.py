from database import get_db_connection


class TaskRepository:
    def get_all(self):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, title, done FROM tasks ORDER BY id ASC;")
                return cur.fetchall()


    def get_by_id(self, task_id: int):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, title, done FROM tasks WHERE id = %s;", (task_id,))
                return cur.fetchone()


    def create(self, title: str):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id, title, done;",
                    (title, False)
                )
                new_task = cur.fetchone()
                conn.commit()
                return new_task

    
    def update(self, task_id: int, title: str | None, done: bool | None):
        # Handle partial updates gracefully
        current = self.get_by_id(task_id)
        if not current:
            return None

        new_title = title if title is not None else current["title"]
        new_done = done if done is not None else current["done"]

        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING id, title, done;",
                    (new_title, new_done, task_id),
                )
                updated = cur.fetchone()
                conn.commit()
                return updated



    def delete(self, task_id: int):
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM tasks WHERE id = %s RETURNING id;", (task_id,))
                deleted = cur.fetchone()
                conn.commit()
                return deleted is not None


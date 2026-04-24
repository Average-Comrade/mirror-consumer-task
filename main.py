from redis_queue import Consumer
from redis import Redis
from neo4j_birtix_db_repo.repos import TaskRepository
from neo4j_birtix_db_repo.models import TaskPayload
from neo4j import GraphDatabase

URI = "bolt://mirror-db:7687"
AUTH = ("neo4j", "password")
redis = Redis('queue', 6379, decode_responses=True)
driver = GraphDatabase.driver(URI, auth=AUTH)


class TaskConsumer(Consumer):
    def __init__(self, task_repo: TaskRepository, redis, stream_key, group_name, consumer, buffer_size, fulsh_time, ):
        super().__init__(redis, stream_key, group_name, consumer, buffer_size, fulsh_time)
        self.repo = task_repo

    def handle_batch(self, batch):
        self.repo.upsert_batch([TaskPayload(**task_tuple[1]) for task_tuple in batch])


task_repo = TaskRepository(driver)

task_consumer = TaskConsumer(task_repo, redis, "tasks", "group", "tasks", 1000, 500)

task_consumer.run()

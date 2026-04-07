import sqlite3
from neo4j import GraphDatabase

SQLITE_DB_PATH = "social_network.db"

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "12345678"

sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
sqlite_cursor = sqlite_conn.cursor()

neo4j_driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD)
)

def clear_database():
    with neo4j_driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")

def migrate_users():
    print("Migrating users...")
    sqlite_cursor.execute("SELECT id, username, name FROM users")

    with neo4j_driver.session() as session:
        for user_id, username, name in sqlite_cursor.fetchall():
            session.run(
                """
                CREATE (:User {
                    id: $id,
                    username: $username,
                    name: $name
                })
                """,
                id=user_id,
                username=username,
                name=name
            )


def migrate_posts():
    print("Migrating posts...")
    sqlite_cursor.execute("SELECT id, user_id, content, timestamp FROM posts")

    with neo4j_driver.session() as session:
        for post_id, user_id, content, timestamp in sqlite_cursor.fetchall():
            session.run(
                """
                MATCH (u:User {id: $user_id})
                CREATE (p:Post {
                    id: $id,
                    content: $content,
                    timestamp: $timestamp
                })
                CREATE (u)-[:POSTED]->(p)
                """,
                id=post_id,
                user_id=user_id,
                content=content,
                timestamp=timestamp
            )


def migrate_follows():
    print("Migrating follows...")
    sqlite_cursor.execute("SELECT follower_id, followee_id FROM followers")

    with neo4j_driver.session() as session:
        for follower_id, followee_id in sqlite_cursor.fetchall():
            session.run(
                """
                MATCH (follower:User {id: $follower_id})
                MATCH (followee:User {id: $followee_id})
                MERGE (follower)-[:FOLLOWS]->(followee)
                """,
                follower_id=follower_id,
                followee_id=followee_id
            )

def main():
    print("Starting migration...")
    
    clear_database()

    migrate_users()
    migrate_posts()
    migrate_follows()

    print("Migration complete!")


if __name__ == "__main__":
    main()
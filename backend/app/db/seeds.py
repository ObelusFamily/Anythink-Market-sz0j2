import asyncio
import os
import pathlib
import random
import string
from typing import List

import asyncpg
from app.db.repositories.items import ItemsRepository
from app.db.repositories.users import UsersRepository
from app.models.domain.users import UserInDB
from app.services.items import get_slug_for_item

file_path = os.path.dirname(os.path.abspath(__file__))

MAX_SEED_SIZE = 100
SEED_SIZE = 100

MY_DATABASE_CONNECTION = "postgresql://postgres:@postgres-python:5432/anythink-market"

# ITEMS AND TAGS
tags = [
    line.strip().split(",")
    for line in open(
        pathlib.Path(file_path).joinpath("./seed_db/tags").as_posix(), "r"
    ).readlines()
]
first_tags = sum(tags, [])[:MAX_SEED_SIZE]
tags = [[tag for tag in tag_list if tag in first_tags] for tag_list in tags]
tags = [tag_list if len(tag_list) else None for tag_list in tags]
titles = [
    line.strip()
    for line in open(
        pathlib.Path(file_path).joinpath("./seed_db/names").as_posix(), "r"
    ).readlines()
]
image_urls = [
    line.strip()
    for line in open(
        pathlib.Path(file_path).joinpath("./seed_db/images").as_posix(), "r"
    ).readlines()
]

# USERS
mails_servers = ["hotmail", "gmail", "protonmail", "walla", "stam"]
username_lengths = list(range(6, 10))
passwords_lengths = list(range(6, 10))


def get_random_string(length):
    # choose from all lowercase letter
    legit_chars = string.ascii_lowercase + string.digits
    result_str = "".join(random.choice(legit_chars) for i in range(length))
    return result_str


usernames = [
    get_random_string(random.choice(username_lengths)) for _ in range(MAX_SEED_SIZE)
]
passwords = [
    get_random_string(random.choice(passwords_lengths)) for _ in range(MAX_SEED_SIZE)
]
mails = [
    username + "@" + random.choice(mails_servers) + ".com" for username in usernames
]


async def seed_items(con: asyncpg.Connection, users: List[UserInDB]):
    items_repo = ItemsRepository(con)
    for title, image_url, tag_list in zip(
        titles[:SEED_SIZE], image_urls[:SEED_SIZE], tags[:SEED_SIZE]
    ):
        description = f"This is a {title}"
        seller = random.choice(users)
        slug = get_slug_for_item(title=title)
        item_in_db = await items_repo.create_item(
            slug=slug,
            title=title,
            image=image_url,
            description=description,
            seller=seller,
            tags=tag_list,
        )
        print(f"Created {item_in_db}")


async def seed_users(con: asyncpg.Connection) -> List[UserInDB]:
    users_in_db = []
    user_repo = UsersRepository(con)
    for username, password, mail in zip(
        usernames[:SEED_SIZE], passwords[:SEED_SIZE], mails[:SEED_SIZE]
    ):
        user_in_db = await user_repo.create_user(
            username=username, email=mail, password=password
        )
        users_in_db.append(user_in_db)
    return users_in_db


async def seed_db():
    print("Connection to db...")
    pool = await asyncpg.create_pool(
        str(MY_DATABASE_CONNECTION),
        min_size=5,
        max_size=5,
    )
    print("Connected to db successfully")
    try:
        async with pool.acquire() as con:
            print("Creating users")
            users_in_db = await seed_users(con=con)
            print(f"Created {len(users_in_db)} users")
            await seed_items(con=con, users=users_in_db)
    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(seed_db())

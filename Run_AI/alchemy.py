from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    select,
    update,
    insert,
    delete,
    ForeignKey,
    REAL,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import ast
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

Base = declarative_base()
DATABASE_URL = "sqlite+aiosqlite:///users.db"
engine = create_async_engine(DATABASE_URL, echo=True)


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, unique=True)
    name = Column(String)
    age = Column(Integer, default=None)
    per_week = Column(Integer, default=None)
    gender = Column(Text, default=None)
    level = Column(Integer, default=None)
    target = Column(String, default=None)
    plan = Column(String, default=None)
    weight_gr = Column(String, default=None)
    user_nik = Column(String, unique=True)
    geo = Column(String, default=None)
    lang = Column(String, default="ru")


class Avg_rate_m(Base):
    __tablename__ = "avg_rate_m"
    topic = Column(String, primary_key=True, default=None)
    avg = Column(REAL, default=0)


class Recent(Base):
    __tablename__ = "recent"
    id = Column(String, primary_key=True, default=None)


class UserSport(Base):
    __tablename__ = "user_sport"
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    km = Column(Integer)
    amount = Column(Integer, default=0)
    amount_at = Column(Integer, default=0)
    level = Column(Integer, default=1)


async def create():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await insert_avg_m()


AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_recent():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(select(Recent.id))
            people = result.scalars().all()
            return people


async def get_weight(user_id):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(
                select(User.weight_gr).where(User.user_id == user_id)
            )
            weight = result.scalars().first()
            return weight


async def get_geo(user_id):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(
                select(User.geo).where(User.user_id == user_id)
            )
            geo = result.scalars().first()
            return geo


async def get_user_data(user_id):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(select(User).where(User.user_id == user_id))
            weight = result.scalars().first()
            return weight


async def get_people():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(select(User))
            people = result.scalars().all()
            return people


async def get_people_ids():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(select(User.user_id))
            people = result.scalars().all()
            return people


async def get_profile1(user_id):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(
                select(UserSport).where(UserSport.user_id == user_id)
            )
            weight = result.scalars().first()
            return weight


async def get_plan_aiosql(user_id):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(
                select(User.plan).where(User.user_id == user_id)
            )
            plan = result.scalars().first()
            return plan


async def update_weight(user_id, weight_dict):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            stmt = (
                update(User)
                .where(User.user_id == user_id)
                .values(weight_gr=str(weight_dict))
            )
            await session.execute(stmt)
            await session.commit()


async def save_location(user_id, geo):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            stmt = update(User).where(User.user_id == user_id).values(geo=str(geo))
            await session.execute(stmt)
            await session.commit()


async def update_gender(user_id, gender):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            stmt = (
                update(User).where(User.user_id == user_id).values(gender=str(gender))
            )
            await session.execute(stmt)
            await session.commit()


async def update_train(user_id, today):
    plan = await get_plan_aiosql(user_id)
    prof = await get_profile1(user_id)
    for i in ast.literal_eval(plan).keys():
        if today in i:
            km = i[len(today) + 2 :][:2]
            km = extract_leading_numbers(km)
            print(prof.km, prof.amount_at)

            async with AsyncSessionLocal() as session:
                async with session.begin():
                    stmt = (
                        update(UserSport)
                        .where(UserSport.user_id == user_id)
                        .values(
                            km=(prof.km + km),
                            amount=0,
                            amount_at=int(prof.amount_at) + 1,
                        )
                    )
                    await session.execute(stmt)
                    await session.commit()
                    return [prof.km + km, prof.level]


async def update_target(user_id, target):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            stmt = (
                update(User).where(User.user_id == user_id).values(target=str(target))
            )
            await session.execute(stmt)
            await session.commit()


async def update_level(user_id, level):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            stmt = update(User).where(User.user_id == user_id).values(level=str(level))
            await session.execute(stmt)
            await session.commit()


async def update_times(user_id, times):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            stmt = (
                update(User).where(User.user_id == user_id).values(per_week=int(times))
            )
            await session.execute(stmt)
            await session.commit()


async def update_plan(user_id, plan):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            stmt = update(User).where(User.user_id == user_id).values(plan=plan)
            await session.execute(stmt)
            await session.commit()


async def update_age(user_id, age):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            stmt = update(User).where(User.user_id == user_id).values(age=int(age))
            await session.execute(stmt)
            await session.commit()


async def insert_user(user_id, first_name, user_nik):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(select(UserSport.user_id))
            users_in_second_table = result.scalars().all()
            try:
                stmt = insert(User).values(
                    user_id=user_id, name=first_name, user_nik=user_nik
                )
                stmt2 = insert(UserSport).values(
                    user_id=user_id, km=0, amount=0, level=1, amount_at=0
                )
                await session.execute(stmt)
                if str(user_id) in str(users_in_second_table):
                    await session.execute(
                        delete(UserSport).where(UserSport.user_id == user_id)
                    )
                await session.execute(stmt2)
                await session.commit()
            except:
                await session.execute(delete(User).where(User.user_id == user_id))
                await session.commit()
                await insert_user(user_id, first_name, user_nik)


async def insert_avg_m():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            try:
                stmt1 = insert(Avg_rate_m).values(topic="rate1", avg=0)
                stmt2 = insert(Avg_rate_m).values(topic="rate2", avg=0)
                stmt3 = insert(Avg_rate_m).values(topic="rate3", avg=0)
                await session.execute(stmt1)
                await session.execute(stmt2)
                await session.execute(stmt3)
                await session.commit()
            except:
                await session.execute(
                    delete(Avg_rate_m).where(Avg_rate_m.topic is not None)
                )
                await session.commit()
                await insert_avg_m()


async def delete_recent():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            stmt = delete(Recent).where(Recent.id is not None)
            await session.execute(stmt)
            await session.commit()


async def add_id(msg):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            stmt = insert(Recent).values(id=msg)
            await session.execute(stmt)
            await session.commit()


async def update_avg_m(i, topic):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            stmt = update(Avg_rate_m).where(Avg_rate_m.topic == topic).values(avg=i)
            await session.execute(stmt)
            await session.commit()


async def delete_topic(user_id):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            stmt = update(User).where(User.user_id == user_id).values(doc="")
            await session.execute(stmt)
            await session.commit()


async def get_avg_m(topic):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(
                select(Avg_rate_m.avg).where(Avg_rate_m.topic == topic)
            )
            doc = result.scalars().first()
            return doc


async def get_avg_info():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(
                select(Avg_rate_m.avg).where(Avg_rate_m.topic == "rate1")
            )
            doc = result.scalars().first()
            return doc


async def get_avg_mis():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(
                select(Avg_rate_m.avg).where(Avg_rate_m.topic == "rate2")
            )
            doc = result.scalars().first()
            return doc


async def get_avg_match():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(
                select(Avg_rate_m.avg).where(Avg_rate_m.topic == "rate3")
            )
            doc = result.scalars().first()
            return doc


def extract_leading_numbers(input_string):
    numbers = ""
    for char in input_string:
        if char.isdigit():
            numbers += char
        else:
            break
    return int(numbers)

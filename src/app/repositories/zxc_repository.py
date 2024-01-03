from bson import ObjectId

from app.core.config import mongo_db_name, mongo_collection_name

from motor.motor_asyncio import AsyncIOMotorClient

from app.dblayer.serializer import mongo_serializer
from app.models.zxc_model import ItemModel


class ZXCRepository:
    def __init__(self, mongo_client: AsyncIOMotorClient):
        self.mongo_client = mongo_client
        self.database = mongo_client.get_database(mongo_db_name)
        self.collection = self.database.get_collection(mongo_collection_name)

    @mongo_serializer
    async def create_one(self, zxc_dto: ItemModel.CREATE, **kwargs):
        session = kwargs.get("session")
        inserted_id = (
            await self.collection.insert_one(document=zxc_dto.dict(), session=session)
        ).inserted_id
        return await self.collection.find_one(
            filter={"_id": inserted_id}, session=session
        )

    @mongo_serializer
    async def find_all(self, limit: int, **kwargs):
        session = kwargs.get("session")
        return self.collection.find(
            filter={"deleted": {"$ne": True}}, session=session
        ).limit(limit)

    @mongo_serializer
    async def delete_one(self, oid: ObjectId, **kwargs):
        session = kwargs.get("session")
        await self.collection.update_one(
            filter={"_id": oid},
            update={"$set": {"deleted": True}},
            session=session,
        )

    @mongo_serializer
    async def find_one(self, oid: ObjectId, **kwargs):
        session = kwargs.get("session")
        return await self.collection.find_one(
            filter={"_id": oid, "deleted": {"$ne": True}}, session=session
        )

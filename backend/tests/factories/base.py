"""Base factory class for SQLModel models with async session support."""

import factory
from sqlmodel.ext.asyncio.session import AsyncSession


class AsyncSQLModelFactory(factory.Factory):
    """
    Base factory for SQLModel models.

    This factory provides a clean interface for creating test data
    that works with SQLModel and async sessions.

    Usage:
        class MyModelFactory(AsyncSQLModelFactory):
            class Meta:
                model = MyModel

            field = factory.Faker("word")

        # Create instance (not saved to DB)
        instance = MyModelFactory.build()

        # Create and save to DB
        instance = await MyModelFactory.create_async(session)
    """

    class Meta:
        abstract = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Create an instance without saving to database."""
        return model_class(*args, **kwargs)

    @classmethod
    async def create_async(cls, session: AsyncSession, **kwargs):
        """
        Create an instance and save it to the database.

        Args:
            session: The async database session
            **kwargs: Override factory defaults

        Returns:
            The created and persisted model instance
        """
        instance = cls.build(**kwargs)
        session.add(instance)
        await session.flush()
        await session.refresh(instance)
        return instance

    @classmethod
    async def create_batch_async(cls, session: AsyncSession, size: int, **kwargs):
        """
        Create multiple instances and save them to the database.

        Args:
            session: The async database session
            size: Number of instances to create
            **kwargs: Override factory defaults

        Returns:
            List of created and persisted model instances
        """
        instances = cls.build_batch(size, **kwargs)
        for instance in instances:
            session.add(instance)
        await session.flush()
        for instance in instances:
            await session.refresh(instance)
        return instances

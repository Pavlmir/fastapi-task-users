from typing import List, TypeVar, Union, Optional

from pydantic import BaseModel
from pydantic.error_wrappers import ValidationError
from tortoise.exceptions import BaseORMException

M = TypeVar("M")
T = TypeVar("T", bound=BaseModel)
C = TypeVar("C", bound=BaseModel)


class BaseRepository:
    _model = None
    _schema = None
    _schema_create = _schema

    def __init__(self, model: M, schema: T) -> None:
        self._model = model
        self._schema = schema

    async def get_by_id(
        self, id: int, cond: Optional[dict] = None
    ) -> Optional[T]:
        """Get objects in DB

        Args:

        * id: id
        * cond: parameters for filter

        """
        cond = cond or dict()
        try:
            result = await self._schema.from_queryset_single(
                self._model.filter(**cond).filter(id=id).first()
            )
        except ValidationError as e:
            raise e
        return result

    async def get_list(
        self, cond: Optional[dict] = None, limit: int = 20, offset: int = 0
    ) -> Optional[List[T]]:
        cond = cond or dict()
        result = await self._schema.from_queryset(
            self._model.filter(**cond).limit(limit).offset(offset)
        )
        return result

    async def create_object(self, obj: C, cond: Optional[dict] = None) -> T:
        """Create object in DB

        Args:

        * obj: object to create
        * cond: parameters for filter

        """
        data = obj.dict(exclude_unset=True)
        if cond:
            data.update(**cond)
        new_obj = await self._model.create(**data)
        return await self._schema.from_tortoise_orm(new_obj)

    async def update_object(
        self,
        obj_id: int,
        obj: Union[C, dict],
        cond: Optional[dict] = None,
        add_fields: Optional[dict] = None,
    ) -> T:
        """Update object in DB

        Args:

        * obj_id: id
        * obj: fields for update
        * add_fields: additional model fields
        * cond: parameters for filter

        """
        cond = cond or dict()
        obj = obj.dict(exclude_unset=True)
        if add_fields:
            obj.update(**add_fields)
        try:
            await self._model.filter(**cond).filter(id=obj_id).update(**obj)
        except BaseORMException as e:
            raise e

        return await self._schema.from_queryset_single(self._model.get(id=obj_id))

    async def delete_object(self, obj_id: int, cond: Optional[dict] = None) -> bool:
        """Delete object in DB

        Args:

        * obj_id: id
        * cond: parameters for filter

        """
        return await self._model.filter(id=obj_id, **cond).delete() > 0

    async def fake_delete_object(
        self, obj_id: int, obj: dict, cond: Optional[dict] = None
    ) -> bool:
        """Fake delete - modifies the fields that are responsible for hiding the entity.
        The real deletion does not happen.

        Args:

        * obj_id: id
        * obj: fields for update
        * cond: parameters for filter

        """
        cond = cond or dict()
        return await self._model.filter(**cond).filter(id=obj_id).update(**obj) > 0

    async def get_count(self, cond: Optional[dict] = None):
        """Get the number of objects

        Args:

        * cond: parameters for filter

        """
        cond = cond or dict()
        result = await self._model.filter(**cond).count()
        return result

    async def update_or_create_object(self, obj_id: int, obj: dict) -> List:
        """Update or create new object, if object not exist

        Args:

        * obj_id: id
        * obj: fields for update

        """
        result = await self._model.update_or_create(defaults=obj, id=obj_id)
        return result

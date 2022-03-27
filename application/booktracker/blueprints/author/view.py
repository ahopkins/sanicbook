from logging import getLogger
from typing import Awaitable, Callable, List, Optional

from booktracker.common.csrf import csrf_protected
from booktracker.common.pagination import Pagination
from sanic import Blueprint, Request, json
from sanic.exceptions import NotFound
from sanic.views import HTTPMethodView
from sanic_ext import openapi
from sanic_ext.extensions.openapi.definitions import Reference

from .executor import AuthorExecutor
from .model import Author, CreateAuthorBody

bp = Blueprint("Authors", url_prefix="/authors")
logger = getLogger("booktracker")


@openapi.component(name="Author")
class A:
    eid: str
    name: str
    num_books: Optional[int]


class Fetch:
    meta = Reference("#/components/schemas/Pagination")
    authors = [Reference("#/components/schemas/Author")]


class AuthorListView(HTTPMethodView, attach=bp):
    @staticmethod
    @openapi.operation("fetch-authors")
    @openapi.response(
        status=200,
        content={"application/json": Fetch},
    )
    async def get(request: Request, pagination: Pagination):
        """
        Fetch all authors
        """
        executor = AuthorExecutor(request.app.ctx.postgres)
        kwargs = {**pagination.to_dict()}
        getter: Callable[
            ..., Awaitable[List[Author]]
        ] = executor.get_all_authors

        if name := request.args.get("name"):
            kwargs["name"] = name
            getter = executor.get_authors_by_name

        try:
            authors = await getter(**kwargs)
        except NotFound:
            authors = []

        return json({"meta": pagination, "authors": authors})

    @staticmethod
    @openapi.operation("create-author")
    @openapi.body({"application/json": CreateAuthorBody}, validate=True)
    @openapi.response(
        status=201,
        content={"application/json": Reference("#/components/schemas/Author")},
    )
    @csrf_protected
    async def post(request: Request, body: CreateAuthorBody):
        """
        Create an author
        """
        executor = AuthorExecutor(request.app.ctx.postgres)
        author = await executor.create_author(**body.to_dict())
        return json({"author": author}, status=201)

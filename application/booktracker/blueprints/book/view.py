from logging import getLogger
from typing import Any, Awaitable, Callable, Dict, List, Optional

from asyncpg.exceptions import UniqueViolationError
from booktracker.blueprints.author.executor import AuthorExecutor
from booktracker.blueprints.user.executor import UserExecutor
from booktracker.blueprints.user.model import User
from booktracker.common.csrf import csrf_protected
from booktracker.common.pagination import Pagination
from sanic import Blueprint, Request, json
from sanic.exceptions import NotFound
from sanic.views import HTTPMethodView
from sanic_ext import openapi, validate
from sanic_jwt.decorators import inject_user, protected

from .executor import BookExecutor, BookSeriesExecutor
from .hydrator import BookHydrator
from .model import (
    Book,
    BookState,
    CreateBookBody,
    CreateSeriesBody,
    Series,
    UpdateBookStateBody,
)
from sanic_ext.extensions.openapi.definitions import Reference

logger = getLogger("booktracker")
bp = Blueprint("Books", url_prefix="/books")


@openapi.component(name="Book")
class B:
    eid: str
    title: str
    author = Reference("#/components/schemas/Author")
    series = Reference("#/components/schemas/BookSeries")
    user = Reference("#/components/schemas/User")
    is_loved: Optional[bool]
    state: Optional[BookState]


@openapi.component(name="BookSeries")
class BS:
    eid: str
    name: str


@openapi.component(name="User")
class U:
    eid: str
    login: str


class CreateBookResponse:
    book = Reference("#/components/schemas/Book")


class CreateBookSeriesResponse:
    series = Reference("#/components/schemas/BookSeries")


class FetchBooks:
    meta = Reference("#/components/schemas/Pagination")
    books = [Reference("#/components/schemas/Book")]


class FetchBookSeries:
    meta = Reference("#/components/schemas/Pagination")
    series = [Reference("#/components/schemas/BookSeries")]


class FetchBook:
    book = Reference("#/components/schemas/Book")


class BookListView(HTTPMethodView, attach=bp):
    @staticmethod
    @openapi.operation("create-book")
    @openapi.body({"application/json": CreateBookBody})
    @openapi.response(
        status=201,
        content={"application/json": CreateBookResponse},
    )
    @validate(json=CreateBookBody)
    @inject_user()
    @protected()
    @csrf_protected
    async def post(request: Request, body: CreateBookBody, user: User):
        """
        Create a book
        """
        book_executor = BookExecutor(request.app.ctx.postgres)
        series_executor = BookSeriesExecutor(request.app.ctx.postgres)
        author_executor = AuthorExecutor(request.app.ctx.postgres)

        if not body.author_is_eid:
            author = await author_executor.create_author(name=body.author)
        else:
            author = await author_executor.get_author_by_eid(eid=body.author)

        if body.series:
            if not body.series_is_eid:
                series = await series_executor.create_book_series(
                    name=body.series
                )
            else:
                series = await series_executor.get_book_series_by_eid(
                    eid=body.series
                )

        if not body.title_is_eid:
            book = await book_executor.create_book(
                title=body.title,
                author_id=author.author_id,
                series_id=series.series_id if body.series else None,
            )
        else:
            book = await book_executor.get_book_by_eid(eid=body.title)

        try:
            await book_executor.create_book_to_user(
                book_id=book.book_id, user_id=user.user_id
            )
        except UniqueViolationError:
            ...

        return json({"book": book}, status=201)

    @staticmethod
    @openapi.operation("fetch-books")
    @openapi.response(
        status=200,
        content={"application/json": FetchBooks},
    )
    @openapi.parameter(name="title", description="Search for books by title")
    @inject_user()
    async def get(
        request: Request,
        pagination: Optional[Pagination] = None,
        user: Optional[User] = None,
    ):
        """
        Fetch all books

        When accessed as a non-authenticated user, it will return all books.
        When accessed with authentication, it will only return books for that
        user (unless the `title` parameter has been specified).
        """
        executor = BookExecutor(request.app.ctx.postgres, BookHydrator())
        kwargs = {**pagination.to_dict()} if pagination else {}
        getter: Callable[..., Awaitable[List[Book]]] = executor.get_all_books

        if title := request.args.get("title"):
            kwargs["title"] = title
            getter = executor.get_books_by_title
        elif user:
            payload = await request.app.ctx.auth.extract_payload(request)
            user_executor = UserExecutor(request.app.ctx.postgres)
            user = await user_executor.get_by_eid(eid=payload["eid"])
            kwargs["user_id"] = user.user_id
            getter = executor.get_all_books_for_user
        try:
            books = await getter(**kwargs)
        except NotFound:
            books = []
        output = [book.to_dict(include_null=False) for book in books]
        return json({"meta": pagination, "books": output})


class BookDetailsView(HTTPMethodView, attach=bp, uri="/<eid>"):
    @staticmethod
    @openapi.operation("fetch-book")
    @openapi.response(
        status=200,
        content={"application/json": FetchBook},
    )
    @inject_user()
    async def get(
        request: Request,
        eid: str,
        user: Optional[User],
        executor: BookExecutor,
    ):
        """
        Fetch single book

        Get the details for a single book
        """
        getter: Callable[..., Awaitable[Book]] = executor.get_book_by_eid
        kwargs: Dict[str, Any] = {"eid": eid}
        if user:
            getter = executor.get_book_by_eid_for_user
            kwargs["user_id"] = user.user_id
        book = await getter(**kwargs)
        return json({"book": book.to_dict(include_null=False)})


class BookLoveView(HTTPMethodView, attach=bp, uri="/<eid>/love"):
    @staticmethod
    @openapi.operation("love-book")
    @inject_user()
    @protected()
    @csrf_protected
    async def put(request: Request, eid: str, user: User):
        """
        Toggle book love

        openapi:
        responses:
            200:
                content:
                    application/json:
                        schema:
                            type: object
                            properties:
                                ok:
                                    type: boolean
                                    example: true
        """
        executor = BookExecutor(request.app.ctx.postgres, BookHydrator())
        await executor.update_toggle_book_is_loved(
            eid=eid, user_id=user.user_id
        )
        return json({"ok": True})


class BookStateView(HTTPMethodView, attach=bp, uri="/<eid>/state"):
    @staticmethod
    @openapi.operation("update-book-state")
    @openapi.body({"application/json": UpdateBookStateBody})
    @inject_user()
    @protected()
    @csrf_protected
    async def put(request: Request, eid: str, user: User):
        """
        Update book state

        openapi:
        responses:
            200:
                content:
                    application/json:
                        schema:
                            type: object
                            properties:
                                ok:
                                    type: boolean
                                    example: true
        """
        executor = BookExecutor(request.app.ctx.postgres, BookHydrator())
        await executor.update_book_state(
            eid=eid, user_id=user.user_id, state=request.json["state"]
        )
        return json({"ok": True})


class BookSeriesListView(HTTPMethodView, attach=bp, uri="/series"):
    @staticmethod
    @openapi.operation("fetch-book-series")
    @openapi.response(
        status=200,
        content={"application/json": FetchBookSeries},
    )
    @openapi.parameter(name="name", description="Filter by name")
    async def get(request: Request, pagination: Pagination):
        """
        Fetch list of book series
        """
        executor = BookSeriesExecutor(request.app.ctx.postgres)
        kwargs = {**pagination.to_dict()}
        getter: Callable[
            ..., Awaitable[List[Series]]
        ] = executor.get_all_series

        if name := request.args.get("name"):
            kwargs["name"] = name
            getter = executor.get_series_by_name
        try:
            series = await getter(**kwargs)
        except NotFound:
            series = []

        return json({"meta": pagination, "series": series})

    @staticmethod
    @openapi.operation("create-book-series")
    @openapi.body({"application/json": CreateSeriesBody})
    @openapi.response(
        status=201,
        content={"application/json": CreateBookSeriesResponse},
    )
    @validate(json=CreateSeriesBody)
    @csrf_protected
    async def post(request: Request, body: CreateSeriesBody):
        """
        Create a book series
        """
        executor = BookSeriesExecutor(request.app.ctx.postgres)
        series = await executor.create_book_series(**body.to_dict())
        return json({"series": series}, status=201)

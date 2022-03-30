from sanic import Request, Sanic
from sanic.response import redirect

app = Sanic.get_app("BooktrackerApp")


@app.on_request
async def https_redirect(request: Request):
    if (
        request.headers.get("x-forwarded-proto") == "http"
        and not app.config.LOCAL
    ):
        return redirect(request.url.replace("http://", "https://"))

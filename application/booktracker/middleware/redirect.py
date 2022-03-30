from sanic import Request, Sanic

app = Sanic.get_app("BooktrackerApp")


@app.on_request
async def https_redirect(request: Request):
    for key, value in request.headers.items():
        if key not in ("authorization", "cookie"):
            print(key, value)

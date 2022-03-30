from sanic import Request, Sanic

app = Sanic.get_app("BooktrackerApp")


@app.on_request
async def https_redirect(request: Request):
    print(request.scheme)

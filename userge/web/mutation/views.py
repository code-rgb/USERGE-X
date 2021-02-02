from web import webX

@webX.get("/")
async def hello_world():
    return {"message": "Userge-X"}

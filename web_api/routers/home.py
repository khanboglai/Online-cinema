# import csv
# import os
# import base64
# import pandas as pd
# from collections import defaultdict
# from typing import Annotated
# from fastapi import APIRouter, Request, Depends
# from starlette.templating import Jinja2Templates
# from routers.auth import get_current_user_id
#
# import httpx
#
# router = APIRouter(
#     prefix='',
#     tags=['Homepage']
# )
#
# templates = Jinja2Templates(directory="templates")
#
# UserDependency = Annotated[dict, Depends(get_current_user_id)]
#
# async def get_image_base64(image_path: str) -> str:
#     with open(image_path, "rb") as image_file:
#         return base64.b64encode(image_file.read()).decode('utf-8')
#
# @router.get("/home")
# async def get_home_html(user: UserDependency, request: Request):
#     """Returns template for home page"""
#     if user is None:
#         return RedirectResponse(url="/login")
#     else:
#         async with httpx.AsyncClient() as client:
#             response = await client.get(f"http://ml:8080/recommend/{user}")  # Обращаемся ко второму API
#         images_by_tag = defaultdict(list)
#         df = pd.read_csv("static/data/items.csv")
#         for film in response.json()["recommendations"]:
#             images_by_tag["Recommended"].append({"cover": await get_image_base64("static/image.png"),
#                                                  "name": df[(df["item_id"] == film)]["title"].to_string(index=False)})
#         return templates.TemplateResponse("home.html", {"request": request, "films": images_by_tag})
#

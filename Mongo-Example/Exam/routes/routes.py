from fastapi import APIRouter
from ..models.exam_models import Class_Subject
from ..Database.database import collection_name 
from ..schema.exam_schema import list_serial,add_serial
from bson import ObjectId
from ..utils.response_utils import Response
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def get_exams():
    todos = list_serial(collection_name.find())
    if todos:
        return Response(status_code=200, message="Exam data retrieved successfully.", data=[todos]).send_success_response()
    if not todos:
        return Response(status_code=200, message="Dont have any Examn Data to load currently.", data={}).send_error_response()

@router.post("/")
async def post_exams(todo: Class_Subject):
    #todos = add_serial(collection_name.insert_one(dict(todo)))
    if todo:
        collection_name.insert_one(dict(todo))
        return Response(status_code=200, message="Exam data posted successfully.", data=(dict(todo))).send_success_response()
    return Response(status_code=200, message="Dont have any Examn Data to load currently.", data={}).send_error_response()

@router.put("/{id}")
async def put_exams(id: str, todo: Class_Subject):
    if todo:
        collection_name.find_one_and_update({"_id": ObjectId(id)},{"$set": dict(todo)})
        return Response(status_code=200, message="Exam data updated successfully.", data={"data": dict(todo)}).send_success_response()
    return Response(status_code=200, message="Dont have any Examn Data to load currently.", data={}).send_error_response()

@router.delete("/{id}")
async def delete_exams(id_enter: str):
    todos = collection_name.find_one({"_id": ObjectId(id_enter)})
    if todos:
        collection_name.find_one_and_delete({"_id": ObjectId(id_enter)})
        return Response(status_code=200, message="Data successfully deleted for given ID." , data={id_enter}).send_success_response()
    return Response(status_code=404, message="Invalid ID.No records found with given id.", data={}).send_error_response()
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from src.api.v1.security import security
from src.api.v1.exam.models.class_subject_model import Class, Subject
from src.api.v1.exam.schemas.class_subject_schema import ClassCreate, SubjectCreate
from src.api.v1.utils.response_utils import Response
from fastapi.encoders import jsonable_encoder
import logging

class ClassSubjectServices:

    @staticmethod
    def create_class(db: Session, class_data: ClassCreate, user_data: dict):
        """
        Create a new class
        """
        # Check if the user has the necessary role (admin or teacher)
        if user_data["role"] not in ["admin", "teacher"]:
            return Response(
                status_code=403, 
                message="Only admins and teachers can create new classes.", 
                data={}
            ).send_error_response()

        # Check if the class already exists
        existing_class = db.query(Class).filter(Class.name == class_data.name).first()
        if existing_class:
            return Response(
                status_code=400, 
                message="Class with this name already exists.", 
                data={}
            ).send_error_response()

        # Create the class
        new_class = Class(name=class_data.name)
        db.add(new_class)
        db.commit()
        db.refresh(new_class)

        return Response(
            status_code=201, 
            message="Class created successfully.", 
            data={"class_id": new_class.id, "name": new_class.name}
        ).send_success_response()

    @staticmethod
    def get_all_classes(db: Session, user_data: dict, page: int, limit: int):
        """
        Get all classes
        """
        # Validate role directly from the user_data (already decoded)
        if user_data["role"] not in ["admin", "teacher"]:
            return Response(
                status_code=403, 
                message="Only admins and teachers can see this information.", 
                data={}
            ).send_error_response()

        # Calculate pagination
        total_classes = db.query(Class).count()
        skip = (page - 1) * limit

        # Query classes with pagination
        classes = db.query(Class).offset(skip).limit(limit).all()
        if not classes:
            if skip >= total_classes:
                return Response(
                    status_code=404, 
                    message="Page exceeds the number of available classes.", 
                    data={}
                ).send_error_response()
            return Response(
                status_code=404, 
                message="No classes found.", 
                data={}
            ).send_error_response()

        # Calculate total pages
        total_pages = (total_classes + limit - 1) // limit
        serialized_classes = jsonable_encoder(classes)

        return Response(
            status_code=200, 
            message="Classes retrieved successfully.", 
            data={ 
                "classes": serialized_classes, 
                "total_classes": total_classes, 
                "total_pages": total_pages, 
                "page": page, 
                "limit": limit
            }
        ).send_success_response()

from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.api.v1.exam.models.class_subject_model import Class, Subject
from src.api.v1.exam.schemas.class_subject_schema import ClassCreate, SubjectCreate
from src.api.v1.utils.response_utils import Response
from fastapi.encoders import jsonable_encoder
from typing import Optional
import logging

logger = logging.getLogger(__name__)

DEFAULT_PAGE = 1
DEFAULT_LIMIT = 5

class ClassSubjectServices:

    @staticmethod
    def create_class(db: Session, class_data: ClassCreate, user_data: dict):
        """
        Create a new class
        """
        if user_data["role"] not in ["admin", "teacher"]:
            return Response(
                status_code=403, 
                message="Only admins and teachers can create new classes.", 
                data={}
            ).send_error_response()

        existing_class = db.query(Class).filter(Class.name == class_data.name).first()
        if existing_class:
            return Response(
                status_code=400, 
                message="Class with this name already exists.", 
                data={}
            ).send_error_response()
        
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
    def get_all_classes(db: Session, user_data: dict, page: int, limit: int, query:Optional[str]):
        """
        Get all classes with pagination (maximum 5 records per page).
        """
        if user_data["role"] not in ["admin", "teacher"]:
            logger.warning(f"Unauthorized access attempt by {user_data['Username']} with role {user_data['role']}")
            return Response(status_code=403, message="Only admins and teachers can see this information.", data={}).send_error_response()
        
        limit = min(limit, 5)
        skip = (page - 1) * limit
        
        if not query:
            total_classes = db.query(Class).count()
            class_es = db.query(Class).filter().offset(skip).limit(limit).all()
            if not class_es:
                if skip >= total_classes:
                    return Response(status_code=400, message="Page exceeds the number of available classes.", data={}).send_error_response()
                return Response(status_code=404, message="No classes found.", data={}).send_error_response()

            total_pages = (total_classes + limit - 1) // limit
            serialized_classes = jsonable_encoder(class_es)

            return Response(status_code=200, message="Classes retrieved successfully.",
                            data={ 
                                    "classes": serialized_classes, 
                                    "total_classes": total_classes, 
                                    "total_pages": total_pages, 
                                    "page": page, 
                                    "limit": limit
                                }).send_success_response()

        search_query = f"%{query}%"
        
        total_classes = db.query(Class).filter(Class.name.ilike(search_query)).count()
        classes = (db.query(Class).filter(Class.name.ilike(search_query)).offset(skip).limit(limit).all())

        if not classes:
            return Response(status_code=404, message="No classes found for given query.", data={}).send_error_response()
        
        if not classes:
            if skip >= total_classes:
                return Response(status_code=400, message="Page exceeds the number of available classes.", data={}).send_error_response()
            return Response(status_code=404, message="No classes found.", data={}).send_error_response()

        total_pages = (total_classes + limit - 1) // limit
        serialized_classes = jsonable_encoder(classes)

        return Response(status_code=200, message="Classes retrieved successfully.", 
                        data=
                            { 
                                "classes": serialized_classes, 
                                "total_classes": total_classes, 
                                "total_pages": total_pages, 
                                "page": page, 
                                "limit": limit
                            }).send_success_response()

    @staticmethod
    def create_subject(db: Session, subject_data: SubjectCreate, user_data: dict):
        """
        Create a new subject
        """
        if user_data["role"] not in ["admin", "teacher"]:
            return Response(
                status_code=403, 
                message="Only admins and teachers can create new subjects.", 
                data={}
            ).send_error_response()

        existing_subject = db.query(Subject).filter(Subject.name == subject_data.name).first()
        if existing_subject:
            return Response(
                status_code=400, 
                message="Subject with this name already exists.", 
                data={}
            ).send_error_response()

        new_subject = Subject(name=subject_data.name)
        db.add(new_subject)
        db.commit()
        db.refresh(new_subject)

        return Response(
            status_code=201, 
            message="Subject created successfully.", 
            data={"subject_id": new_subject.id, "name": new_subject.name}
        ).send_success_response()

    @staticmethod
    def get_all_subjects(db: Session, user_data: dict, page: int, limit: int, query:Optional[str]):
        """
        Get all subjects with pagination (maximum 5 records per page).
        """
        if user_data["role"] not in ["admin", "teacher"]:
            return Response(status_code=403, message="Only admins and teachers can see this information.", data={}).send_error_response()

        limit = min(limit, 5) 
        skip = (page - 1) * limit
        
        if not query:
            total_subjects = db.query(Subject).count()
            subjec_ts = db.query(Subject).filter().offset(skip).limit(limit).all()
            if not subjec_ts:
                if skip >= total_subjects:
                    return Response(status_code=400, message="Page exceeds the number of available classes.", data={}).send_error_response()
                return Response(status_code=404, message="No classes found.", data={}).send_error_response()

            total_pages = (total_subjects + limit - 1) // limit
            serialized_subjects = jsonable_encoder(subjec_ts)

            return Response(status_code=200, message="Classes retrieved successfully.",
                            data={ 
                                    "classes": serialized_subjects, 
                                    "total_classes": total_subjects, 
                                    "total_pages": total_pages, 
                                    "page": page, 
                                    "limit": limit
                                }).send_success_response()

        search_query = f"%{query}%"
        total_subjects = db.query(Subject).filter(Subject.name.ilike(search_query)).count()

        subjects = (db.query(Subject).filter(Subject.name.ilike(search_query)).offset(skip).limit(limit).all())

        if not subjects:
            return Response(status_code=404, message="No subjects found for given query.", data={}).send_error_response()

        if not subjects:
            if skip >= total_subjects:
                return Response(status_code=404, message="Page exceeds the number of available subjects.", data={}).send_error_response()
            return Response(status_code=404, message="No subjects found.", data={}).send_error_response()
            
        total_pages = (total_subjects + limit - 1) // limit
        serialized_subjects = jsonable_encoder(subjects)

        return Response(status_code=200, message="Subjects retrieved successfully.", 
                        data=
                        { 
                            "subjects": serialized_subjects, 
                            "total_subjects": total_subjects, 
                            "total_pages": total_pages, 
                            "page": page, 
                            "limit": limit
                        }).send_success_response()


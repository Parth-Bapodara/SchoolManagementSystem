def individual_serial(todo) -> dict:
    return{
            "id": str(todo["_id"]),
            "class_name": todo["class_name"],
            "subject_name": todo["subject_name"],
            "student_name": todo["student_name"],
            "marks": todo["marks"]
        }

def list_serial(todos) -> dict:
    return[individual_serial(todo) for todo in todos]

def add_serial(todos) -> dict:
    return[individual_serial(todo) for todo in todos]
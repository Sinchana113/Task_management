from flask import Blueprint, request, jsonify
from models import db, User, Task
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)

routes = Blueprint("routes", __name__)

# ---------------- REGISTER ----------------

@routes.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({"message": "Email already exists"}), 400

    hashed_password = generate_password_hash(password)

    new_user = User(
        username=username,
        email=email,
        password=hashed_password
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


# ---------------- LOGIN ----------------

@routes.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    if not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid password"}), 401

    access_token = create_access_token(identity=user.email)

    return jsonify({
        "message": "Login successful",
        "access_token": access_token
    }), 200


# ---------------- PROFILE ----------------

@routes.route("/profile", methods=["GET"])
@jwt_required()
def profile():

    current_user = get_jwt_identity()

    return jsonify({
        "message": "Welcome!",
        "logged_in_as": current_user
    }), 200


# ---------------- CREATE TASK ----------------

@routes.route("/tasks", methods=["POST"])
@jwt_required()
def create_task():

    current_email = get_jwt_identity()

    user = User.query.filter_by(email=current_email).first()

    data = request.get_json()

    title = data.get("title")
    description = data.get("description")

    new_task = Task(
        title=title,
        description=description,
        status="Pending",
        user_id=user.id
    )

    db.session.add(new_task)
    db.session.commit()

    return jsonify({
        "message": "Task created successfully"
    }), 201


# ---------------- GET TASKS (WITH FILTER) ----------------

@routes.route("/tasks", methods=["GET"])
@jwt_required()
def get_tasks():

    current_email = get_jwt_identity()

    user = User.query.filter_by(email=current_email).first()

    status = request.args.get("status")

    if status:
        tasks = Task.query.filter_by(
            user_id=user.id,
            status=status
        ).all()
    else:
        tasks = Task.query.filter_by(
            user_id=user.id
        ).all()

    output = []

    for task in tasks:
        output.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status
        })

    return jsonify(output), 200


# ---------------- UPDATE TASK ----------------

@routes.route("/tasks/<int:id>", methods=["PUT"])
@jwt_required()
def update_task(id):

    current_email = get_jwt_identity()

    user = User.query.filter_by(email=current_email).first()

    task = Task.query.filter_by(
        id=id,
        user_id=user.id
    ).first()

    if not task:
        return jsonify({"message": "Task not found"}), 404

    data = request.get_json()

    task.title = data.get("title", task.title)
    task.description = data.get("description", task.description)
    task.status = data.get("status", task.status)

    db.session.commit()

    return jsonify({
        "message": "Task updated successfully"
    }), 200



# ---------------- DELETE TASK ----------------

@routes.route("/tasks/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_task(id):

    current_email = get_jwt_identity()

    user = User.query.filter_by(email=current_email).first()

    task = Task.query.filter_by(id=id, user_id=user.id).first()

    if not task:
        return jsonify({"message": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()

    return jsonify({
        "message": "Task deleted successfully"
    }), 200
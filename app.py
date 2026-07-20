from flask import Flask
from config import Config
from models import db
from routes import routes
from flask_jwt_extended import JWTManager

app = Flask(__name__)

app.config.from_object(Config)

app.config["JWT_SECRET_KEY"] = "mysecretkey123"

jwt = JWTManager(app)

db.init_app(app)

app.register_blueprint(routes)

@app.route("/")
def home():
    return "Task Management API Running"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
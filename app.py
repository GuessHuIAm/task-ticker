from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Concept: Models in Flask are specified using classes, which inherit from db.Model.
# Each class attribute represents a database column, and each instance of the class
# represents a row in the database table.
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(200), nullable=True)
    category = db.Column(db.String(100))
    expiry_date = db.Column(db.DateTime, nullable=True)
    complete = db.Column(db.Boolean, default=False)
    
    def days_left(self):
        if self.expiry_date is not None:
            delta = self.expiry_date - datetime.now()
            if delta.days < 0:
                return f"{abs(delta.days)} days ago"
            elif delta.days < 1:
                return f"{abs(delta.seconds // 3600)} hours left"
            return f"{delta.days} days left"
        else:
            return None
        
    def nice_expiry_date(self):
        if self.expiry_date is not None:
            # Date of the week, day of the month, month, year
            return self.expiry_date.strftime('%A, %d %B %Y')
        else:
            return None

# Concept: Routes in Flask are specified using decorators, usually placed above the function definition.
@app.route("/")
def home():
    default_categories = ["General", "Work", "Personal", "Academic", "Miscellaneous"]
    db_categories = [category[0] for category in db.session.query(Todo.category).distinct()]
    combined_categories = list(set(default_categories + db_categories))
    
    tomorrow = datetime.today() + timedelta(days=1)
    formatted_date = tomorrow.strftime('%Y-%m-%d')
    
    todo_list = Todo.query.all()
    
    # Concept: Templates in Flask are specified using Jinja2, which is a templating language. Here, we are passing
    # the todo_list variable alongside other to the template, which is then used to render the HTML stored at templates/base.html.
    return render_template("base.html", todo_list=todo_list, categories=combined_categories, formatted_date=formatted_date)

@app.route("/add", methods=["POST"])
def add():
    # Concept: Requests in Flask are specified using the request object. Here, we are using the form attribute
    # to access the form data sent by the client.
    title = request.form.get("title")
    description = request.form.get("description")
    category = request.form.get("category")
    expiry_date = request.form.get("expiry_date")
    new_category = request.form.get("new_category")
    if expiry_date:
        expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d')

    if category == 'other' and new_category:
        category = new_category.strip().capitalize()

    # Create a new Todo item by unpacking form_data
    new_todo = Todo(
        title=title,
        description=description,
        category=category,
        expiry_date=expiry_date,
    )
    db.session.add(new_todo)
    db.session.commit()
    
    # Concept: We are building a URL using the url_for function, which takes the name of the function as the first
    # argument, and any keyword arguments as the rest. Here, we are redirecting the client to the home page.
    return redirect(url_for("home"))

@app.route("/update/<int:todo_id>")
def update(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.complete = not todo.complete
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("home"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
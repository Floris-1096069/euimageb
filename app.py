from flask import Flask, render_template, request, redirect, url_for
from config import Config
from models import db, Board, Post
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    boards = Board.query.all()
    return render_template('index.html', boards=boards)

@app.route('/b/<board_name>')
def view_board(board_name):
    board = Board.query.filter_by(name=board_name).first_or_404()
    posts = Post.query.filter_by(board_id=board.id, parent_id=None).order_by(Post.created_at.desc()).all()
    return render_template('board.html', board=board, posts=posts)

@app.route('/api/b/<board_name>/posts')
def get_posts(board_name):
    board = Board.query.filter_by(name=board_name).first_or_404()
    posts = Post.query.filter_by(board_id=board.id, parent_id=None).order_by(Post.created_at.desc()).all()
    return render_template('_posts.html', posts=posts, board=board)

@app.route('/api/b/<board_name>/posts', methods=['POST'])
def create_post(board_name):
    board = Board.query.filter_by(name=board_name).first_or_404()
    content = request.form.get('content')
    image = request.files.get('image')

    image_url = None
    if image and image.filename != '':
        filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)
        image_url = f"/static/uploads/{filename}"

    new_post = Post(
        board_id=board.id,
        content=content,
        image_url=image_url,
        user_id=None
    )
    db.session.add(new_post)
    db.session.commit()

    return render_template('_post.html', post=new_post, board=board)

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return ""

@app.route('/api/b/<board_name>/posts/<int:parent_id>/reply', methods=['POST'])
def create_reply(board_name, parent_id):
    board = Board.query.filter_by(name=board_name).first_or_404()
    parent_post = Post.query.get_or_404(parent_id)
    content = request.form.get('content')
    image = request.files.get('image')

    image_url = None
    if image and image.filename != '':
        filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)
        image_url = f"/static/uploads/{filename}"

    new_reply = Post(
        board_id=board.id,
        content=content,
        image_url=image_url,
        user_id=None,
        parent_id=parent_post.id
    )
    db.session.add(new_reply)
    db.session.commit()

    return render_template('_reply.html', reply=new_reply)

@app.route('/api/b/create', methods=['POST'])
def create_board():
    board_name = request.form.get('board_name')
    board_description = request.form.get('board_description')

    new_board = Board(
        name=board_name[0],
        title=board_name,
        description=board_description,
        anonymous_allowed=False
    )
    db.session.add(new_board)
    db.session.commit()

    return render_template('_board.html', board=new_board)

if __name__ == '__main__':
    app.run(debug=True)
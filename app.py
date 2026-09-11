from flask import Flask, render_template, request, redirect, url_for, send_file
from config import Config
from gundb_client import GunDBClient
import os
import io
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_object(Config)

gundb = GunDBClient(app.config['UPLOAD_FOLDER'])

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/ipfs/<path:cid>')
def ipfs_proxy(cid):
    """Proxy images from IPFS using raw HTTP requests."""
    try:
        data = gundb._get_from_ipfs(cid)
        if not data:
            return "File not found", 404
        # Detect mimetype (simplified)
        if cid.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            mimetype = f"image/{cid.split('.')[-1]}"
        else:
            mimetype = 'application/octet-stream'
        return send_file(
            io.BytesIO(data),
            mimetype=mimetype,
            as_attachment=False
        )
    except Exception as e:
        return f"Error fetching from IPFS: {str(e)}", 500


@app.route('/')
def index():
    boards = gundb.get_all_boards()
    return render_template('index.html', boards=boards)

@app.route('/b/<board_name>')
def view_board(board_name):
    board = gundb.get_board(board_name)
    if not board:
        return redirect(url_for('index'))
    posts = gundb.get_posts(board_name, parent_id=None)  # Only top-level posts
    print("Posts with replies:", posts)
    return render_template('board.html', board=board, posts=posts)

@app.route('/api/b/<board_name>/posts')
def get_posts(board_name):
    board = gundb.get_board(board_name)
    if not board:
        return "", 404
    posts = gundb.get_posts(board_name, parent_id=None)
    return render_template('_posts.html', posts=posts, board=board)

@app.route('/api/b/<board_name>/posts', methods=['POST'])
def create_post(board_name):
    content = request.form.get('content')
    image = request.files.get('image')
    new_post = gundb.create_post(board_name, content, image)
    if new_post:
        return render_template('_post.html', post=new_post, board={'name': board_name})
    else:
        return "Error creating post", 500

@app.route('/api/posts/<board_name>/<post_key>', methods=['DELETE'])
def delete_post(board_name, post_key):
    success = gundb.delete_post(board_name, post_key)
    return "" if success else "Error deleting post", 500

@app.route('/api/b/<board_name>/posts/<parent_key>/reply', methods=['POST'])
def create_reply(board_name, parent_key):
    content = request.form.get('content')
    image = request.files.get('image')
    new_reply = gundb.create_reply(board_name, parent_key, content, image)
    if new_reply:
        return render_template('_reply.html', reply=new_reply)
    else:
        return "Error creating reply", 500

@app.route('/api/b/create', methods=['POST'])
def create_board():
    board_name = request.form.get('board_name')
    board_description = request.form.get('board_description')
    new_board = gundb.create_board(
        name=board_name,
        title=board_name,
        description=board_description,
        anonymous_allowed=False
    )
    if new_board:
        return render_template('_board.html', board=new_board)
    else:
        return "Error creating board", 500

if __name__ == '__main__':
    app.run(debug=True)
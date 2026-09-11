import requests
import ipfshttpclient
import time
import secrets
from werkzeug.utils import secure_filename
import os
from datetime import datetime

GUN_URL = 'http://localhost:8080/gun'
IPFS_API_URL = 'http://127.0.0.1:5001/api/v0'

class GunDBClient:
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder
        os.makedirs(upload_folder, exist_ok=True)

    def _add_to_ipfs(self, file):
        """Add a file to IPFS using raw HTTP requests."""
        if not file or file.filename == '':
            return None
        try:
            # Read file content and reset pointer for Flask
            file_content = file.read()
            file.seek(0)  # Reset for Flask to reuse later
            response = requests.post(
                f"{IPFS_API_URL}/add",
                files={'file': (file.filename, file_content)},  # Use file_content
                timeout=10
            )
            if response.ok:
                return response.json()['Hash']
            else:
                print(f"IPFS add error: {response.text}")
                return None
        except Exception as e:
            print(f"Error adding to IPFS: {e}")
            return None

    # Replace _get_from_ipfs with this (if you use it elsewhere):
    def _get_from_ipfs(self, cid):
        """Fetch a file from IPFS using raw HTTP requests."""
        try:
            response = requests.post(  # <-- Change from GET to POST
                f"{IPFS_API_URL}/cat?arg={cid}",
                timeout=10
            )
            if response.ok:
                return response.content
            else:
                print(f"IPFS cat error: {response.text}")
                return None
        except Exception as e:
            print(f"Error fetching from IPFS: {e}")
            return None

    def _get_image_url(self, image_cid):
        """Generate a URL for an IPFS-stored image."""
        if not image_cid:
            return None
        return f"/ipfs/{image_cid}"


    def get_all_boards(self):
        """Fetch all boards from GunDB."""
        try:
            response = requests.get(f"{GUN_URL}/boards", timeout=5)
            if not response.ok:
                return []
            boards_data = response.json()
            boards = []
            for board_key, board_data in boards_data.items():
                if isinstance(board_data, dict):
                    board = {
                        'id': board_key,
                        'name': board_data.get('name', board_key),
                        'title': board_data.get('title', ''),
                        'description': board_data.get('description', ''),
                        'anonymous_allowed': board_data.get('anonymous_allowed', False),
                        'created_at': datetime.fromtimestamp(board_data.get('created_at', 0))
                    }
                    boards.append(board)
            return boards
        except Exception as e:
            print(f"Error getting boards: {e}")
            return []


    def get_board(self, board_name):
        """Fetch a single board by name."""
        try:
            response = requests.get(f"{GUN_URL}/boards/{board_name}", timeout=5)
            if not response.ok:
                return None
            board_data = response.json()
            return {
                'id': board_name,
                'name': board_data.get('name', board_name),
                'title': board_data.get('title', ''),
                'description': board_data.get('description', ''),
                'anonymous_allowed': board_data.get('anonymous_allowed', False),
                'created_at': datetime.fromtimestamp(board_data.get('created_at', 0))
            }
        except Exception as e:
            print(f"Error getting board {board_name}: {e}")
            return None


    def create_board(self, name, title, description, anonymous_allowed=False):
        """Create a new board in GunDB."""
        board_data = {
            "name": name,
            "title": title,
            "description": description,
            "anonymous_allowed": anonymous_allowed,
            "created_at": int(time.time()),
            "posts": {}  # Initialize empty posts
        }
        try:
            requests.post(f"{GUN_URL}/boards/{name}", json=board_data, timeout=5)
            return self.get_board(name)
        except Exception as e:
            print(f"Error creating board: {e}")
            return None


    def _get_image_url(self, image_cid):
        """Generate a URL for an IPFS-stored image."""
        if not image_cid:
            return None
        return f"/ipfs/{image_cid}"

    def get_posts(self, board_name, parent_id=None):
        try:
            response = requests.get(f"{GUN_URL}/boards/{board_name}/posts", timeout=5)
            if not response.ok:
                return []
            posts_data = response.json()
            print("DEBUG: Raw GunDB posts data:", posts_data)
            posts = []
            for post_key, post_data in posts_data.items():
                print("DEBUG: post_key:", post_key, "post_data:", post_data)
                if not isinstance(post_data, dict):
                    continue
                if parent_id is None and post_data.get('parent_id') is not None:
                    continue
                if parent_id is not None and post_data.get('parent_id') != parent_id:
                    continue
                post = {
                    'id': post_key,
                    'board_id': board_name,
                    'content': post_data.get('content', ''),  # Ensure this is included
                    'image_url': self._get_image_url(post_data.get('image_cid')),  # Reconstruct URL
                    'user_id': post_data.get('user_id'),
                    'parent_id': post_data.get('parent_id'),
                    'created_at': datetime.fromtimestamp(post_data.get('created_at', 0)),
                    'board': {'name': board_name}
                }
                posts.append(post)
            posts.sort(key=lambda x: x.get('created_at') or 0, reverse=True)  # Safe sort
            return posts
        except Exception as e:
            print(f"Error getting posts: {e}")
            return []


    def create_post(self, board_name, content, image_file=None):
        """Create a new post in a board."""
        image_cid = None
        if image_file and image_file.filename != '':
            image_cid = self._add_to_ipfs(image_file)
        post_key = f"{int(time.time())}_{secrets.token_hex(4)}"
        post_data = {
            "content": content,
            "image_cid": image_cid,
            "user_id": None,
            "parent_id": None,
            "created_at": int(time.time()),
            "replies": {}
        }
        try:
            requests.post(f"{GUN_URL}/boards/{board_name}/posts/{post_key}", json=post_data, timeout=5)
            return {
                **post_data,
                'id': post_key,
                'board_id': board_name,
                'image_url': self._get_image_url(image_cid),
                'board': {'name': board_name},
                'created_at': datetime.fromtimestamp(post_data['created_at'])  # Override the integer
            }
        except Exception as e:
            print(f"Error creating post: {e}")
            return None


    def create_reply(self, board_name, parent_key, content, image_file=None):
        """Create a reply to a post."""
        image_cid = None
        if image_file and image_file.filename != '':
            image_cid = self._add_to_ipfs(image_file)
        reply_key = f"{int(time.time())}_{secrets.token_hex(4)}"
        reply_data = {
            "content": content,
            "image_cid": image_cid,
            "user_id": None,
            "parent_id": parent_key,
            "created_at": int(time.time()),
            "replies": {}
        }
        try:
            requests.post(
                f"{GUN_URL}/boards/{board_name}/posts/{parent_key}/replies/{reply_key}",
                json=reply_data,
                timeout=5
            )
            return {
                **reply_data,
                'id': reply_key,
                'board_id': board_name,
                'image_url': self._get_image_url(image_cid),
                'board': {'name': board_name},
                'created_at': datetime.fromtimestamp(reply_data['created_at'])  # Override the integer
            }
        except Exception as e:
            print(f"Error creating reply: {e}")
            return None


    def delete_post(self, board_name, post_key):
        """Delete a post by setting it to null in GunDB."""
        try:
            requests.put(f"{GUN_URL}/boards/{board_name}/posts/{post_key}", json=None, timeout=5)
            return True
        except Exception as e:
            print(f"Error deleting post: {e}")
            return False
from . import api
from .authentication import auth
from ..models import Post, Permission, User, Comment
from flask import request, jsonify, g, url_for
from .decorators import permission_required
from .errors import forbidden

@api.route("/users/<int:id>")
@auth.login_required
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())

@api.route("/users/<int:id>/posts/")
def get_user_posts(id):
    user = User.query.get_or_404(id)
    return jsonify({
        "posts" : [post.to_json() for post in user.posts]
    })

@api.route("/users/<int:id>/timeline/")
def get_user_followed_posts(id):
    page = request.args.get("page", 1, type=int)
    user = User.query.get_or_404(id)
    pagination = user.followed_posts.order_by(Post.timestamp.desc()).paginate(page=page, per_page=10, error_out=False)
    posts = pagination.items
    ret_json = {}
    ret_json["prev"] = pagination.has_prev and url_for("api.get_user_followed_posts", id=id, page=page-1) or "null"
    ret_json["next"] = pagination.has_next and url_for("api.get_user_followed_posts", id=id, page=page+1) or "null"
    ret_json["items"] = [post.to_json() for post in posts]
    return jsonify(ret_json)

from . import api
from .authentication import auth
from ..models import Post, Permission, User, Comment
from flask import request, jsonify, g, url_for
from .decorators import permission_required
from .errors import forbidden

@api.route("/comments/<int:id>")
@auth.login_required
def get_comments(id):
    page = request.args.get("page", 1, type=int)
    post = Post.query.get_or_404(id)
    pagination = post.comments.order_by(Comment.timestamp.desc()).paginate(page, per_page=10, error_out=False)
    ret_json = {}
    if pagination.has_prev:
        ret_json["prev"] = url_for("api.get_comments", id=id, page=page - 1)
    else:
        ret_json["prev"] = "null"

    if pagination.has_next:
        ret_json["next"] = url_for("api.get_comments", id=id, page=page + 1)
    else:
        ret_json["next"] = "null"
    comments = pagination.items
    ret_json["comments"] = [comment.to_json() for comment in comments]
    return jsonify(ret_json)

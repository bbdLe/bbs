#-*- coding: utf-8 -*-
from flask import render_template, session, redirect, url_for, current_app, abort, flash, request, make_response
from flask_login import login_required, current_user
from .. import db
from ..models import User, Role, Post, Permission, Comment
from ..email import send_mail
from . import main
from .forms import NameForm, EditProfileForm, EditProfileAdminForm, PostForm, CommentForm
from ..decorators import admin_required, permission_required

@main.route("/", methods=["GET", "POST"])
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body = form.body.data, author = current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for(".index"))
    page = request.args.get("page", 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get("show_followed", ""))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(page, per_page=10, error_out=False)
    posts = pagination.items
    return render_template("index.html", form=form, posts = posts, pagination = pagination, show_followed = show_followed)

@main.route("/user/<username>")
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    page = request.args.get("page", 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(page, per_page=10, error_out=False)
    posts = pagination.items
    return render_template("user.html", user=user, posts=posts, pagination = pagination)

@main.route("/post/<int:id>", methods=["GET", "POST"])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body = form.body.data, post = post,
                          author = current_user._get_current_object())
        db.session.add(comment)
        flash("评论成功")
        return redirect(url_for(".post", id = id, page = -1))
    page = request.args.get("page", 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // 10 + 1
    pagination = post.comments.order_by(Comment.timestamp.desc()).paginate(page, per_page=10, error_out=False)
    comments = pagination.items
    return render_template("post.html", posts=[post], form=form, comments = comments, pagination = pagination)

@main.route("/edit-post/<int:id>", methods=["GET", "POST"])
def edit_post(id):
    post = Post.query.get_or_404(id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    form.body.data = post.body
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        return redirect(url_for(".index"))
    return render_template("edit_post.html", form = form)

@main.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.localtion = form.localtion.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash("资料已经修改")
        return redirect(url_for(".user", username = current_user.username))
    form.name.data = current_user.name
    form.localtion.data = current_user.localtion
    form.about_me.data = current_user.about_me
    return render_template("edit_profile.html", form=form)

@main.route("/edit-profile/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user)
    if form.validate_on_submit():
        user.change_email(form.email.data)
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.localtion = form.localtion.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash("资料已经修改")
        return redirect(url_for(".user", username = user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.name.data = user.name
    form.localtion.data = user.localtion
    form.about_me.data = user.about_me
    return render_template("edit_profile.html", form=form)

@main.route("/follow/<username>")
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username = username).first()
    if not user:
        flash("没有该用户")
        return redirect(url_for(".main"))
    if current_user.is_following(user):
        flash("你已经关注该用户")
        return redirect(url_for(".user", username = user.username))
    current_user.follow(user)
    return redirect(url_for(".user", username = username))

@main.route("/unfollow/<username>")
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username = username).first()
    if not user:
        flash("没有该用户")
        return redirect(url_for(".main"))
    if not current_user.is_following(user):
        flash("你没有关注该用户")
        return redirect(url_for(".user", username = username))
    current_user.unfollow(user)
    return redirect(url_for(".user", username = username))

@main.route("/followers/<username>")
def followers(username):
    user = User.query.filter_by(username = username).first()
    if user is None:
        flash("没有该用户")
        return redirect(url_for(".index"))
    page = request.args.get("page", 1, type=int)
    pagination = user.followers.paginate(page, per_page = 10, error_out=False)
    followers = [{"user" : item.follower, "timestamp" : item.timestamp} for item in pagination.items]
    return render_template("followers.html", user=user, title="Followers of", endpoint=".followers",
                           pagination=pagination, followers=followers)

@main.route("/followed_by/<username>")
def followed_by(username):
    user = User.query.filter_by(username = username).first()
    if user is None:
        flash("没有该用户")
        return redirect(url_for(".index"))
    page = request.args.get("page", 1, type=int)
    pagination = user.followed.paginate(page, per_page = 10, error_out=False)
    followers = [{"user" : item.followed, "timestamp" : item.timestamp} for item in pagination.items]
    return render_template("followers.html", user=user, title="Followed by", endpoint=".followed_by",
                           pagination=pagination, followers=followers)

@main.route("/show_followed")
@login_required
@permission_required(Permission.FOLLOW)
def show_followed():
    resp = make_response(redirect(url_for(".index")))
    resp.set_cookie("show_followed", "1", max_age=30*24*60*60)
    return resp

@main.route("/show_all")
@login_required
@permission_required(Permission.FOLLOW)
def show_all():
    resp = make_response(redirect(url_for(".index")))
    resp.set_cookie("show_followed", "", max_age=30*24*60*60)
    return resp

@main.route("/moderate")
@login_required
@permission_required(Permission.MODERATE_COMMITS)
def moderate():
    page = request.args.get("page", 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(page, per_page = 10, error_out=False)
    comments = pagination.items
    return render_template("moderate.html", pagination=pagination, comments=comments, page=page)

@main.route("/enable/<int:id>")
@login_required
@permission_required(Permission.MODERATE_COMMITS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    page = request.args.get("page", 1, type=int)
    comment.disable = False
    db.session.add(comment)
    return redirect(url_for(".moderate", page=page))

@main.route("/disable/<int:id>")
@login_required
@permission_required(Permission.MODERATE_COMMITS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    page = request.args.get("page", 1, type=int)
    comment.disable = True
    db.session.add(comment)
    return redirect(url_for(".moderate", page=page))

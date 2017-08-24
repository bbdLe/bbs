#-*- coding: utf-8 -*-
from flask import render_template, session, redirect, url_for, current_app, abort, flash, request
from flask_login import login_required, current_user
from .. import db
from ..models import User, Role, Post
from ..email import send_mail
from . import main
from .forms import NameForm, EditProfileForm, EditProfileAdminForm, PostForm
from ..decorators import admin_required

@main.route("/", methods=["GET", "POST"])
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body = form.body.data, author = current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for(".index"))
    page = request.args.get("page", 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=10, error_out=False)
    posts = pagination.items
    return render_template("index.html", form=form, posts = posts, pagination = pagination)

@main.route("/user/<username>")
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    page = request.args.get("page", 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(page, per_page=10, error_out=False)
    posts = pagination.items
    return render_template("user.html", user=user, posts=posts, pagination = pagination)

@main.route("/post/<int:id>")
def post(id):
    post = Post.query.get_or_404(id)
    return render_template("post.html", posts=[post])

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

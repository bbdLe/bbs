#-*- coding: utf-8 -*-
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..models import User
from ..email import send_mail
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, SendMailResetPasswordForm, ResetPasswordForm

@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get("next") or url_for("main.index"))
        flash("不正确的账号或者密码")
    return render_template("auth/login.html", form=form)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("你已经注销")
    return redirect(url_for("main.index"))

@auth.route("/register", methods=["GET", "POST"])
def register():
    if not current_user.is_anonymous:
        return redirect(url_for("main.index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_mail(user.email, "请确认你的账号", "auth/email/confirm", user=user, token=token)
        flash("请到邮箱确认你的信息")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form = form)

@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if  not current_user.confirmed and request.endpoint[:5] != "auth." and request.endpoint != "static":
            return redirect(url_for("auth.unconfirmed"))

@auth.route("/unconfirmed")
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for("main.index"))
    return render_template("auth/unconfirmed.html")

@auth.route("/changepasswd", methods=["POST", "GET"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = current_user.email).first()
        if user.verify_password(form.oldpassword.data):
            user.password = form.newpassword.data
            db.session.add(user)
            if current_user.is_authenticated:
                logout_user()
            flash("密码修改成功")
            return redirect(url_for("auth.login"))
        else:
            flash("密码错误")
            return render_template("auth/changepassword.html", form = form)
    return render_template("auth/changepassword.html", form = form)

@auth.route("/reset", methods=["POST", "GET"])
def send_reset_password_mail():
    form = SendMailResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        token = user.gererate_reset_password_token()
        send_mail(user.email, "重置你的密码", "auth/email/resetpassword", token = token)
        flash("已经发送重置密码邮件到您的邮箱，请到邮箱确认信息")
        return redirect(url_for("auth.login"))
    return render_template("auth/resetpasswordsendmail.html", form=form)

@auth.route("/reset/<token>", methods=["POST", "GET"])
def reset_password(token):
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user.check_reset_token_and_change_passwd(token, form.password.data):
            flash("密码已经重置")
        else:
            flash("链接已过期或账号错误")
        return redirect(url_for("auth.login"))
    return render_template("auth/resetpassword.html", form = form)

@auth.route("/confirm/<token>")
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for("main.index"))
    if current_user.confirm(token):
        flash("你已经确认你的账号信息")
    else:
        flash("确认链接无效或者过期")
    return redirect(url_for("main.index"))

@auth.route("/confirm")
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_mail(current_user.email, "请确认你的账号", "auth/email/confirm", user=current_user, token=token)
    flash("一封信的邮件已经发到你邮箱，请确认")
    return redirect(url_for("main.index"))

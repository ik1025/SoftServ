from flaskblog.models import User, Post
from flask import Flask, render_template, url_for, flash, redirect, request
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flaskblog import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
import secrets
import os

@app.route("/")
def front():
	return render_template('front.html')

# @app.route("/")
@app.route("/Home")
@login_required
def hello():
	posts=Post.query.all()
	return render_template('home.html', posts=posts)

@app.route("/about")
def about():
	return render_template("about.html", title='About Page')

@app.route("/register", methods=['GET','POST'])
def register():
	if(current_user.is_authenticated):
		return redirect(url_for('hello'))
	form = RegistrationForm()
	if(form.validate_on_submit()):
		hashed = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data, email=form.email.data, password=hashed)
		db.session.add(user)
		db.session.commit()
		flash('Account created!', 'success')
		return redirect(url_for('hello'))
	return render_template('register.html',title='Register',form=form)

@app.route("/login", methods=['GET','POST'])
def login():
	if(current_user.is_authenticated):
		return redirect(url_for('hello'))
	form = LoginForm()
	if(form.validate_on_submit()):
		user = User.query.filter_by(email=form.email.data).first()
		if(user and bcrypt.check_password_hash(user.password, form.password.data)):
			login_user(user,remember=form.remember.data)
			np = request.args.get('next')
			if(np):
				return redirect(np)
			else:
				return redirect(url_for('hello'))
		else:
			flash('login unsuccessful', 'danger')
	return render_template('login.html',title='Register',form=form)

@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('front'))

def save_pic(picdata):
	random_hex = secrets.token_hex(8)
	fname, fext = os.path.splitext(picdata.filename)
	newfn = random_hex + fext
	picpath = os.path.join(app.root_path, 'static/profile_pics', newfn)
	picdata.save(picpath)
	return newfn

@app.route("/account", methods=['GET','POST'])
@login_required
def account():
	form = UpdateAccountForm()
	if(form.validate_on_submit()):

		if(form.picture.data):
			picture_file = save_pic(form.picture.data)
			current_user.image_file = picture_file

		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('Account Updated', 'success')
		return redirect(url_for('account'))

	elif(request.method == 'GET'):
		form.username.data = current_user.username
		form.email.data = current_user.email

	image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
	return render_template('account.html',title='Account', image_file=image_file, form=form)

@app.route("/post/new", methods=['GET','POST'])
@login_required
def new_post():
	form = PostForm()
	if(form.validate_on_submit()):
		post = Post(title=form.title.data, content=form.content.data, author=current_user)
		db.session.add(post)
		db.session.commit()
		flash('Post Submitted!', 'success')
		return redirect(url_for('hello'))
	return render_template('createpost.html', title='Create Post', form=form)
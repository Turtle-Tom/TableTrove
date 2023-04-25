# 3rd-party packages
from flask import render_template, request, redirect, url_for, flash
from flask_mongoengine import MongoEngine
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename


import plotly.express as px 
import plotly.offline as po

# imports for image rendering
import io
import base64

# stdlib
from datetime import datetime

# local
from . import app, bcrypt, client
from .forms import (
    SearchForm,
    ItemCommentForm,
    ItemLikeForm,
    CreateItemForm,
    CreatureCommentForm,
    CreatureLikeForm,
    CreateCreatureForm,
    RegistrationForm,
    LoginForm,
    UpdateUsernameForm,
    UpdateProfilePicForm,
    DeleteAccountForm
)
from .models import User, Item, ItemComment, Creature, CreatureComment, load_user
from .utils import current_time

""" ************ View functions ************ """

@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")


@app.route("/", methods=["GET", "POST"])
def index():
    # Get top liked item
    items = Item.objects()
    item_max = -1
    top_item = None
    if items:
        top_item = items.first()
        for item in items:
            if item.likes > item_max:
                top_item = item
                item_max = item.likes

    creatures = Creature.objects()
    creature_max = -1
    top_creature = None
    if creatures:
        top_creature = creatures.first()
        for creature in creatures:
            if creature.likes > creature_max:
                top_creature = creature
                creature_max = creature.likes

    form = SearchForm()

    if form.validate_on_submit():
        return redirect(url_for("query_results", query=form.search_query.data))

    return render_template("index.html", form=form, top_item=top_item, top_creature=top_creature)


@app.route("/search-results/<query>", methods=["GET"])
def query_results(query):
    try:
        items_query = Item.objects(name=query)
        item_query_result = []

        for item in items_query:
            item_query_result.append(item)

        item_results=item_query_result

        creatures_query = Creature.objects(name=query)
        creature_query_result = []

        for creature in creatures_query:
            creature_query_result.append(creature)

        creature_results = creature_query_result
    except ValueError as e:
        return render_template("query.html", error_msg=str(e))

    return render_template("query.html", 
        item_results=item_results, 
        creature_results=creature_results
    )

""" ************ Items ************ """

@app.route("/items/<item_id>", methods=["GET", "POST"])
def item_detail(item_id):
    try:
        item = Item.objects(item_id=item_id).first()
    except ValueError as e:
        return render_template("item_detail.html", error_msg=str(e))

    item_like_form = ItemLikeForm()
    if item_like_form.is_submitted:
        if item_like_form.submit_like.data:
            item_likes = item.likes + 1
            item.modify(likes=item_likes)
            item.save()

            return redirect(url_for('item_detail', item_id=item_id))

    form = ItemCommentForm()
    if form.validate_on_submit():
        if form.submit.data:
            item_comment = ItemComment(
                commenter=current_user._get_current_object(),
                content=form.text.data,
                date=current_time(),
                item_id=item_id
            )
            item_comment.save()

            return redirect(request.path)

    item_comments = ItemComment.objects(item_id=item_id)

    return render_template(
        "item_detail.html", item_comment_form=form, item_like_form=item_like_form, item=item, item_comments=item_comments
    )

@app.route("/create/item", methods=["GET", "POST"])
@login_required
def create_item():
    form = CreateItemForm()
    if form.validate_on_submit():
        curr_date = current_time()
        id = form.name.data + " " + curr_date
        item = Item(
            creator=current_user._get_current_object(), 
            content=form.content.data, 
            date=curr_date,
            name=form.name.data,
            item_id=id,
            likes=0
        )
        item.save()

        return redirect(url_for("item_detail", item_id=id))

    return render_template("create_item.html", item_form=form)


""" ************ Creatures ************ """

@app.route("/creatures/<creature_id>", methods=["GET", "POST"])
def creature_detail(creature_id):
    try:
        creature = Creature.objects(creature_id=creature_id).first()
    except ValueError as e:
        return render_template("creature_detail.html", error_msg=str(e))

    creature_like_form = CreatureLikeForm()
    if creature_like_form.is_submitted:
        if creature_like_form.submit_like.data:
            creature_likes = creature.likes + 1
            creature.modify(likes=creature_likes)
            creature.save()

            return redirect(url_for('creature_detail', creature_id=creature_id))

    form = CreatureCommentForm()
    if form.validate_on_submit():
        if form.submit.data:
            creature_comment = CreatureComment(
                commenter=current_user._get_current_object(),
                content=form.text.data,
                date=current_time(),
                creature_id=creature_id
            )
            creature_comment.save()

            return redirect(request.path)

    creature_comments = CreatureComment.objects(creature_id=creature_id)

    return render_template(
        "creature_detail.html", 
        creature_comment_form=form, 
        creature=creature, 
        creature_comments=creature_comments,
        creature_like_form=creature_like_form
    )

@app.route("/create/creature", methods=["GET", "POST"])
@login_required
def create_creature():
    form = CreateCreatureForm()
    if form.validate_on_submit():
        curr_date = current_time()
        id = form.name.data + " " + curr_date
        creature = Creature(
            creator=current_user._get_current_object(), 
            content=form.content.data, 
            date=curr_date,
            name=form.name.data,
            creature_id=id,
            likes=0
        )
        creature.save()

        return redirect(url_for("creature_detail", creature_id=id))

    return render_template("create_creature.html", creature_form=form)

""" ************ User Details ************ """

@app.route("/user/<username>")
def user_detail(username):
    user = User.objects(username=username).first()
    if user is not None:
        items = Item.objects(creator=user)
        item_comments = ItemComment.objects(commenter=user)
        creatures = Creature.objects(creator=user)
        creature_comments = CreatureComment.objects(commenter=user)

        df = {
            'post_type': ['Items', 'Comments on items', 'Creatures', 'Comments on Creatures'],
            'num_posts': [len(items), len(item_comments), len(creatures), len(creature_comments)]
        }

        # fig = px.bar(dict_frame, x=['items', 'comments on items', 'creatures', 'comments on creatures'], y='Number of Posts') 
        fig = px.pie(df, title="Distribution of Posts", values="num_posts", names="post_type") 
        # fig.write_html('user_stats/fig.html')

        plt = po.plot(fig, include_plotlyjs=False, output_type='div')

        if user.profile_pic.get() is None:
            return render_template("user_detail.html", 
            items=items, 
            item_comments=item_comments,
            creatures=creatures,
            creature_comments=creature_comments,
            username=username,
            plot=plt)
        else:
            bytes_im = io.BytesIO(user.profile_pic.read())
            image = base64.b64encode(bytes_im.getvalue()).decode()
            return render_template("user_detail.html", 
                items=items, 
                item_comments=item_comments,
                creatures=creatures,
                creature_comments=creature_comments,
                username=username,
                image=image,
                plot=plt)
    else:
        return render_template("user_detail.html", error_msg='User not found!')

@app.errorhandler(404)
def custom_404(e):
    err = 'Natural 1! Critical Failure!'
    return render_template('404.html', error_msg=err)


""" ************ User Management views ************ """


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    error_msg = ""
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            form.validate_email(form.email)
            form.validate_username(form.username)
            form.validate_pass(form.password.data)
            hashed = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data, email=form.email.data, password=hashed)
            user.save()

            return redirect(url_for('login'))
        except Exception as e:
            error_msg = str(e)
            flash(str(e))

    return render_template('register.html', title='Register', registration_form=form, error_msg=error_msg)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.objects(username=form.username.data).first()

            if user is not None and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('account'))
            else:
                flash('Invalid Login')
        except Exception as e:
            flash(str(e))

    return render_template("login.html", title="Login", login_form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    delete_form = DeleteAccountForm()
    if delete_form.validate_on_submit():
        try:
            delete_form.validate_confirmation(delete_form.text.data)

            # Deletes database data for testing purposes
            # User.objects().delete()
            # Item.objects().delete()
            # ItemComment.objects().delete()
            # Creature.objects().delete()
            # CreatureComment.objects().delete()

            username = current_user._get_current_object().username
            user = User.objects(username=username).first()
            Item.objects(creator=user).delete()
            ItemComment.objects(commenter=user).delete()
            Creature.objects(creator=user).delete()
            CreatureComment.objects(commenter=user).delete()

            User.delete(user)

            return redirect(url_for('index'))
        except Exception as e:
            flash(str(e))

        return redirect(url_for('account'))

    name_form = UpdateUsernameForm()
    if name_form.validate_on_submit():
        try:
            name_form.validate_username(name_form.name)
            current_user.modify(username=name_form.name.data)
            current_user.save()
        except Exception as e:
            flash(str(e))

        return redirect(url_for('account'))

    picture_form = UpdateProfilePicForm()
    if picture_form.validate_on_submit():
        img = picture_form.picture.data
        filename = secure_filename(img.filename)
        content_type = f'images/{filename[-3:]}'

        if current_user.profile_pic.get() is None:
            current_user.profile_pic.put(img.stream, content_type=content_type)
        else:
            current_user.profile_pic.replace(img.stream, content_type=content_type)

        current_user.save()
        return redirect(url_for('account'))

    if current_user.profile_pic.get() is None:
        return render_template("account.html", 
        pic_form=picture_form, 
        username_form=name_form,
        delete_form=delete_form)
    else:
        print("NOT NONE!!!!")
        bytes_im = io.BytesIO(current_user.profile_pic.read())
        image = base64.b64encode(bytes_im.getvalue()).decode()
        return render_template("account.html", 
            pic_form=picture_form, 
            username_form=name_form,
            delete_form=delete_form,
            image=image)

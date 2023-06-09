from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def index(): # The index will show all of the posts, most recent first.
    #establish db connection
    db = get_db()
    #execute query
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    #render template
    return render_template('blog/index.html', posts=posts)

# The create view works the same as the auth register view. 
# Either the form is displayed, or the posted data is validated 
# and the post is added to the database or an error is shown.
@bp.route('/create', methods = ("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        author_id = g.user['id']
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = "Title required"
        
        if error is None:
            db = get_db()
            db.execute(
                "INSERT INTO post (author_id, title, body)"
                "VALUES (?, ?, ?)",
                (author_id, title, body)
            )
            db.commit()
            return redirect(url_for('blog.index'))
        
        flash(error)
    return render_template('blog/create.html')


def get_post(id, check_author = True):
    post= get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")
    
    if check_author and post['author_id'] != g.user['id']:
        abort(403)
    
    return post

@bp.route('/<int:id>/update', methods = ('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = "Title required"
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE post SET title = ?, body = ?"
                " WHERE id = ?",
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))
        
    return render_template('blog/update.html', post = post)

@bp.route('/<int:id>/delete', methods = ('POST',))
@login_required
def delete(id):
    get_post(id)

    db = get_db()
    db.execute(
        "DELETE from post WHERE id = ?",
        (id,)
    )
    db.commit()
    return redirect(url_for('blog.index'))
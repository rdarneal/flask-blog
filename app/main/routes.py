from flask import render_template, flash, redirect, url_for, request, current_app, g
from flask_login import current_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime
from app import db
from app.main import bp
from app.main.forms import EditProfileForm, EmptyForm, PostForm, SearchForm
from app.models import User, Posts

@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        # g can store data that is available to all templates for life of request
        g.search_form = SearchForm()

@bp.route("/")
@bp.route("/index")
def index():
    return render_template('main/home.html')

@bp.route('/blog', methods=['GET', 'POST'])
@login_required
def blog():
    form = PostForm()
    if form.validate_on_submit():
        post = Posts(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!', 'success')
        return redirect(url_for('main.blog'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page=page,
        per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False
    )
    template = 'main.blog'
    first_url = url_for(template, page=1)
    last_url = url_for(template, page=posts.pages)
    next_url = url_for(template, page=posts.next_num) if posts.has_next else None
    prev_url = url_for(template, page=posts.prev_num) if posts.has_prev else None
    return render_template('main/blog.html', 
                           form=form, 
                           posts=posts,
                           first_url=first_url,
                           last_url=last_url,
                           next_url=next_url,
                           prev_url=prev_url,
                           template=template)

@bp.route('/explore')
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Posts.query.order_by(Posts.timestamp.desc()).paginate(
        page=page,
        per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False
    )
    template='main.explore' #set current page template to reuse with blog
    first_url = url_for(template, page=1)
    last_url = url_for(template, page=posts.pages)
    next_url = url_for(template, page=posts.next_num) if posts.has_next else None
    prev_url = url_for(template, page=posts.prev_num) if posts.has_prev else None
    return render_template('main/blog.html', 
                           posts=posts,
                           first_url=first_url,
                           last_url=last_url,
                           next_url=next_url,
                           prev_url=prev_url,
                           template=template
                           )

@bp.route('/search')
@login_required
def search():
    # if not g.search_form.validate():
    #     return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    posts, total = Posts.search(g.search_form.q.data, page, current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page=page+1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page-1) \
        if page > 1 else None
    return render_template('main/search.html', title='Search', posts=posts,
                           next_url=next_url, prev_url=prev_url)

@bp.route('/user/<email>')
@login_required
def user(email):
    user = User.query.filter_by(email=email).first_or_404()
    page = request.args.get('page', 1, type=int) # get the url 'page' arg, default is page 1
    posts = Posts.query.filter_by(user_id=user.id).order_by(Posts.timestamp.desc()).paginate(
        page=page,
        per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False
    )
    template = 'main.user' #set current page template (used below and in the jinja template)
    first_url = url_for(template, email=user.email, page=1)
    last_url = url_for(template, email=user.email, page=posts.pages)
    next_url = url_for(template, email=user.email, page=posts.next_num) if posts.has_next else None
    prev_url = url_for(template, email=user.email, page=posts.prev_num) if posts.has_prev else None
    form = EmptyForm() #pass the same empty form used for following/unfollowing views
    return render_template('main/user.html', 
                           user=user, 
                           posts=posts,
                           first_url=first_url,
                           last_url=last_url,
                           next_url=next_url,
                           prev_url=prev_url,
                           template=template,
                           form=form)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.email)
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.', 'success')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
        form.about_me.data = current_user.about_me
    return render_template('main/edit_profile.html', form=form)

@bp.route('/follow/<email>', methods=['POST'])
@login_required
def follow(email):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first()
        if user is None:
            flash(f'User {email} not found.', 'warning')
            return redirect(url_for('main.index'))
        if user == current_user:
            flash('You cannot follow yourself!', 'info')
            return redirect(url_for('main.user', email=email))
        current_user.follow(user)
        db.session.commit()
        flash(f'You are now following {email}!', 'success')
        return redirect(url_for('main.user', email=email))
    else:
        redirect(url_for('index'))
        
@bp.route('/unfollow/<email>', methods=['POST'])
@login_required
def unfollow(email):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first()
        if user is None:
            flash(f'User {email} not found.', 'warning')
            return redirect(url_for('main.index'))
        if user == current_user:
            flash('You cannot unfollow yourself!', 'info')
            return redirect(url_for('main.user', email=email))
        current_user.unfollow(user)
        db.session.commit()
        flash(f'You are no longer following {email}', 'info')
        return redirect(url_for('main.user', email=email))
    else:
        return redirect(url_for('main.index'))
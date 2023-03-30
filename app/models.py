import jwt
from flask import current_app
from app import db, login
from app.search import add_to_index, remove_from_index, query_index
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from datetime import datetime
from time import time

class SearchableMixin(object):
    # used cls instead of self to indicate that the class method is related to the class
    # e.g. once attached to search, the class will have a search method
    @classmethod
    def search(cls, expression, page, per_page):
        # wrap the query from search.py to replace the list of object Ids with actual objects
        # pass cls.__tablename__ as the index name
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        # initiate list for query order
        when = []
        # append the ids in elastic search query order
        for i in range(len(ids)):
            when.append((ids[i], i))
        # return the results sorted in same order provided, e.g. in more to less relevant
        return cls.query.filter(cls.id.in_(ids)).order_by(db.case(when, value=cls.id)), total
    
    @classmethod
    def before_commit(cls, session):
        # before a db commit, track db _changes (temp) to determine how to update elasticsearch
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }
    
    @classmethod
    def after_commit(cls, session):
        # on db commit, apply _changes and index
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None
        
    @classmethod
    def reindex(cls):
        # helper to refresh index with data from relational side
        # add posts in database to search index
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)

# setup event handlers to call before commit and after_commit
db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)

# load user from database during login
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# association table with User class for followers & followed
followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    tagline = db.Column(db.String(120))
    about_me = db.Column(db.String(3500))
    avatar = db.Column(db.String(120))
    posts = db.relationship('Posts', backref='author', lazy='dynamic')
    followed = db.relationship(
        'User', # right side relationship, left side being parent class
        secondary=followers, # configures association table
        primaryjoin=(followers.c.follower_id == id), #links left side entity (follower)
        secondaryjoin=(followers.c.followed_id == id), #links right side entity
        backref=db.backref('followers', lazy='dynamic'), #defines right side relationship
        lazy='dynamic' #applied to left side relationship
    )
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_reset_password_token(self, expires_in=600):
        # Create JSON web token using secret key
        return jwt.encode(
            {'reset_password': self.id,
             'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
    
    @staticmethod
    def verify_reset_password_token(token):
        # static method can be invoked directly, does not receive class as first arg.
        try:
            id = jwt.decode(token, 
                            current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'
    
    def is_following(self, user):
        # used to check is user is already following
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0
    
    def follow(self, user):
        # if not already following, follow target user
        if not self.is_following(user):
            self.followed.append(user)
    
    def unfollow(self, user):
        # if already following, unfollow target user
        if self.is_following(user):
            self.followed.remove(user)
    
    def followed_posts(self):
        followed_posts = Posts.query.join( # create temp table that combines posts and followers
            followers,
            (followers.c.followed_id == Posts.user_id)
            ).filter( # filter the posts from users I am following
                followers.c.follower_id == self.id)
        # get users own posts
        own_posts = Posts.query.filter_by(user_id=self.id)
        # union and return result
        return followed_posts.union(own_posts).order_by(Posts.timestamp.desc())
    
    def __repr__(self):
        return f'<User {self.email}>'

class Posts(SearchableMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    __searchable__ = ['body']

    def __repr__(self):
        return f'Post {self.body}'

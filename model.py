"""Models and database functions for git_data db."""

import datetime
from flask_sqlalchemy import SQLAlchemy
import config

db = SQLAlchemy()

class Repo(db.Model):
    """Repository model."""

    __tablename__ = "repos"

    repo_id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.ForeignKey("users.user_id"), nullable=False)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(), nullable=True)
    updated_at = db.Column(db.DateTime(), nullable=True)
    pushed_at = db.Column(db.DateTime(), nullable=True)
    last_updated = db.Column(db.DateTime(), nullable=True,
                             default=datetime.datetime.utcnow)
    last_crawled = db.Column(db.DateTime(), nullable=True)
    last_crawled_depth = db.Column(db.Integer, nullable=True)
    url = db.Column(db.Text, nullable=True)
    stargazers_count = db.Column(db.Integer, nullable=True)

    owner = db.relationship("User",
                            backref=db.backref("repos",
                                               order_by="desc(Repo.pushed_at)"))

    stargazers = db.relationship("User",
                                 secondary="stargazers",
                                 order_by="User.user_id",
                                 backref=db.backref("stars",
                                                    order_by="desc(Repo.repo_id)"))

    dislikes = db.relationship("User",
                               secondary="dislikes",
                               order_by="User.user_id",
                               backref=db.backref("dislikes",
                                                  order_by="desc(Repo.repo_id)"))

    watchers = db.relationship("User",
                               secondary="watchers",
                               order_by="User.user_id",
                               backref=db.backref("watches",
                                                  order_by="desc(Repo.repo_id)"))

    contributors = db.relationship("User",
                                   secondary="contributors",
                                   order_by="User.user_id",
                                   backref=db.backref("contributions",
                                                      order_by="desc(Repo.repo_id)"))

    languages = db.relationship("Language",
                               secondary="repo_languages",
                               order_by="Language.language_name",
                               backref=db.backref("repos",
                                                  order_by="desc(Repo.repo_id)"))

    repo_langs = db.relationship("RepoLanguage",
                                 order_by="desc(RepoLanguage.language_bytes)",
                                 backref=db.backref("repos",
                                                    order_by="desc(Repo.repo_id)"))

    def __repr__(self): # pragma: no cover
        """Provide helpful representation when printed."""

        return ("<Repo {} owner={} name={}>"
                .format(self.repo_id,
                        self.owner_id,
                        self.name))


class User(db.Model):
    """User model."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), nullable=False)
    name = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(), nullable=True)
    updated_at = db.Column(db.DateTime(), nullable=True,
                           default=datetime.datetime.utcnow)    
    last_crawled = db.Column(db.DateTime(), nullable=True)
    last_crawled_depth = db.Column(db.Integer, nullable=True)
    last_crawled_user_repos = db.Column(db.DateTime(), nullable=True)
    
    followers = db.relationship("User",
                                secondary="followers",
                                order_by=user_id,
                                primaryjoin="User.user_id==followers.c.user_id",
                                secondaryjoin="User.user_id==followers.c.follower_id",
                                backref=db.backref("follows",
                                                   order_by=user_id))

    def __repr__(self): # pragma: no cover
        """Provide helpful representation when printed."""

        return ("<User {} login={} name={}>"
                .format(self.user_id,
                        self.login,
                        self.name))

class Account(db.Model):
    """Account model."""

    __tablename__ = "accounts"

    account_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.ForeignKey("users.user_id"), nullable=False)
    access_token = db.Column(db.String(100), nullable=True)
    last_login = db.Column(db.DateTime(), nullable=True,
                           default=datetime.datetime.utcnow)

    user = db.relationship("User", backref=db.backref("account"))

    def __repr__(self): # pragma: no cover
        """Provide helpful representation when printed."""

        return ("<Account {} user_id={}>"
                .format(self.account_id,
                        self.user_id))


class Follower(db.Model):
    """Watcher model."""

    __tablename__ = "followers"

    follow_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.ForeignKey("users.user_id"), nullable=False)
    follower_id = db.Column(db.ForeignKey("users.user_id"), nullable=False)

    def __repr__(self): # pragma: no cover
        """Provide helpful representation when printed."""

        return ("<Follower {} user_id={} follower_id={}>"
                .format(self.follow_id,
                        self.user_id,
                        self.follower_id))


class Stargazer(db.Model):
    """Stargazer model."""

    __tablename__ = "stargazers"

    stargazer_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    repo_id = db.Column(db.ForeignKey("repos.repo_id"), nullable=False)
    user_id = db.Column(db.ForeignKey("users.user_id"), nullable=False)

    user = db.relationship("User", backref=db.backref("stars_sec"))
    repo = db.relationship("Repo", backref=db.backref("stargazers_sec"))

    __table_args__ = ( db.UniqueConstraint("user_id",
                                           "repo_id",
                                           name="uniq_star_user_repo_id"), )

    def __repr__(self): # pragma: no cover
        """Provide helpful representation when printed."""

        return ("<Stargazer {} repo_id={} user_id={}>"
                .format(self.stargazer_id,
                        self.repo_id,
                        self.user_id))


class Watcher(db.Model):
    """Watcher model."""

    __tablename__ = "watchers"

    watcher_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    repo_id = db.Column(db.ForeignKey("repos.repo_id"), nullable=False)
    user_id = db.Column(db.ForeignKey("users.user_id"), nullable=False)

    def __repr__(self): # pragma: no cover
        """Provide helpful representation when printed."""

        return ("<Watcher {} repo_id={} user_id={}>"
                .format(self.watcher_id,
                        self.repo_id,
                        self.user_id))


class Contributor(db.Model):
    """Contributor model."""

    __tablename__ = "contributors"

    contributor_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    repo_id = db.Column(db.ForeignKey("repos.repo_id"), nullable=False)
    user_id = db.Column(db.ForeignKey("users.user_id"), nullable=False)

    def __repr__(self): # pragma: no cover
        """Provide helpful representation when printed."""

        return ("<Contributor {} repo_id={} user_id={}>"
                .format(self.contributor_id,
                        self.repo_id,
                        self.user_id))


class Dislike(db.Model):
    """Dislike model."""

    __tablename__ = "dislikes"

    dislike_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    repo_id = db.Column(db.ForeignKey("repos.repo_id"), nullable=False)
    user_id = db.Column(db.ForeignKey("users.user_id"), nullable=False)

    __table_args__ = ( db.UniqueConstraint("user_id",
                                           "repo_id",
                                           name="uniq_dislike_user_repo_id"), )

    def __repr__(self): # pragma: no cover
        """Provide helpful representation when printed."""

        return ("<Dislike {} repo_id={} user_id={}>"
                .format(self.dislike_id,
                        self.repo_id,
                        self.user_id))


class Language(db.Model):
    """Languages model."""

    __tablename__ = "languages"

    language_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    language_name = db.Column(db.String(100), nullable=False, unique=True)

    def __repr__(self): # pragma: no cover
        """Provide helpful representation when printed."""

        return ("<Language {} name={}>"
                .format(self.language_id,
                        self.language_name))


class RepoLanguage(db.Model):
    """Association table between Repository and Language."""

    __tablename__ = "repo_languages"

    repo_language_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    repo_id = db.Column(db.Integer,
                        db.ForeignKey("repos.repo_id"),
                        nullable=False)
    language_id = db.Column(db.Integer,
                            db.ForeignKey("languages.language_id"),
                            nullable=False)
    language_bytes = db.Column(db.Integer, nullable=True)

    language = db.relationship("Language")

    def __repr__(self): # pragma: no cover
        """Provide helpful representation when printed."""

        return ("<RepoLanguage {} repo_id={} language_id={} bytes={}>"
                .format(self.repo_language_id,
                        self.repo_id,
                        self.language_id,
                        self.language_bytes))


def connect_to_db(app, uri=config.DB_URI):
    """Connect the database to our Flask app."""

    # Configure to use our database.
    app.config["SQLALCHEMY_DATABASE_URI"] = uri
    app.config["SQLALCHEMY_ECHO"] = False
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


if __name__ == "__main__": # pragma: no cover
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    # So that we can use Flask-SQLAlchemy, we'll make a Flask app.
    from flask import Flask

    app = Flask(__name__)

    connect_to_db(app)
    print("Connected to DB {}.".format(config.DB_URI))

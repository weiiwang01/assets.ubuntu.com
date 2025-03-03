import functools

import flask
from django_openid_auth.teams import TeamsRequest, TeamsResponse
from flask_openid import OpenID


SSO_LOGIN_URL = "https://login.ubuntu.com"
SSO_TEAMS = ["canonical-content-people", "canonical-is-devops"]


def init_sso(app):
    open_id = OpenID(
        store_factory=lambda: None,
        safe_roots=[],
        extension_responses=[TeamsResponse],
    )

    @app.route("/login", methods=["GET", "POST"])
    @open_id.loginhandler
    def login():
        app.logger.critical("receive login request")
        if "openid" in flask.session:
            app.logger.critical(f"{open_id.get_next_url()=}")
            return flask.redirect(open_id.get_next_url())

        teams_request = TeamsRequest(query_membership=SSO_TEAMS)
        try_login = open_id.try_login(
            SSO_LOGIN_URL, ask_for=["email"], extensions=[teams_request]
        )
        app.logger.critical(f"{try_login=}")
        app.logger.critical(f"{try_login.headers}")
        app.logger.critical(f"{SSO_LOGIN_URL=}")
        return try_login

    @open_id.after_login
    def after_login(resp):
        if not any(team not in resp.extensions["lp"].is_member for team in SSO_TEAMS):
            flask.abort(403)

        flask.session["openid"] = {
            "identity_url": resp.identity_url,
            "email": resp.email,
        }

        return flask.redirect(open_id.get_next_url())


def login_required(func):
    """
    Decorator that checks if a user is logged in, and redirects
    to login page if not.
    """

    @functools.wraps(func)
    def is_user_logged_in(*args, **kwargs):
        if "openid" not in flask.session:
            return flask.redirect("/login?next=" + flask.request.path)
        response = flask.make_response(func(*args, **kwargs))
        response.cache_control.private = True
        return response

    return is_user_logged_in

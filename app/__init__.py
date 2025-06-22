#===========================================================
# App Creation and Launch
#===========================================================

from flask import Flask, render_template, request, flash, redirect
import html

from app.helpers.session import init_session
from app.helpers.db      import connect_db
from app.helpers.errors  import init_error, not_found_error
from app.helpers.logging import init_logging
from app.helpers.time    import init_datetime, utc_timestamp, utc_timestamp_now


# Create the app
app = Flask(__name__)

# Configure app
init_session(app)   # Setup a session for messages, etc.
init_logging(app)   # Log requests
init_error(app)     # Handle errors and exceptions
init_datetime(app)  # Handle UTC dates in timestamps


#-----------------------------------------------------------
# Home page route
#-----------------------------------------------------------
@app.get("/")
def index():
        with connect_db() as client:
        # Get all the things from the DB
            sql = "SELECT code, name FROM teams ORDER BY name ASC"
            result = client.execute(sql)
            teams = result.rows
        return render_template("pages/home.jinja", teams=teams)


#-----------------------------------------------------------
# About page route
#-----------------------------------------------------------
@app.get("/about/")
def about():
    return render_template("pages/about.jinja")


#-----------------------------------------------------------
# Things page route - Show all the things, and new thing form
#-----------------------------------------------------------
@app.get("/teams/")
def show_all_things():
    with connect_db() as client:
        # Get all the things from the DB
        sql = "SELECT id, name FROM things ORDER BY name ASC"
        params = []
        result = client.execute(sql, params)
        things = result.rows

        # And show them on the page
        return render_template("pages/things.jinja", things=things)


#-----------------------------------------------------------
# Team page route - Show details of a single team
#-----------------------------------------------------------
@app.get("/team/<string:code>")
def show_one_thing(code):
    with connect_db() as client:
        # Get the thing details from the DB
        sql = """SELECT
                    players.name AS player_name,
                    players.notes,
                    teams.name AS team_name,
                    teams.website,
                    teams.code
                FROM
                    players
                JOIN teams ON players.team = teams.code
                WHERE teams.code = ?
                ORDER BY
                    players.name ASC;"""
        params = [code]
        result = client.execute(sql, params)

        # Did we get a result?
        if result.rows:
            # yes, so show it on the page
            team = result.rows[0]
            players = result.columns[players.name]
            website = team['website']
            return render_template("pages/team.jinja", team=team, players=players, website=website)

        else:
            # No, so show error
            return not_found_error()


#-----------------------------------------------------------
# Route for adding a thing, using data posted from a form
#-----------------------------------------------------------
@app.post("/add")
def add_a_thing():
    # Get the data from the form
    name  = request.form.get("name")
    price = request.form.get("price")

    # Sanitise the text inputs
    name = html.escape(name)

    with connect_db() as client:
        # Add the thing to the DB
        sql = "INSERT INTO things (name, price) VALUES (?, ?)"
        params = [name, price]
        client.execute(sql, params)

        # Go back to the home page
        flash(f"Thing '{name}' added", "success")
        return redirect("/things")


#-----------------------------------------------------------
# Route for deleting a thing, Id given in the route
#-----------------------------------------------------------
@app.get("/delete/<int:id>")
def delete_a_thing(id):
    with connect_db() as client:
        # Delete the thing from the DB
        sql = "DELETE FROM things WHERE id=?"
        params = [id]
        client.execute(sql, params)

        # Go back to the home page
        flash("Thing deleted", "success")
        return redirect("/things")



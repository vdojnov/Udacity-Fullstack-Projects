#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from flask_migrate import Migrate
from sqlalchemy.orm import load_only


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    website = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=True)
    venue_show_rel = db.relationship('Show', backref='venue_show', lazy=True)

    def get_venue(self):
        pshows = Show.query.filter(Show.venue_id == self.id,  Show.start_time < datetime.now()).all()
        ushows = Show.query.filter(Show.venue_id == self.id, Show.start_time > datetime.now()).all()

        data = {
          "id": self.id,
          "name": self.name,
          "genres": self.genres,
          "address": self.address,
          "city": self.city,
          "state": self.state,
          "phone": self.phone,
          "website": self.website,
          "facebook_link": self.facebook_link,
          "seeking_talent": self.seeking_talent,
          "seeking_description": self.seeking_description,
          "image_link": self.image_link,
          "past_shows": [pshow.get_show() for pshow in pshows],
          "upcoming_shows": [ushow.get_show() for ushow in ushows],
          "past_shows_count": Show.query.filter(Show.venue_id == self.id, Show.start_time < datetime.now()).count(),
          "upcoming_shows_count": Show.query.filter(Show.venue_id == self.id, Show.start_time > datetime.now()).count(),
        }

        return data

#-------------------------------------------------------------------------------

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
#    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=True)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    artist_show_rel = db.relationship('Show', backref='artist_show', lazy=True)


    def get_artist(self):
        pshows = Show.query.filter(Show.artist_id == self.id,  Show.start_time < datetime.now()).all()
        ushows = Show.query.filter(Show.artist_id == self.id, Show.start_time > datetime.now()).all()

        return {
          "id": self.id,
          "name": self.name,
          "genres": self.genres,
          "city": self.city,
          "state": self.state,
          "phone": self.phone,
          "website": self.website,
          "facebook_link": self.facebook_link,
          "seeking_venue": self.seeking_venue,
          "seeking_description": self.seeking_description,
          "image_link": self.image_link,
          "past_shows": [pshow.get_show() for pshow in pshows],
          "upcoming_shows": [ushow.get_show() for ushow in ushows],
          "past_shows_count": Show.query.filter(Show.artist_id == self.id, Show.start_time < datetime.now()).count(),
          "upcoming_shows_count": Show.query.filter(Show.artist_id == self.id, Show.start_time > datetime.now()).count(),
        }



# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = "show"

    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), primary_key=True )
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), primary_key=True )
    start_time = db.Column(db.DateTime, nullable=False, primary_key=True)

    @hybrid_property
    def venue_name(self):
        return self.venue_show.name

    @hybrid_property
    def artist_name(self):
        return self.artist_show.name

    @hybrid_property
    def start_t(self):
        return self.start_time.strftime("%m/%d/%Y, %H:%M:%S")

    @hybrid_property
    def artist_image_link(self):
        return self.artist_show.image_link

    @hybrid_property
    def venue_image_link(self):
        return self.venue_show.image_link

    def get_show(self):
        return {
          "venue_id": self.venue_id,
          "venue_name": self.venue_name,
          "artist_id": self.artist_id,
          "artist_name": self.artist_name,
          "artist_image_link": self.artist_image_link,
          "venue_image_link": self.venue_image_link,
          "start_time": self.start_t
        }




#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  data=[]
  areas = Venue.query.distinct('city', 'state').all()

  for area in areas:
      venues = Venue.query.filter(Venue.city == area.city, Venue.state == area.state).all()
      record = {
      'city': area.city,
      'state': area.state,
      'venues': [venue.get_venue() for venue in venues]

      }
      data.append(record)


  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  s_term = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike('%' + s_term + '%')).all()
  response={
    "count": Venue.query.filter(Venue.name.ilike('%' + s_term + '%')).count(),
    "data": [venue.get_venue() for venue in venues]
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venues = Venue.query.all()
  data = list(filter(lambda d: d['id'] == venue_id, [venue.get_venue() for venue in venues]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  try:
      name = request.form['name']
      city = request.form['city']
      state = request.form['state']
      address = request.form['address']
      phone = request.form['phone']
      genres = request.form.getlist('genres')
      facebook_link = request.form['facebook_link']
      new_venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, facebook_link=facebook_link)
      db.session.add(new_venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
      error = True
      db.session.rollback()
  finally:
      db.session.close()
  if error:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
      return redirect(url_for('create_venue_form'))
  else:
      return render_template('pages/home.html')

  # on successful db insert, flash success

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

  try:
      venues = Venue.query.get(venue_id).first()
      # shows = Show.query.filter(Show.venue_id == venue_id).all()
      # db.session.delete(shows)
      db.session.delete(venues)
      db.session.commit()
      flash('The venue has been removed!')
  except:
      flash('Something went wrong')
      db.session.rollback()
  finally:
      db.session.close()
      return redirect(url_for('venues'))



#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data= Artist.query.all()

  return render_template('pages/artists.html', artists= data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  s_term = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike('%' + s_term + '%')).all()
  response={
    "count": Artist.query.filter(Artist.name.ilike('%' + s_term + '%')).count(),
    "data": [artist.get_artist() for artist in artists]
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  artists = Artist.query.all()
  data = list(filter(lambda d: d['id'] == artist_id, [artist.get_artist() for artist in artists]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  # TODO: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.get(artist_id)

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  try:
      artist = Artist.query.get(artist_id)
      artist.name = request.form['name']
      artist.city = request.form['city']
      artist.state = request.form['state']
      artist.phone = request.form['phone']
      artist.genres = request.form.getlist('genres')
      artist.facebook_link = request.form['facebook_link']
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except:
      error = True
      db.session.rollback()
  finally:
      db.session.close()
  if error:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be Updated.')
  else:
      return redirect(url_for('show_artist', artist_id=artist_id))



@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  error = False
  try:
      venue = Venue.query.get(venue_id)
      venue.name = request.form['name']
      venue.city = request.form['city']
      venue.state = request.form['state']
      venue.phone = request.form['phone']
      venue.genres = request.form.getlist('genres')
      venue.facebook_link = request.form['facebook_link']
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except:
      error = True
      db.session.rollback()
  finally:
      db.session.close()
  if error:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be Updated.')
  else:
       return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  try:
      name = request.form['name']
      city = request.form['city']
      state = request.form['state']
      phone = request.form['phone']
      genres = request.form.getlist('genres')
      facebook_link = request.form['facebook_link']
      new_artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link)
      db.session.add(new_artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
      error = True
      db.session.rollback()
  finally:
      db.session.close()
  if error:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
      return redirect(url_for('create_artist_form'))
  else:
      return render_template('pages/home.html')

  # on successful db insert, flash success

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  shows = Show.query.filter(Show.start_time > datetime.now()).all()
  data = [show.get_show() for show in shows]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():

    error = False
    try:
        venue_id = request.form['venue_id']
        artist_id = request.form['artist_id']
        start_time = request.form['start_time']
        new_show = Show(venue_id=venue_id, artist_id=artist_id, start_time=start_time)
        db.session.add(new_show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Show could not be listed.')
        return redirect(url_for('create_shows'))
    else:
        return render_template('pages/home.html')
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

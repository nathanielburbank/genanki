import json

from .apkg_col import APKG_COL
from datetime import datetime


class OptionsGroup:
  def __init__(
      self, options_id=None, options_group_name=None,
      # Organized according to options window tabs in Anki.
      ## General ##
      max_time_per_answer = 60,     # minutes
      show_timer = False,
      autoplay_audio = True,
      replay_audio_for_answer = True,
      ## New Cards ##
      new_steps = [1, 10],          # list of minute intervals per learning stage
      order = 1,                    # option selected in dropdown
                                    # (0 = first, 1 = second)
      new_cards_per_day = 20,       # days
      graduating_interval = 1,      # days
      easy_interval = 4,            # days
      starting_ease = 2500,         # 2500 = 250%
      bury_related_new_cards = True,
      ## Reviews ##
      max_reviews_per_day = 100,
      easy_bonus = 1.3,
      interval_modifier = 1.0,
      max_interval = 36500,    # days
      bury_related_review_cards = True,
      ## Lapses ##
      lapse_steps = [10],
      leech_interval_multiplier = 0,
      lapse_min_interval = 1,
      leech_threshold = 8,
      leech_action = 0,
      # Used for adding arbitrary options via JSON string. Useful for
      # addons.
      misc = ''
  ):
    self.options_id = options_id
    self.options_group_name = options_group_name
    ## General ##
    self.max_time_per_answer = max_time_per_answer
    self.show_timer = show_timer
    self.autoplay_audio = autoplay_audio
    self.replay_audio_for_answer = replay_audio_for_answer
    ## New Cards ##
    self.new_steps = new_steps
    self.order = order
    self.new_cards_per_day = new_cards_per_day
    self.graduating_interval = graduating_interval
    self.easy_interval = easy_interval
    self.starting_ease = starting_ease
    self.bury_related_new_cards = bury_related_new_cards
    ## Reviews ##
    self.max_reviews_per_day = max_reviews_per_day
    self.easy_bonus = easy_bonus
    self.interval_modifier = interval_modifier
    self.max_interval = max_interval
    self.bury_related_review_cards = bury_related_review_cards
    ## Lapses ##
    self.lapse_steps = lapse_steps
    self.leech_interval_multiplier = leech_interval_multiplier
    self.lapse_min_interval = lapse_min_interval
    self.leech_threshold = leech_threshold
    self.leech_action = leech_action

    self.misc = misc

  def validate(self):
    if self.misc and self.misc[-1] != ',':
      self.misc += ','

  def _format_fields(self):
    self.validate()
    fields = {}
    for key, value in self.__dict__.items():
      if key.startswith('__') or callable(key):
        continue
      if type(value) is bool:
        fields[key] = str(value).lower()
      else:
        fields[key] = str(value)
    return fields


class Deck:
  def __init__(self, deck_id=None, name=None, description='', options=None):
    self.deck_id = deck_id
    self.name = name
    self.description = description
    self.creation_time = datetime.now()
    self.notes = []
    self.models = {}  # map of model id to model
    self.options = options or OptionsGroup()

  def add_note(self, note):
    self.notes.append(note)

  def add_model(self, model):
    self.models[model.model_id] = model

  def write_to_db(self, cursor, now_ts):
    if not isinstance(self.deck_id, int):
      raise TypeError('Deck .deck_id must be an integer, not {}.'.format(self.deck_id))
    if not isinstance(self.name, str):
      raise TypeError('Deck .name must be a string, not {}.'.format(self.name))

    for note in self.notes:
      self.add_model(note.model)
    models = {model.model_id: model.to_json(now_ts, self.deck_id) for model in self.models.values()}

    #cursor.execute(APKG_COL, [self.name, self.deck_id, json.dumps(models), self.desc])
    params = self.options._format_fields()

    params.update({
      'creation_time': int(self.creation_time.timestamp()),
      'modification_time': int(self.creation_time.timestamp()) * 1000,
      'name': self.name,
      'deck_id': self.deck_id,
      'models': json.dumps(models),
      'description': self.description,
    })
    print(params)
  
    cursor.execute(APKG_COL, params)


    for note in self.notes:
      note.write_to_db(cursor, now_ts, self.deck_id)

  def write_to_file(self, file):
    """
    Write this deck to a .apkg file.
    """
    from .package import Package
    Package(self).write_to_file(file)

  def write_to_collection_from_addon(self):
    """
    Write to local collection. *Only usable when running inside an Anki addon!* Only tested on Anki 2.1.

    This writes to a temporary file and then calls the code that Anki uses to import packages.

    Note: the caller may want to use mw.checkpoint and mw.reset as follows:

      # creates a menu item called "Undo Add Notes From MyAddon" after this runs
      mw.checkpoint('Add Notes From MyAddon')
      # run import
      my_package.write_to_collection_from_addon()
      # refreshes main view so new deck is visible
      mw.reset()

    Tip: if your deck has the same name and ID as an existing deck, then the notes will get placed in that deck rather
    than a new deck being created.
    """
    from .package import Package
    Package(self).write_to_collection_from_addon()

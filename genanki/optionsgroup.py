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

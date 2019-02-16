from cached_property import cached_property

from .card import Card
from .util import guid_for

class Note:
  def __init__(self, model=None, fields=None, sort_field=None, tags=None, guid=None, note_id='null', card_id='null', csum=0):
    self.model = model
    self.fields = fields
    self.sort_field = sort_field
    self.tags = tags or []
    self.note_id = note_id
    self.card_id = card_id
    self.csum = csum
    try:
      self.guid = guid
    except AttributeError:
      # guid was defined as a property
      pass

  @property
  def sort_field(self):
    return self._sort_field or self.fields[0]

  @sort_field.setter
  def sort_field(self, val):
    self._sort_field = val

  # We use cached_property instead of initializing in the constructor so that the user can set the model after calling
  # __init__ and it'll still work.
  @cached_property
  def cards(self):
    rv = []
    for card_ord, any_or_all, required_field_ords in self.model._req:
      op = {'any': any, 'all': all}[any_or_all]
      if op(self.fields[ord_] for ord_ in required_field_ords):
        rv.append(Card(card_ord))
    return rv

  @property
  def guid(self):
    if self._guid is None:
      return guid_for(*self.fields)
    return self._guid

  @guid.setter
  def guid(self, val):
    self._guid = val

  def write_to_db(self, cursor, now_ts, deck_id):
    cursor.execute('INSERT INTO notes VALUES(?,?,?,?,?,?,?,?,?,?,?);', (
        self.note_id,                  #note_id
        self.guid,                    # guid
        self.model.model_id,          # mid
        now_ts,                       # mod
        -1,                           # usn
        self._format_tags(),          # TODO tags
        self._format_fields(),        # flds
        self.sort_field,              # sfld
        self.csum,                    # csum, can be ignored
        0,                            # flags
        '',                           # data
    ))


    note_id = cursor.lastrowid if self.note_id == 'null' else self.note_id
    for card in self.cards:
      card.write_to_db(cursor, now_ts, deck_id, note_id, self.card_id)

  def _format_fields(self):
    return '\x1f'.join(self.fields)

  def _format_tags(self):
    return ' ' + ' '.join(self.tags) + ' '

class Plugin:
  def __init__(self, app):
    self.app = app
    self.register_message_handler()

  def register_message_handler(self):
    return
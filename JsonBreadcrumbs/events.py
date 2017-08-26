import time
import sublime_plugin
import sublime

try:
    set_timeout = sublime.set_timeout_async
except AttributeError:
    set_timeout = sublime.set_timeout


NEW = 1
CLONE = 2
LOAD = 4
PRE_SAVE = 8
POST_SAVE = 16
MODIFIED = 32
SELECTION_MODIFIED = 64
ACTIVATED = 128
DEACTIVATED = 256
SYNTAX_CHANGE = 512

class JsonWhereEventListener(sublime_plugin.EventListener):
    def __init__(self):
        """Initialize GitGutterEvents object."""
        self.view_events = {}
        super(JsonWhereEventListener, self).__init__()

    def on_new(self, view):
        self.debounce(view, NEW)

    def on_load(self, view):
        """Run git_gutter after loading, if view is valid.

        Arguments:
            view (View): The view which received the event.
        """
        self.debounce(view, LOAD)

    def on_close(self, view):
        """Clean up the debounce dictionary.

        Arguments:
            view (View): The view which received the event.
        """
        key = view.id()
        if key in self.view_events:
            del self.view_events[key]

    def on_clone(self, view):
        """Run git_gutter for a cloned view.

        Arguments:
            view (View): The view which received the event.
        """
        self.debounce(view, CLONE)

    def on_selection_modified(self, view):
        self.debounce(view, SELECTION_MODIFIED)

    def on_syntax_change(self, view):
        self.debounce(view, SYNTAX_CHANGE)

    def debounce(self, view, event_id):
        """Invoke evaluation of changes after some idle time.

        Arguments:
            view (View): The view to perform evaluation for
            event_id (int): The event identifier
        """
        key = view.id()
        if key not in self.view_events:
            self.view_events[key] = ViewEventListener(view)
            view.settings().add_on_change('syntax', lambda v=view: self.on_syntax_change(v))

        self.view_events[key].push(event_id)

class ViewEventListener(object):
    """The class queues and forwards view events to GitGutterCommand.

    A ViewEventListener object queues all events received from a view and
    starts a single sublime timer to forward the event to GitGutterCommand
    after some idle time. This ensures not to bloat sublime API due to dozens
    of timers running for debouncing events.
    """

    def __init__(self, view):
        """Initialize ViewEventListener object.

        Arguments:
            view (View): The view the object is created for.
        """
        self.view = view
        # view aware git gutter settings
        # timer is running flag
        self.busy = False
        # a binary combination of above events
        self.events = 0
        # latest time of append() call
        self.latest_time = 0.0
        # debounce delay in milliseconds
        self.delay = 0

    def push(self, event_id):
        """Push the event to the queue and start idle timer.

        Add the event identifier to 'events' and update the 'latest_time'.
        This marks an event to be received rather than counting the number
        of received events. The idle timer is started only, if no other one
        is already in flight.

        Arguments:
            event_id (int): One of the event identifiers.
        """
        self.latest_time = time.time()
        self.events |= event_id
        if not self.busy:
            self.delay = 200
            self.start_timer(200)


    def start_timer(self, delay):
        """Run GitGutterCommand after some idle time.
        Check if no more events were received during idle time and run
        GitGutterCommand if not. Restart timer to check later, otherwise.
        Timer is stopped without calling GitGutterCommand, if a view is not
        visible to save some resources. Evaluation will be triggered by
        activating the view next time.
        Arguments:
            delay (int): The delay in milliseconds to wait until probably
                forward the events, if no other event was received in the
                meanwhile.
        """
        start_time = self.latest_time

        def worker():
            """The function called after some idle time."""
            
            if start_time < self.latest_time:
                self.start_timer(self.delay)
                return

            self.busy = False
            if not self.is_view_visible():
                return
            self.view.run_command('json_where', {'events': self.events})
            self.events = 0

            
        self.busy = True
        set_timeout(worker, delay)

    def is_view_visible(self):
        """Determine if the view is visible.
        Only an active view of a group is visible.
        Returns:
            bool: True if the view is visible in any window.
        """
        window = self.view.window()
        if window:
            view_id = self.view.id()
            for group in range(window.num_groups()):
                active_view = window.active_view_in_group(group)
                if active_view and active_view.id() == view_id:
                    return True
        return False



# -*- coding: utf-8 -*-
"""Entities related to google analytics."""

from datetime import datetime
from pyanalytics import utils
from pyanalytics import requests


# pylint: disable=R0903,W0142
class GAException(object):

    """Specifies the description of an exception.

    properties:
    description: Specifies the description of an exception - exd.
    is_fatal: Specifies whether the exception was fatal - exf. (0|1)
    """

    def __init__(self, description=None, is_fatal=False):
        self.description = description
        self.is_fatal = int(is_fatal)

    def __setattr__(self, name, value):
        if name == 'is_fatal' and not isinstance(value, bool):
            raise ValueError('is_fatal not valid, should be boolean.')


class Event(object):

    """
    Represents an Event: http://goo.gl/jkZvdo

    Properties:
    category -- The general event category
    action -- The action for the event
    label -- An optional descriptor for the event
    value -- An optional value associated with the event. You can see your
             event values in the Overview, Categories, and Actions reports,
             where they are listed by event or aggregated across events,
             depending upon your report view.
    """

    def __init__(self, category=None, action=None, label=None, value=None):
        self.category = category
        self.action = action
        self.label = label
        self.value = value

    def validate(self):
        """Validate event parameters."""
        if not(self.category and self.action):
            raise ValueError(
                'Events, at least need to have a category and action defined.')

    def __setattr__(self, name, value):
        if name == 'value' and not isinstance(value, int):
            raise ValueError(
                'Event value must be specified in integer.')
        object.__setattr__(self, name, value)


class Page(object):

    """
    Contains all parameters needed for tracking a page

    Properties:
    path -- Page request URI, will be mapped to "dl" parameter
    title -- Page title, will be mapped to "dt" parameter
    charset -- Charset encoding, will be mapped to "de" parameter
    referrer -- Referer URL, will be mapped to "dr" parameter
    load_time -- Page load time in milliseconds, will be encoded into
        "plt" parameter.

    """

    def __init__(self, path):
        self.path = None
        self.title = None
        self.charset = None
        self.referrer = None
        self.load_time = 0

        if path:
            self.path = path

    def __setattr__(self, name, value):
        if name == 'path' and value and value != '' and value[0] != '/':
            raise ValueError(
                'The page path should always start with a slash ("/").')
        elif name == 'load_time' and not isinstance(value, int):
            raise ValueError(
                'Page load time must be specified in integer milliseconds.')
        object.__setattr__(self, name, value)


class Session(object):

    """
    You should serialize this object and store it in the user session to keep
    it persistent between requests (similar to the "__umtb" cookie of the
    GA Javascript client).

    Properties:
    session_id -- A unique per-session ID, will be mapped to "cid" parameter
    track_count -- The amount of pageviews that were tracked within this
                   session so far. Will get incremented automatically upon each
                   request.
    start_time -- Timestamp of the start of this new session.

    """

    def __init__(self):
        self.session_id = utils.get_32bit_random_num()
        self.track_count = 0
        self.start_time = datetime.utcnow()

    @staticmethod
    def generate_session_id():
        """Generate and return session id."""
        return utils.get_32bit_random_num()

    def extract_from_utmb(self, utmb):
        """
        Will extract information for the "trackCount" and "startTime"
        properties from the given session cookie value.
        """
        parts = utmb.split('.')
        if len(parts) != 4:
            raise ValueError('The given cookie value is invalid.')

        self.track_count = int(parts[1])
        self.start_time = utils.convert_ga_timestamp(parts[3])
        return self


class Tracker(object):

    """
    Act like a Manager of all files

    Properties:
    account_id -- Google Analytics ID, will be mapped to "tid" parameter
    hostname -- Host Name, will be mapped to "dh" parameter
    """
    config = requests.Config()

    def __init__(self, account_id='', host_name=None, conf=None):
        self.account_id = account_id
        self.host_name = host_name
        if isinstance(conf, requests.Config):
            Tracker.config = conf

    def track_pageview(self, page, session, visitor):
        """Equivalent of _trackPageview() in GA Javascript client."""
        params = {
            'tracker': self,
            'visitor': visitor,
            'session': session,
            'page': page,
        }
        request = requests.PageViewRequest(**params)
        request.fire()

    def track_event(self, event, session, visitor, page):
        """Equivalent of _trackEvent() in GA Javascript client."""
        event.validate()

        params = {
            'tracker': self,
            'visitor': visitor,
            'session': session,
            'page': page,
            'event': event
        }
        request = requests.EventRequest(**params)
        request.fire()


class Visitor(object):

    """
    You should serialize this object and store it in the user database to
    keep it persistent for the same user permanently (similar to the "__umta"
    cookie of the GA Javascript client).

    Properties:
    :: Will be part of the "__utma" cookie parameter
    unique_id -- Unique user ID, will be part of the "uid"
    ip_address -- IP Address of the end user, will be mapped to "uip"
                  parameter and "X-Forwarded-For" request header
    user_agent -- User agent string of the end user,
                  will be mapped to "User-Agent" request header
    locale -- Locale string (country part optional) will be mapped to
              "ul" parameter
    """

    def __init__(self):
        self.ip_address = None
        self.unique_id = None
        self.user_agent = None
        self.locale = None
        self.source = None

    def __setattr__(self, name, value):
        if name == 'unique_id':
            if value and value < 0 or value > 0x7fffffff:
                raise ValueError(
                    ('Visitor unique ID has to be a 32-bit integer'
                     'between 0 and 0x7fffffff: ' + value))
        object.__setattr__(self, name, value)

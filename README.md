## PyAnalytics

Google Analytics collection api - now use it in server as well (not just client). You can track your server side  request / API request which are not possible using client js of Google Analytics.

### Use Cases

* Multiplayer games
* Mobile applications
* Flash applications / games
* File download track such as images, pdf, etc

### Features

* PageView
* Events

### Installation

You can install pyanalytics from below methods:

#### pip

```
pip install pyanalytics
```

#### git

```
git clone https://github.com/zonito/PyAnalytics.git
```

#### [Quack](https://github.com/Autodesk/quack)

Configure below snippet in quack.yaml

```yaml
modules:
  pyanalytic:
    repository: https://github.com/zonito/PyAnalytics.git
    path: pyanalytics
```

and then just run 

```
quack
```

### Usages Example

Below are the example on how to use PyAnalytics,

#### Page View

```python

from PyAnalytics import Config
from PyAnalytics import Tracker

def _get_page(self):
    """Return page object."""
    page = Page('/to/the/tracking/path')
    page.referrer = 'http://google.com/referrer'
    page.load_time = 100
    return page

def _get_session(self):
    """Return session object."""
    session = Session()
    session.session_id = self.post_data.get('user_id')
    return session

def _get_visitor(self):
    """Return visitor object."""
    visitor = Visitor()
    visitor.user_agent = 'Android'
    visitor.locale = 'en'
    visitor.unique_id = int(self.post_data.get('user_id', 0))
    visitor.ip_address = env.get('REMOTE_ADDR', '1.0.0.0')
    return visitor

def track_pageview(self):
    """Track required information per api request."""
    conf = Config()
    tracker = Tracker(self.tracking_code, self.domain, conf=conf)
    tracker.track_pageview(
        self._get_page(),
        self._get_session(),
        self._get_visitor()
    )
```

#### Event tracking

```python
def _track_event(self, category=None, action=None, value=0):
    """Global method for sending GA."""
    conf = Config()
    tracker = Tracker(self.tracking_code, self.domain, conf=conf)
    tracker.track_event(
        Event(
            category=category,
            action=action,
            label='something',
            value=value
        ),
        self._get_session(),
        self._get_visitor(),
        self._get_page()
    )
```

### Contributing
We <3 issue submissions, and address your problem as quickly as possible!

If you want to write code:

* Fork the repository
* Create your feature branch (`git checkout -b my-new-feature`)
* Commit your changes (`git commit -am 'add some feature'`)
* Push to your branch (`git push origin my-new-feature`)
* Create a new Pull Request

## Join Chats

* [Telegram chat](https://telegram.me/pyanalytics)

![Analytics](https://ga-beacon.appspot.com/UA-68498210-3/pyanalytics/repo)

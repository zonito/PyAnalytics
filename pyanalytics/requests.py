"""Request classes for Google analytics."""

import urllib
import urllib2
import uuid
from pyanalytics import utils


# pylint: disable=R0903
class Config(object):

    """
    Configurations for Google Analytics: Server Side

    Properties:
    endpoint -- Google Analytics tracking request endpoint. Can be set to null
        to silently simulate (and log) requests without actually sending them.
    """

    def __init__(self):
        self.endpoint = 'http://www.google-analytics.com/collect'
        self.anonimize_ip_address = False
        self.protocol_version = 1
        self.request_timeout = 1


class CollectRequest(object):

    """
    Responsible to make http call and send collected information to
    /collect google analytics endpoint.
    """

    def __init__(self, config):
        self.config = None
        if isinstance(config, Config):
            self.config = config

    def build_http_request(self):
        """
        Build http request object to send information to google analytics.
        """
        params = self.build_parameters()
        query_string = urllib.urlencode(params.get_parameters())
        query_string = query_string.replace('+', '%20')

        # Mimic Javascript's encodeURIComponent() encoding for the query
        # string just to be sure we are 100% consistent with GA's Javascript
        # client
        query_string = utils.convert_to_uri_encoding(query_string)

        # Recent versions of collect use HTTP POST requests if the query string
        # is too long
        use_post = len(query_string) > 2036

        if not use_post:
            url = '%s?%s' % (self.config.endpoint, query_string)
            post = None
        else:
            url = self.config.endpoint
            post = query_string

        headers = {}
        headers['Host'] = self.config.endpoint.split('/')[2]
        headers['User-Agent'] = params.ua

        if use_post:
            headers['Content-Type'] = 'text/plain'
            headers['Content-Length'] = len(query_string)

        return urllib2.Request(url, post, headers)

    # pylint: disable=R0201
    def build_parameters(self):
        """Marker implementation"""
        return Parameters()

    def fire(self):
        """Send all required information to google analytics."""
        request = self.build_http_request()
        response = None

        #  Do not actually send the request if endpoint host is set to null
        if self.config.endpoint:
            response = urllib2.urlopen(
                request, timeout=self.config.request_timeout)

        return response


# pylint: disable=R0902
class Parameters(object):

    """
    Default parameters for all Google Analytics Measurement Protocol.
    Ref: http://goo.gl/WUEcJA

    properties:
    aid: Application ID
    aiid: Application Installer ID
    aip: Anonymize IP, default=1
    an: Application Name
    av: Application Version
    cc: Campaign Content
    cd: Screen Name
    ci: Campaign ID
    cid *: User - Client ID
    ck: Campaign Keyword
    clt: Content Load Time
    cm: Campaign Medium
    cn: Campaign Name
    cs: Campaign Source
    cu: Currency Code
    dclid: Google Display Ads ID
    de: Document Encoding
    dh: Document Host Name
    dl: Document location URL
    dns: DNS Time
    dp: Document Path
    dr: Document Referrer
    ds: Data Source, default=web
    dt: Document Title
    ea: Event Action
    ec: Event Category
    el: Event Label
    ev: Event Value
    exd: Exception Description
    exf: Is Exception Fatal?
    fl: Flash Version
    gclid: Google AdWords ID
    geoid: Geographical Override
    ht: Hit type
    ic: Item Code
    in: Item Name
    ip: Item Price
    iq: Item Quantity
    iv: Item Category
    je: Java Enabled
    linkid: Link ID
    ni: Non-Interaction Hit
    pdt: Page Download Time
    plt: Page Load Time
    qt: Queue Time
    rrt: Redirect Response Time
    sa: Social Action
    sc: Session Control (start|end)
    sd: Screen Colors
    sn: Social Network
    sr: Screen Resolution
    st: Social Action Target
    ta: Transaction Affiliation
    ti: Transaction ID
    tid *: Tracking ID / Web Property ID
    tr: Transaction Revenue
    ts: Transaction Shipping
    tt: Transaction Tax
    ua: User Agent Override
    uid: IP Override
    uid: User - User ID
    ul: User Language
    utc: User timing category
    utl: User timing label
    utt: User timing time
    utv: User timing variable name
    v: Protocol Version, default=1
    vp: Viewport size
    z *: Cache Buster
    """
    # pylint: disable=C0103
    de = 'UTF-8'
    dp = '/'
    ds = 'web'
    dr = dt = plt = t = aip = v = tid = ds = None
    cid = uid = uip = ua = ul = dh = dl = _u = None

    def get_parameters(self):
        """
        Get all collect request parameters out of the class in a dict form.
        Attributes starting with _ are cookie names, so we dont need them.
        """
        params = {}

        def updateParams(attribs):
            """Update params variable."""
            for attr in attribs:
                if attr[0] != '_' and attr != 'get_parameters':
                    val = getattr(self, attr)
                    if val:
                        params[attr] = val
        updateParams(vars(Parameters))
        updateParams(vars(self))
        return params


class Request(CollectRequest):

    """Request object / abstract class."""

    def __init__(self, tracker, visitor, session, page):
        super(Request, self).__init__(tracker.config)
        self.tracker = tracker
        self.visitor = visitor
        self.session = session
        self.page = page

    def build_parameters(self):
        """Build default parameters."""
        params = Parameters()
        config = self.tracker.config
        # pylint: disable=C0103
        params.aip = config.anonimize_ip_address
        params.v = config.protocol_version
        params.tid = self.tracker.account_id
        params.ds = self.visitor.source
        params.uid = self.session.session_id
        params.cid = str(
            uuid.uuid3(uuid.NAMESPACE_DNS, str(self.session.session_id)))
        params.uip = self.visitor.ip_address
        params.ua = self.visitor.user_agent
        params.ul = self.visitor.locale or 'en-us'
        params.dh = self.tracker.host_name
        params.dp = self.page.path
        params.dt = self.page.title
        params.plt = self.page.load_time
        params.dr = self.page.referrer
        if self.page.charset:
            params.de = self.page.charset
        return params


class PageViewRequest(Request):

    """Page view request."""

    def __init__(self, tracker, visitor, session, page):
        super(PageViewRequest, self).__init__(tracker, visitor, session, page)

    def build_parameters(self):
        """Build parameters specific to pageview."""
        params = super(PageViewRequest, self).build_parameters()
        params.t = 'pageview'
        return params


class EventRequest(Request):

    """Event request."""

    # pylint: disable=R0913
    def __init__(self, tracker, visitor, session, page, event):
        super(EventRequest, self).__init__(tracker, visitor, session, page)
        self.event = event

    def build_parameters(self):
        """Build parameters using Page object."""
        params = super(EventRequest, self).build_parameters()
        params.ec = self.event.category
        params.ea = self.event.action
        params.el = self.event.label
        params.ev = self.event.value
        params.t = 'event'
        return params

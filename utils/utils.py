from utils.constants import UserAgent, Render
from urllib.parse import urlparse
from utils.defaults import (
    DEFAULT_LIMIT_SERP,
    DEFAULT_DOMAIN,
    DEFAULT_START_PAGE,
    DEFAULT_USER_AGENT,
    DEFAULT_PAGES,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_TIMEOUT,
)


class BaseSearchOpts:
    def __init__(
        self,
        domain=DEFAULT_DOMAIN,
        start_page=DEFAULT_START_PAGE,
        pages=DEFAULT_PAGES,
        limit=DEFAULT_LIMIT_SERP,
        user_agent_type=DEFAULT_USER_AGENT,
        callback_url=None,
        parse_instructions=None,
        parse=False,
    ):
        self.domain = domain
        self.start_page = start_page
        self.pages = pages
        self.limit = limit
        self.user_agent_type = user_agent_type
        self.callback_url = callback_url
        self.parse_instructions = parse_instructions
        self.parse = parse


class BaseUrlOpts:
    def __init__(
        self,
        user_agent_type=DEFAULT_USER_AGENT,
        callback_url=None,
        parse_instructions=None,
        parse=False,
    ):
        self.user_agent_type = user_agent_type
        self.callback_url = callback_url
        self.parse_instructions = parse_instructions
        self.parse = parse


class BaseGoogleOpts:
    def __init__(
        self,
        geo_location=None,
        user_agent_type=DEFAULT_USER_AGENT,
        render=None,
        callback_url=None,
        parse_instructions=None,
        parse=False,
        context=None,
    ):
        self.geo_location = geo_location
        self.user_agent_type = user_agent_type
        self.render = render
        self.callback_url = callback_url
        self.parse_instructions = parse_instructions
        self.parse = parse
        self.context = context


def prepare_config(**kwargs):
    config = {}
    if "timeout" in kwargs:
        config["timeout"] = (
            kwargs["timeout"] if kwargs["timeout"] is not None else DEFAULT_TIMEOUT
        )
    if "poll_interval" in kwargs:
        config["poll_interval"] = (
            kwargs["poll_interval"]
            if kwargs["poll_interval"] is not None
            else DEFAULT_POLL_INTERVAL
        )
    return config


def validate_url(input_url, host):
    # Check if the URL is empty
    if not input_url:
        raise ValueError("URL parameter is empty")

    # Parse the URL
    parsed_url = urlparse(input_url)

    # Check if the scheme (protocol) is present and not empty
    if not parsed_url.scheme:
        raise ValueError("URL is missing scheme")

    # Check if the host is present and not empty
    if not parsed_url.netloc:
        raise ValueError("URL is missing a host")

    # Check if the host matches the expected domain or host
    if host not in parsed_url.netloc:
        raise ValueError(f"URL does not belong to {host}")

    return None


def check_user_agent_validity(user_agent_type):
    if not UserAgent.is_user_agent_valid(user_agent_type):
        raise ValueError(f"Invalid user agent parameter: {user_agent_type}")


def check_render_validity(render):
    if render and not Render.is_render_valid(render):
        raise ValueError(f"Invalid render parameter: {render}")


def check_domain_validity(domain, acceptable_domains):
    if domain and domain not in acceptable_domains:
        raise ValueError(f"Invalid domain parameter: {domain}")


def check_locale_validity(locale, acceptable_locales):
    if locale and locale not in acceptable_locales:
        raise ValueError(f"Invalid locale parameter: {locale}")


def check_limit_validity(limit):
    if limit <= 0:
        raise ValueError("Limit parameter must be greater than 0")


def check_pages_validity(pages):
    if pages <= 0:
        raise ValueError("Pages parameter must be greater than 0")


def check_start_page_validity(start_page):
    if start_page <= 0:
        raise ValueError("Start page parameter must be greater than 0")

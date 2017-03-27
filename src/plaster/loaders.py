import pkg_resources

from .exceptions import (
    LoaderNotFound,
    MultipleLoadersFound,
)
from .interfaces import ILoaderInfo
from .uri import parse_uri


def get_sections(config_uri):
    """
    Load the list of named sections.

    .. code-block:: python

        sections = plaster.get_sections('development.ini')
        full_config = {
            section: plaster.get_settings('development.ini', section)
            for section in sections
        }

    ``config_uri`` may be anything that can be parsed by
    :func:`plaster.parse_uri`.

    """
    loader = get_loader(config_uri)
    return loader.get_sections()


def get_settings(config_uri, section=None, defaults=None):
    """
    Load the settings from a named section.

    .. code-block:: python

        settings = plaster.get_settings(...)
        print(settings['foo'])

    ``config_uri`` may be anything that can be parsed by
    :func:`plaster.parse_uri`.

    If ``name`` is not ``None`` then it will be used. Otherwise, the ``name``
    will be populated by the fragment defined in the ``config_uri#name``
    syntax. If ``name`` is still ``None`` then a
    :class:`plaster.NoSectionError` error will be raised.

    Any values in ``defaults`` may be overridden by the loader prior to
    returning the final configuration dictionary.

    """
    loader = get_loader(config_uri)
    return loader.get_settings(section, defaults)


def setup_logging(config_uri, defaults=None):
    """
    Execute the logging configuration defined in the config file.

    This function should, at least, configure the Python standard logging
    module. However, it may also be used to configure any other logging
    subsystems that serve a similar purpose.

    ``config_uri`` may be anything that can be parsed by
    :func:`plaster.parse_uri`.

    """
    loader = get_loader(config_uri)
    return loader.setup_logging(defaults)


def get_loader(config_uri, protocol=None):
    """
    Find a :class:`plaster.ILoader` object capable of handling ``config_uri``.

    ``config_uri`` may be anything that can be parsed by
    :func:`plaster.parse_uri`.

    ``protocol`` may be a :term:`loader protocol` that the loader must
    satisfy to match the desired ``config_uri``.

    """
    config_uri = parse_uri(config_uri)
    requested_scheme = config_uri.scheme

    matched_loaders = find_loaders(requested_scheme, protocol=protocol)

    if len(matched_loaders) < 1:
        raise LoaderNotFound(requested_scheme, protocol=protocol)

    if len(matched_loaders) > 1:
        raise MultipleLoadersFound(
            requested_scheme, matched_loaders, protocol=protocol)

    loader_info = matched_loaders[0]
    loader = loader_info.load(config_uri)
    return loader


def find_loaders(scheme=None, protocol=None):
    """
    Find all loaders that match the ``config_uri`` and ``protocol``.

    ``scheme`` may be any valid scheme. Examples would be something like
    ``ini`` or ``ini+pastedeploy``. If ``None`` then loaders matching any
    scheme will be returned.

    ``protocol`` may be a :term:`loader protocol` that the loader must
    satisfy to match the desired ``config_uri``. If ``None`` then only
    non-protocol-specific loaders will be returned.

    Returns a list containing zero or more :class:`plaster.ILoaderInfo`
    objects.

    """
    matched_entry_points = []

    if protocol is None:
        group = 'plaster.loader_factory'
    else:
        group = 'plaster.loader_factory.' + protocol

    if scheme is not None:
        scheme = scheme.lower()

        parts = scheme.rsplit('+', 1)
        if len(parts) == 2:
            try:
                distro = pkg_resources.get_distribution(parts[1])
            except pkg_resources.DistributionNotFound:
                pass
            else:
                scheme = parts[0]
                for ep in distro.get_entry_map(group).values():
                    if scheme == ep.name.lower():
                        matched_entry_points.append(ep)

    # only search entry points for all packages if the scheme is not pointing
    # at an installed distribution that contains a matching entry point
    if not matched_entry_points:
        for ep in pkg_resources.iter_entry_points(group):
            if scheme is None or scheme == ep.name.lower():
                matched_entry_points.append(ep)

    return [
        EntryPointLoaderInfo(ep, protocol=protocol)
        for ep in matched_entry_points
    ]


class EntryPointLoaderInfo(ILoaderInfo):
    def __init__(self, ep, protocol=None):
        self.entry_point = ep
        self.scheme = '{0}+{1}'.format(ep.name, ep.dist.project_name)
        self.protocol = protocol

        self._factory = None

    @property
    def factory(self):
        if self._factory is None:
            self._factory = self.entry_point.load()
        return self._factory

    def load(self, config_uri):
        config_uri = parse_uri(config_uri)
        return self.factory(config_uri)

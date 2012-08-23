"""
Configuration Base Class
"""
import configuration  # python configuration module, not local!
import grp
import json
import logging
import requests
import socket
import os

logger = logging.getLogger(name=__name__)
logger.setLevel('DEBUG')

from leap.util.fileutil import (mkdir_p)


class BaseLeapConfig(object):
    slug = None

    # XXX we have to enforce that we have a slug (via interface)
    # get property getter that raises NI..

    def save(self):
        raise NotImplementedError("abstract base class")

    def load(self):
        raise NotImplementedError("abstract base class")

    def get_config(self, *kwargs):
        raise NotImplementedError("abstract base class")

    #XXX todo: enable this property after
    #fixing name clash with "config" in use at
    #vpnconnection

    #@property
    #def config(self):
        #return self.get_config()

    def get_value(self, *kwargs):
        raise NotImplementedError("abstract base class")


class JSONLeapConfig(BaseLeapConfig):

    def __init__(self, *args, **kwargs):
        # sanity check
        assert self.slug is not None
        assert self.spec is not None
        assert issubclass(self.spec, configuration.Configuration)

        self._config = self.spec()
        self._config.parse_args(list(args))

    # mandatory baseconfig interface

    def save(self, to=None):
        if to is None:
            to = self.filename
        self._config.serialize(to)

    def load(self, fromfile=None):
        # load should get a much more generic
        # argument. it could be, f.i., from_uri,
        # and call to Fetcher

        if fromfile is None:
            fromfile = self.filename
        self._config.deserialize(fromfile)

    def get_config(self):
        return self._config.config

    # public methods

    def get_filename(self):
        return self._slug_to_filename()

    @property
    def filename(self):
        return self.get_filename()

    def _slug_to_filename(self):
        # is this going to work in winland if slug is "foo/bar" ?
        folder, filename = os.path.split(self.slug)
        # XXX fix import
        config_file = get_config_file(filename, folder)
        return config_file

#
# utility functions
#
# (might be moved to some class as we see fit, but
# let's remain functional for a while)
#


def get_config_dir():
    """
    get the base dir for all leap config
    @rparam: config path
    @rtype: string
    """
    # TODO
    # check for $XDG_CONFIG_HOME var?
    # get a more sensible path for win/mac
    # kclair: opinion? ^^
    return os.path.expanduser(
        os.path.join('~',
                     '.config',
                     'leap'))


def get_config_file(filename, folder=None):
    """
    concatenates the given filename
    with leap config dir.
    @param filename: name of the file
    @type filename: string
    @rparam: full path to config file
    """
    path = []
    path.append(get_config_dir())
    if folder is not None:
        path.append(folder)
    path.append(filename)
    return os.path.join(*path)


def get_default_provider_path():
    default_subpath = os.path.join("providers",
                                   "default")
    default_provider_path = get_config_file(
        '',
        folder=default_subpath)
    return default_provider_path


def validate_ip(ip_str):
    """
    raises exception if the ip_str is
    not a valid representation of an ip
    """
    socket.inet_aton(ip_str)


def get_username():
    return os.getlogin()


def get_groupname():
    gid = os.getgroups()[-1]
    return grp.getgrgid(gid).gr_name


# json stuff

# XXX merge with JSONConfig
def get_config_json(config_file=None):
    """
    will replace get_config function be developing them
    in parralel for branch purposes.
    @param: configuration file
    @type: file
    @rparam: configuration turples
    @rtype: dictionary
    """
    if not config_file:
        fpath = get_config_file('eip.json')
        if not os.path.isfile(fpath):
            dpath, cfile = os.path.split(fpath)
            if not os.path.isdir(dpath):
                mkdir_p(dpath)
            with open(fpath, 'wb') as configfile:
                configfile.flush()
        config_file = open(fpath)

    config = json.load(config_file)

    return config


def get_definition_file(url=None):
    """
    """
    #TODO: determine good default location of definition file.
    r = requests.get(url)
    return r.json

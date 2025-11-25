__all__ = ['ConfigError', 'ConfigValueError', 'ConfigPlaceholderError']


class ConfigError(Exception):
    """Base class for exceptions raised when querying a configuration.
    """


class ConfigPlaceholderError(ConfigError):
    """The value of the placeholder in the configuration doesn't have an environment variable."""


class ConfigValueError(ConfigError):
    """The value in the configuration is illegal."""

"""Color Helper plugin."""
import re
import decimal
from ColorHelper.lib.rgba import RGBA, round_int, clamp
import sublime
from collections import OrderedDict
import os
import imp
import sys

loaded_plugins = OrderedDict()

FLOAT_TRIM_RE = re.compile(r'^(?P<keep>\d+)(?P<trash>\.0+|(?P<keep2>\.\d*[1-9])0+)$')


def fmt_float(f, p=0):
    """Set float precision and trim precision zeros."""

    string = str(
        decimal.Decimal(f).quantize(decimal.Decimal('0.' + ('0' * p) if p > 0 else '0'), decimal.ROUND_HALF_UP)
    )

    m = FLOAT_TRIM_RE.match(string)
    if m:
        string = m.group('keep')
        if m.group('keep2'):
            string += m.group('keep2')
    return string


def alpha_dec_normalize(dec):
    """Normailze a deciaml alpha value."""

    temp = float(dec)
    if temp < 0.0 or temp > 1.0:
        dec = fmt_float(clamp(float(temp), 0.0, 1.0), 3)
    alpha_dec = dec
    alpha = "%02X" % round_int(float(alpha_dec) * 255.0)
    return alpha, alpha_dec


def alpha_percent_normalize(perc):
    """Normailze a percent alpha value."""

    alpha_float = clamp(float(perc.strip('%')), 0.0, 100.0) / 100.0
    alpha_dec = fmt_float(alpha_float, 3)
    alpha = "%02X" % round_int(alpha_float * 255.0)
    return alpha, alpha_dec


def sublime_format_path(pth):
    """Format path for Sublime internally."""
    m = re.match(r"^([A-Za-z]{1}):(?:/|\\)(.*)", pth)
    if sublime.platform() == "windows" and m is not None:
        pth = m.group(1) + "/" + m.group(2)
    return pth.replace("\\", "/")


def get_plugins():
    """Get plugins."""

    return loaded_plugins


def load_modules():
    """Load bracket plugin modules."""

    settings = sublime.load_settings('color_helper.sublme-settings')
    plugins = settings.get(
        'color_plugins',
        [
            'ch_modules.hex', 'ch_modules.rgb', 'ch_modules.hsl',
            'ch_modules.hwb', 'ch_modules.gray', 'ch_modules.web_color'
        ]
    )
    for plugin in plugins:
        module = _import_module(plugin, loaded_plugins)
        for type_name in module.__dict__:
            try:
                t = module.__dict__[type_name]
                if issubclass(t, Color):
                    loaded_plugins[plugin] = t()
            except Exception:
                pass


def _import_module(module_name, loaded=None):
    """
    Import the module.

    Import the module and track which modules have been loaded
    so we don't load already loaded modules.
    """

    # Pull in built-in and custom plugin directory
    if module_name.startswith("ch_modules."):
        path_name = os.path.join("Packages", "ColorHelper", os.path.normpath(module_name.replace('.', '/')))
    else:
        path_name = os.path.join("Packages", os.path.normpath(module_name.replace('.', '/')))
    path_name += ".py"
    if module_name not in loaded:
        module = imp.new_module(module_name)
        sys.modules[module_name] = module
        exec(
            compile(
                sublime.load_resource(sublime_format_path(path_name)),
                module_name,
                'exec'
            ),
            sys.modules[module_name].__dict__
        )
    return sys.modules[module_name]


def import_module(module, attribute=None):
    """Import module or module attribute."""

    mod = _import_module(module)
    return getattr(mod, attribute) if attribute is not None else mod


class Color(object):
    """Color Object."""

    def get_keys(self):
        return tuple()

    def get_regex(self):
        """Get regex."""
        return None

    def get_incomplete_regex(self):
        """Get incomplete regex."""
        return None

    def evaluate(self, m, **kwargs):
        return None, None, None

    def is_valid(self, color, **kwargs):
        return False

    def format(self, color, **kwargs):
        return color

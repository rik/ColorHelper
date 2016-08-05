"""
ColorHelper.

Copyright (c) 2015 - 2016 Isaac Muse <isaacmuse@gmail.com>
License: MIT
"""
import sublime
import re
import decimal
from ColorHelper.lib import csscolors
from ColorHelper.lib.rgba import RGBA, round_int, clamp
from textwrap import dedent
from ColorHelper import ch_plugin

fmt_float = ch_plugin.fmt_float

BETTER_CSS_SUPPORT = int(sublime.version()) >= 3119

TAG_HTML_RE = re.compile(
    br'''(?x)(?i)
    (?:
        (?P<comments>(\r?\n?\s*)<!--[\s\S]*?-->(\s*)(?=\r?\n)|<!--[\s\S]*?-->)|
        (?P<style><style((?:\s+[\w\-:]+(?:\s*=\s*(?:"[^"]*"|'[^']*'|[^>\s]+))?)*)\s*>(?P<css>.*?)<\/style[^>]*>) |
        (?P<open><[\w\:\.\-]+)
        (?P<attr>(?:\s+[\w\-:]+(?:\s*=\s*(?:"[^"]*"|'[^']*'))?)*)
        (?P<close>\s*(?:\/?)>)
    )
    ''',
    re.DOTALL
)

TAG_STYLE_ATTR_RE = re.compile(
    br'''(?x)
    (?P<attr>
        (?:
            \s+style
            (?:\s*=\s*(?P<content>"[^"]*"|'[^']*'))
        )
    )
    ''',
    re.DOTALL
)

color_re = None
color_all_re = None

ADD_CSS = dedent(
    '''
    {% if var.sublime_version >= 3119 %}
    .color-helper.content { margin: 0; padding: 0.5rem; }
    .color-helper .small { font-size: 0.7rem; }
    .color-helper .alpha { text-decoration: underline; }
    {% else %}
    .color-helper.content { margin: 0; padding: 0.5em; }
    .color-helper.small { font-size: {{'*.8px'|relativesize}}; }
    .color-helper.alpha { text-decoration: underline; }
    {% endif %}
    '''
)

WRAPPER_CLASS = "color-helper content"
LEGACY_CLASS = '' if BETTER_CSS_SUPPORT else 'color-helper'

CSS3 = ("webcolors", "hex", "hex_compressed", "rgb", "rgba", "hsl", "hsla")
CSS4 = CSS3 + ("gray", "graya", "hwb", "hwba", "hexa", "hexa_compressed")
ALL = CSS4


def log(*args):
    """Log."""

    text = ['\nColorHelper: ']
    for arg in args:
        text.append(str(arg))
    text.append('\n')
    print(''.join(text))


def debug(*args):
    """Log if debug enabled."""

    if sublime.load_settings("color_helper.sublime-settings").get('debug', False):
        log(*args)


def color_picker_available():
    """Check if color picker is available."""

    s = sublime.load_settings('color_helper_share.sublime-settings')
    s.set('color_pick_return', None)
    sublime.run_command('color_pick_api_is_available', {'settings': 'color_helper_share.sublime-settings'})
    return s.get('color_pick_return', None)


def get_rules(view):
    """Get auto-popup scope rule."""

    rules = view.settings().get("color_helper.scan", {})

    return rules if rules.get("enabled", False) else None


def get_scope(view, rules, skip_sel_check=False):
    """Get auto-popup scope rule."""

    scopes = None
    if rules is not None:
        scopes = ','.join(rules.get('scan_scopes', []))
        sels = view.sel()
        if not skip_sel_check:
            if len(sels) == 0 or not scopes or view.score_selector(sels[0].begin(), scopes) == 0:
                scopes = None
    return scopes


def get_scope_completion(view, rules, skip_sel_check=False):
    """Get additional auto-popup scope rules for incomplete colors only."""

    scopes = None
    if rules is not None:
        scopes = ','.join(rules.get('scan_completion_scopes', []))
        sels = view.sel()
        if not skip_sel_check:
            if len(sels) == 0 or not scopes or view.score_selector(sels[0].begin(), scopes) == 0:
                scopes = None
    return scopes


def get_favs():
    """Get favorites object."""

    bookmark_colors = sublime.load_settings('color_helper.palettes').get("favorites", [])
    return {"name": "Favorites", "colors": bookmark_colors}


def save_palettes(palettes, favs=False):
    """Save palettes."""

    s = sublime.load_settings('color_helper.palettes')
    if favs:
        s.set('favorites', palettes)
    else:
        s.set('palettes', palettes)
    sublime.save_settings('color_helper.palettes')


def save_project_palettes(window, palettes):
    """Save project palettes."""

    data = window.project_data()
    if data is None:
        data = {'color_helper_palettes': palettes}
    else:
        data['color_helper_palettes'] = palettes
    window.set_project_data(data)


def get_palettes():
    """Get palettes."""

    return sublime.load_settings('color_helper.palettes').get("palettes", [])


def get_project_palettes(window):
    """Get project palettes."""
    data = window.project_data()
    if data is None:
        data = {}
    return data.get('color_helper_palettes', [])


def get_project_folders(window):
    """Get project folder."""
    data = window.project_data()
    if data is None:
        data = {'folders': [{'path': f} for f in window.folders()]}
    return data.get('folders', [])


def get_color_regex(full=False):
    """Get color regex."""
    global color_re
    global color_all_re

    if color_re is None or color_all_re is None:
        regex = []
        for plugin in ch_plugin.get_plugins().values():
            r = plugin.get_regex()
            if r:
                regex.append(r)
        color_re = re.compile(r'(?x)(?i)(?<![@#$.\-_])(?:%s)(?![@#$.\-_])' % '|'.join(regex))

        incomplete_regex = []
        for plugin in ch_plugin.get_plugins().values():
            r = plugin.get_incomplete_regex()
            if r:
                incomplete_regex.append(r)
        color_re = re.compile(r'(?x)(?i)(?<![@#$.\-_])(?:%s)(?![@#$.\-_])' % '|'.join(regex + incomplete_regex))
    return color_all_re if full else color_re


def translate_color(m, use_hex_argb=False):
    """Translate the match object to a color w/ alpha."""

    args = {'m': m, 'use_hex_argb': use_hex_argb}

    color = None
    alpha = None
    alpha_dec = None
    for plugin in ch_plugin.get_plugins().values():
        color, alpha, alpha_dec = plugin.evaluate(**args)
        if color is not None:
            break

    return color, alpha, alpha_dec

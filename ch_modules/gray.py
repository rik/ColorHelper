"""GRAY."""
import re
from ColorHelper import ch_plugin

COLOR_PARTS = {
    "percent": r"[+\-]?(?:(?:\d*\.\d+)|\d+)%",
    "float": r"[+\-]?(?:(?:\d*\.\d+)|\d+)"
}

HEX_IS_GRAY_RE = re.compile(r'(?i)^#([0-9a-f]{2})\1\1')


class Gray(ch_plugin.Color):
    """Gray object."""

    keys = ('gray', 'graya')
    incomplete_keys = ('gray_open',)

    def get_keys(self):
        return self.keys

    def get_regex(self):
        """Get regex."""
        return r'''
            \b(?P<gray>gray\(\s*(?P<gray_content>%(float)s|%(percent)s)\s*\)) |
            \b(?P<graya>gray\(\s*(?P<graya_content>
                (?:%(float)s|%(percent)s)\s*,\s*(?:%(percent)s|%(float)s)
            )\s*\))
        ''' % COLOR_PARTS

    def get_incomplete_regex(self):
        """Get incomplete regex."""
        return r'\b(?P<gray_open>gray\()'

    def is_valid(self, color, **kwargs):
        """Check if color is gray (all channels the same)."""

        m = HEX_IS_GRAY_RE.match(color)
        return m is not None

    def evaluate(self, m, **kwargs):
        color = None
        alpha = None
        alpha_dec = None

        if m.group('gray'):
            content = m.group('gray_content')
            if content.endswith('%'):
                g = ch_plugin.round_int(ch_plugin.clamp(float(content.strip('%')), 0.0, 255.0) * (255.0 / 100.0))
            else:
                g = ch_plugin.clamp(ch_plugin.round_int(float(content)), 0, 255)
            color = "#%02x%02x%02x" % (g, g, g)
        elif m.group('graya'):
            content = [x.strip() for x in m.group('graya_content').split(',')]
            if content[0].endswith('%'):
                g = ch_plugin.round_int(ch_plugin.clamp(float(content[0].strip('%')), 0.0, 255.0) * (255.0 / 100.0))
            else:
                g = ch_plugin.clamp(ch_plugin.round_int(float(content[0])), 0, 255)
            color = "#%02x%02x%02x" % (g, g, g)
            if content[1].endswith('%'):
                alpha, alpha_dec = ch_plugin.alpha_percent_normalize(content[1])
            else:
                alpha, alpha_dec = ch_plugin.alpha_dec_normalize(content[1])
        return color, alpha, alpha_dec

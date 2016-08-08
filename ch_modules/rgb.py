"""RGB."""
from ColorHelper import ch_plugin

COLOR_PARTS = {
    "percent": r"[+\-]?(?:(?:\d*\.\d+)|\d+)%",
    "float": r"[+\-]?(?:(?:\d*\.\d+)|\d+)"
}


class Rgb(ch_plugin.Color):
    """RGB object."""

    keys = ('rgb', 'rgba')
    incomplete_keys = ('rgb_open', 'rgba_open')

    def get_keys(self):
        return self.keys

    def get_regex(self):
        """Get regex."""
        return r'''
            \b(?P<rgb>rgb\(\s*(?P<rgb_content>
                (?:%(float)s\s*,\s*){2}%(float)s | (?:%(percent)s\s*,\s*){2}%(percent)s
            )\s*\)) |
            \b(?P<rgba>rgba\(\s*(?P<rgba_content>
                (?:%(float)s\s*,\s*){3}(?:%(percent)s|%(float)s) | (?:%(percent)s\s*,\s*){3}(?:%(percent)s|%(float)s)
            )\s*\))
        ''' % COLOR_PARTS

    def get_incomplete_regex(self):
        """Get incomplete regex."""
        return r'''
            \b(?P<rgb_open>rgb\() |
            \b(?P<rgba_open>rgba\()
        '''

    def evaluate(self, m, **kwargs):
        color = None
        alpha = None
        alpha_dec = None

        if m.group('rgb'):
            content = [x.strip() for x in m.group('rgb_content').split(',')]
            if content[0].endswith('%'):
                r = ch_plugin.round_int(ch_plugin.clamp(float(content[0].strip('%')), 0.0, 255.0) * (255.0 / 100.0))
                g = ch_plugin.round_int(ch_plugin.clamp(float(content[1].strip('%')), 0.0, 255.0) * (255.0 / 100.0))
                b = ch_plugin.round_int(ch_plugin.clamp(float(content[2].strip('%')), 0.0, 255.0) * (255.0 / 100.0))
                color = "#%02x%02x%02x" % (r, g, b)
            else:
                color = "#%02x%02x%02x" % (
                    ch_plugin.clamp(ch_plugin.round_int(float(content[0])), 0, 255),
                    ch_plugin.clamp(ch_plugin.round_int(float(content[1])), 0, 255),
                    ch_plugin.clamp(ch_plugin.round_int(float(content[2])), 0, 255)
                )
        elif m.group('rgba'):
            content = [x.strip() for x in m.group('rgba_content').split(',')]
            if content[0].endswith('%'):
                r = ch_plugin.round_int(ch_plugin.clamp(float(content[0].strip('%')), 0.0, 255.0) * (255.0 / 100.0))
                g = ch_plugin.round_int(ch_plugin.clamp(float(content[1].strip('%')), 0.0, 255.0) * (255.0 / 100.0))
                b = ch_plugin.round_int(ch_plugin.clamp(float(content[2].strip('%')), 0.0, 255.0) * (255.0 / 100.0))
                color = "#%02x%02x%02x" % (r, g, b)
            else:
                color = "#%02x%02x%02x" % (
                    ch_plugin.clamp(ch_plugin.round_int(float(content[0])), 0, 255),
                    ch_plugin.clamp(ch_plugin.round_int(float(content[1])), 0, 255),
                    ch_plugin.clamp(ch_plugin.round_int(float(content[2])), 0, 255)
                )
            if content[3].endswith('%'):
                alpha, alpha_dec = ch_plugin.alpha_percent_normalize(content[3])
            else:
                alpha, alpha_dec = ch_plugin.alpha_dec_normalize(content[3])
        return color, alpha, alpha_dec

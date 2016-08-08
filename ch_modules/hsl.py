"""HSL."""
from ColorHelper import ch_plugin

COLOR_PARTS = {
    "percent": r"[+\-]?(?:(?:\d*\.\d+)|\d+)%",
    "float": r"[+\-]?(?:(?:\d*\.\d+)|\d+)"
}


class Hsl(ch_plugin.Color):
    """HSL object."""

    keys = ('hsl', 'hsla')
    incomplete_keys = ('hsl_open', 'hsla_open')

    def get_keys(self):
        return self.keys

    def get_regex(self):
        """Get regex."""
        return r'''
            \b(?P<hsl>hsl\(\s*(?P<hsl_content>
                %(float)s\s*,\s*%(percent)s\s*,\s*%(percent)s
            )\s*\)) |
            \b(?P<hsla>hsla\(\s*(?P<hsla_content>
                %(float)s\s*,\s*(?:%(percent)s\s*,\s*){2}(?:%(percent)s|%(float)s)
            )\s*\))
        ''' % COLOR_PARTS

    def get_incomplete_regex(self):
        """Get incomplete regex."""
        return r'''
            \b(?P<hsl_open>hsl\() |
            \b(?P<hsla_open>hsla\()
        '''

    def evaluate(self, m, **kwargs):
        color = None
        alpha = None
        alpha_dec = None

        if m.group('hsl'):
            content = [x.strip() for x in m.group('hsl_content').split(',')]
            rgba = ch_plugin.RGBA()
            hue = float(content[0])
            if hue < 0.0 or hue > 360.0:
                hue = hue % 360.0
            h = hue / 360.0
            s = ch_plugin.clamp(float(content[1].strip('%')), 0.0, 100.0) / 100.0
            l = ch_plugin.clamp(float(content[2].strip('%')), 0.0, 100.0) / 100.0
            rgba.fromhls(h, l, s)
            color = rgba.get_rgb()
        elif m.group('hsla'):
            content = [x.strip() for x in m.group('hsla_content').split(',')]
            rgba = ch_plugin.RGBA()
            hue = float(content[0])
            if hue < 0.0 or hue > 360.0:
                hue = hue % 360.0
            h = hue / 360.0
            s = ch_plugin.clamp(float(content[1].strip('%')), 0.0, 100.0) / 100.0
            l = ch_plugin.clamp(float(content[2].strip('%')), 0.0, 100.0) / 100.0
            rgba.fromhls(h, l, s)
            color = rgba.get_rgb()
            if content[3].endswith('%'):
                alpha, alpha_dec = ch_plugin.alpha_percent_normalize(content[3])
            else:
                alpha, alpha_dec = ch_plugin.alpha_dec_normalize(content[3])
        return color, alpha, alpha_dec

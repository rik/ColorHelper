"""HWB."""
from ColorHelper import ch_plugin

COLOR_PARTS = {
    "percent": r"[+\-]?(?:(?:\d*\.\d+)|\d+)%",
    "float": r"[+\-]?(?:(?:\d*\.\d+)|\d+)"
}


class Hwb(ch_plugin.Color):
    """HWB object."""

    keys = ('hwb', 'hwba')

    def get_keys(self):
        return self.keys

    def get_regex(self):
        """Get regex."""
        return r'''
            \b(?P<hwb>hwb\(\s*(?P<hwb_content>
                %(float)s\s*,\s*%(percent)s\s*,\s*%(percent)s
            )\s*\)) |
            \b(?P<hwba>hwb\(\s*(?P<hwba_content>
                %(float)s\s*,\s*(?:%(percent)s\s*,\s*){2}(?:%(percent)s|%(float)s)
            )\s*\)) |
        ''' % COLOR_PARTS

    def get_incomplete_regex(self):
        """Get incomplete regex."""
        return r'\b(?P<hwb_open>hwb\()'

    def evaluate(self, m, **kwargs):
        color = None
        alpha = None
        alpha_dec = None

        if m.group('hwb'):
            content = [x.strip() for x in m.group('hwb_content').split(',')]
            rgba = ch_plugin.RGBA()
            hue = float(content[0])
            if hue < 0.0 or hue > 360.0:
                hue = hue % 360.0
            h = hue / 360.0
            w = ch_plugin.clamp(float(content[1].strip('%')), 0.0, 100.0) / 100.0
            b = ch_plugin.clamp(float(content[2].strip('%')), 0.0, 100.0) / 100.0
            rgba.fromhwb(h, w, b)
            color = rgba.get_rgb()
        elif m.group('hwba'):
            content = [x.strip() for x in m.group('hwba_content').split(',')]
            rgba = ch_plugin.RGBA()
            hue = float(content[0])
            if hue < 0.0 or hue > 360.0:
                hue = hue % 360.0
            h = hue / 360.0
            w = ch_plugin.clamp(float(content[1].strip('%')), 0.0, 100.0) / 100.0
            b = ch_plugin.clamp(float(content[2].strip('%')), 0.0, 100.0) / 100.0
            rgba.fromhwb(h, w, b)
            color = rgba.get_rgb()
            if content[3].endswith('%'):
                alpha, alpha_dec = ch_plugin.alpha_percent_normalize(content[3])
            else:
                alpha, alpha_dec = ch_plugin.alpha_dec_normalize(content[3])
        return color, alpha, alpha_dec

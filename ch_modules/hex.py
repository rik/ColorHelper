"""Alpha Hex."""
import re
from ColorHelper import ch_plugin

HEX_COMPRESS_RE = re.compile(r'(?i)^#([0-9a-f])\1([0-9a-f])\2([0-9a-f])\3(?:([0-9a-f])\4)?$')


class Hex(ch_plugin.Color):
    """Hex object."""

    keys = ('hex', 'hexa')

    def get_keys(self):
        return self.keys

    def get_regex(self):
        """Get regex."""
        return r'''
            (?P<hexa>\#(?P<hexa_content>[\dA-Fa-f]{8}))\b |
            (?P<hex>\#(?P<hex_content>[\dA-Fa-f]{6}))\b |
            (?P<hexa_compressed>\#(?P<hexa_compressed_content>[\dA-Fa-f]{4}))\b |
            (?P<hex_compressed>\#(?P<hex_compressed_content>[\dA-Fa-f]{3}))\b
        '''

    def get_incomplete_regex(self):
        """Get incomplete regex."""
        return r'(?P<hash>\#)'

    def format(self, color, compress=False, **kwargs):
        """Compress hex."""

        if compress:
            m = HEX_COMPRESS_RE.match(color)
            if m:
                color = '#' + m.group(1) + m.group(2) + m.group(3)
                if m.group(4):
                    color += m.group(4)
        return color

    def evaluate(self, m, use_hex_argb=False, **kwargs):
        color = None
        alpha = None
        alpha_dec = None

        if m.group('hex_compressed'):
            content = m.group('hex_compressed_content')
            color = "#%02x%02x%02x" % (
                int(content[0:1] * 2, 16), int(content[1:2] * 2, 16), int(content[2:3] * 2, 16)
            )
        elif m.group('hexa_compressed') and use_hex_argb:
            content = m.group('hexa_compressed_content')
            color = "#%02x%02x%02x" % (
                int(content[1:2] * 2, 16), int(content[2:3] * 2, 16), int(content[3:] * 2, 16)
            )
            alpha = content[0:1]
            alpha_dec = ch_plugin.fmt_float(float(int(alpha, 16)) / 255.0, 3)
        elif m.group('hexa_compressed'):
            content = m.group('hexa_compressed_content')
            color = "#%02x%02x%02x" % (
                int(content[0:1] * 2, 16), int(content[1:2] * 2, 16), int(content[2:3] * 2, 16)
            )
            alpha = content[3:]
            alpha_dec = ch_plugin.fmt_float(float(int(alpha, 16)) / 255.0, 3)
        elif m.group('hex'):
            content = m.group('hex_content')
            if len(content) == 6:
                color = "#%02x%02x%02x" % (
                    int(content[0:2], 16), int(content[2:4], 16), int(content[4:6], 16)
                )
            else:
                color = "#%02x%02x%02x" % (
                    int(content[0:1] * 2, 16), int(content[1:2] * 2, 16), int(content[2:3] * 2, 16)
                )
        elif m.group('hexa') and use_hex_argb:
            content = m.group('hexa_content')
            if len(content) == 8:
                color = "#%02x%02x%02x" % (
                    int(content[2:4], 16), int(content[4:6], 16), int(content[6:], 16)
                )
                alpha = content[0:2]
                alpha_dec = ch_plugin.fmt_float(float(int(alpha, 16)) / 255.0, 3)
            else:
                color = "#%02x%02x%02x" % (
                    int(content[1:2] * 2, 16), int(content[2:3] * 2, 16), int(content[3:] * 2, 16)
                )
                alpha = content[0:1]
                alpha_dec = ch_plugin.fmt_float(float(int(alpha, 16)) / 255.0, 3)
        elif m.group('hexa'):
            content = m.group('hexa_content')
            if len(content) == 8:
                color = "#%02x%02x%02x" % (
                    int(content[0:2], 16), int(content[2:4], 16), int(content[4:6], 16)
                )
                alpha = content[6:]
                alpha_dec = ch_plugin.fmt_float(float(int(alpha, 16)) / 255.0, 3)
            else:
                color = "#%02x%02x%02x" % (
                    int(content[0:1] * 2, 16), int(content[1:2] * 2, 16), int(content[2:3] * 2, 16)
                )
                alpha = content[3:]
                alpha_dec = ch_plugin.fmt_float(float(int(alpha, 16)) / 255.0, 3)
        return color, alpha, alpha_dec

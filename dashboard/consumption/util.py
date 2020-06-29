# -*- coding: utf-8 -*-

class Util:
    @classmethod
    def remap(self, value, from1, to1, from2, to2):
        """Remap value with (a,b) -> (c, d)

        It is usually used for normalization.
        example:
            value = 250
            from1, to1 = (0, 1000)
            from2, to2 = (0, 1)
            -> 0.25
        """
        return from2 + (value - from1) * (to2 - from2) / (to1 - from1)
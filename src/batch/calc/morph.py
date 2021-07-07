
# 形態素解析用クラス
class Morph(object):
    def __init__(self, surface, pos, base):
        self.surface = surface
        self.pos = pos
        self.base = base

    def __repr__(self):
        return str({
            "surface": self.surface,
            "pos": self.pos,
            "base": self.base
        })

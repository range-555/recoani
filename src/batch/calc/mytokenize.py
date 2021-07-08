import MeCab

from src.batch.calc.normalize import Normalize
from src.batch.calc.morph import Morph


def mytokenize(sentence, title):
    mecab = MeCab.Tagger()
    if sentence is None:
        sentence = ""
    s = sentence + title * 4

    s = Normalize(s)
    sentence = s.normalize()
    mecab.parse("")
    lines = mecab.parse(sentence).split("\n")
    tokens = []
    for line in lines:
        elems = line.split("\t")
        if len(elems) < 2:
            continue
        surface = elems[0]
        if len(surface):
            feature = elems[1].split(",")
            base = surface if len(feature) < 7 or feature[6] == "*" else feature[6]
            pos = ",".join(feature[0:4])
            tokens.append(Morph(surface=surface, pos=pos, base=base))
    return tokens

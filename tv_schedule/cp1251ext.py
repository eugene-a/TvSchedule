import codecs
from encodings import charmap, cp1251

# replacement for non-cp1251 latin characters
S1 = "ƒ£´ºÀÁÂÃÄÅăÆÇÈÉÊËÌÍÎÏÑÒÓÔÕÖØŠŞŢÙÚÛÜÝŸŽàáâãäåæçèéêëìíîïñòóôõöøšùúûüýÿž"
S2 = "fL'°AAaAAAa'CEEEЁIIIЇNOOOOOOSstUUUUYYZaaaaaa'ceeeёiiiїnoooooosuuuuyyz"

# make cp1251 encoding map
dec_map = dict((i, ord(c)) for i, c in enumerate(cp1251.decoding_table))
enc_map = codecs.make_encoding_map(dec_map)
del dec_map

# supplement the map with substitution encodings of the missing characters
enc_map.update((ord(c1), enc_map[ord(c2)]) for c1, c2 in zip(S1, S2))


class IncrementalEncoder(charmap.IncrementalEncoder):
    def __init__(self, errors='strict'):
        charmap.IncrementalEncoder.__init__(self, errors, enc_map)


class StreamWriter(charmap.StreamWriter):
    def __init__(self, stream, errors='strict'):
        charmap.StreamWriter.__init__(self, stream, errors, enc_map)


def register():
    name = __name__[__name__.rindex('.') + 1:]

    codec_info = codecs.CodecInfo(
        charmap.Codec.encode, cp1251.Codec.decode,
        cp1251.StreamReader, StreamWriter,
        IncrementalEncoder, cp1251.IncrementalDecoder, name
    )
    codecs.register(lambda n: codec_info if n == name else None)

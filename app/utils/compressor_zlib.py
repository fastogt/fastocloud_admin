import zlib


class CompressorZlib:
    def __init__(self, gzip=False):
        zl = zlib.MAX_WBITS | 16 if gzip else zlib.MAX_WBITS
        c = zlib.compressobj(9, zlib.DEFLATED, zl)
        self.c_context = c.copy()

        d = zlib.decompressobj(zl)
        self.d_context = d.copy()
        self.is_gzlip = gzip

    def compress(self, data: bytes) -> bytes:
        c = self.c_context.copy()
        t = c.compress(data)
        t2 = c.flush(zlib.Z_FINISH)
        return t + t2

    def decompress(self, data: bytes) -> bytes:
        d = self.d_context.copy()
        t = d.decompress(data)
        while d.unconsumed_tail:
            t += d.decompress(d.unconsumed_tail)
        return t

    def name(self):
        return 'gzip' if self.is_gzlip else 'zlib'

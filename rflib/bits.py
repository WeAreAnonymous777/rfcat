import struct

def shiftString(string, bits):
    carry = 0
    news = []
    for x in xrange(len(string)-1):
        newc = ((ord(string[x]) << bits) + (ord(string[x+1]) >> (8-bits))) & 0xff
        news.append("%c"%newc)
    newc = (ord(string[-1])<<bits) & 0xff
    news.append("%c"%newc)
    return "".join(news)

def findDword(byts):
        possDwords = []
        # find the preamble (if any)
        bitoff = 0
        while True:
            sbyts = byts
            pidx = byts.find("\xaa\xaa")
            if pidx == -1:
                pidx = byts.find("\x55\x55")
                bitoff = 1
            if pidx == -1:
                return possDwords
            
            # chop off the nonsense before the preamble
            sbyts = byts[pidx:]
            #print "sbyts: %s" % repr(sbyts)
            
            # find the definite end of the preamble (ie. it may be sooner, but we know this is the end)
            while (sbyts[0] == ('\xaa', '\x55')[bitoff] and len(sbyts)>2):
                sbyts = sbyts[1:]
            
            #print "sbyts: %s" % repr(sbyts)
            # now we look at the next 16 bits to narrow the possibilities to 8
            # at this point we have no hints at bit-alignment
            dwbits, = struct.unpack(">H", sbyts[:2])
            if len(sbyts)>=3:
                bitcnt = 0
                #  bits1 =      aaaaaaaaaaaaaaaabbbbbbbbbbbbbbbb
                #  bits2 =                      bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
                bits1, = struct.unpack(">H", sbyts[:2])
                bits1 = bits1 | (ord(('\xaa','\x55')[bitoff]) << 16)
                bits1 = bits1 | (ord(('\xaa','\x55')[bitoff]) << 24)
                bits1 <<= 8
                bits1 |= (ord(sbyts[2]) )
                bits1 >>= bitoff            # now we should be aligned correctly
                #print "bits: %x" % (bits1)

                bit = (5 * 8) - 2  # bytes times bits/byte
                while (bits1 & (3<<bit) == (2<<bit)):
                    bit -= 2
                #print "bit = %d" % bit
                bits1 >>= (bit-14)
                #while (bits1 & 0x30000 != 0x20000): # now we align the end of the 101010 pattern with the beginning of the dword
                #    bits1 >>= 2
                #print "bits: %x" % (bits1)
                
                for frontbits in xrange(0, 16, 2):
                    poss = (bits1 >> frontbits) & 0xffff
                    if not poss in possDwords:
                        possDwords.append(poss)
            byts = byts[pidx+1:]
        
        return possDwords

def findDwordDoubled(byts):
        possDwords = []
        # find the preamble (if any)
        bitoff = 0
        pidx = byts.find("\xaa\xaa")
        if pidx == -1:
            pidx = byts.find("\55\x55")
            bitoff = 1
        if pidx == -1:
            return []

        # chop off the nonsense before the preamble
        byts = byts[pidx:]

        # find the definite end of the preamble (ie. it may be sooner, but we know this is the end)
        while (byts[0] == ('\xaa', '\x55')[bitoff] and len(byts)>2):
            byts = byts[1:]

        # now we look at the next 16 bits to narrow the possibilities to 8
        # at this point we have no hints at bit-alignment
        dwbits, = struct.unpack(">H", byts[:2])
        if len(byts)>=5:
            bitcnt = 0
            #  bits1 =      aaaaaaaaaaaaaaaabbbbbbbbbbbbbbbb
            #  bits2 =                      bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
            bits1, = struct.unpack(">H", byts[:2])
            bits1 = bits1 | (ord(('\xaa','\x55')[bitoff]) << 16)
            bits1 = bits1 | (ord(('\xaa','\x55')[bitoff]) << 24)
            bits1 <<= 8
            bits1 |= (ord(byts[2]) )
            bits1 >>= bitoff

            bits2, = struct.unpack(">L", byts[:4])
            bits2 <<= 8
            bits2 |= (ord(byts[4]) )
            bits2 >>= bitoff
            

            frontbits = 0
            for frontbits in xrange(16, 40, 2):    #FIXME: if this doesn't work, try 16, then 18+frontbits
                dwb1 = (bits1 >> (frontbits)) & 3
                dwb2 = (bits2 >> (frontbits)) & 3
                print "\tfrontbits: %d \t\t dwb1: %s dwb2: %s" % (frontbits, bin(bits1 >> (frontbits)), bin(bits2 >> (frontbits)))
                if dwb2 != dwb1:
                    break

            # frontbits now represents our unknowns...  let's go from the other side now
            for tailbits in xrange(16, -1, -2):
                dwb1 = (bits1 >> (tailbits)) & 3
                dwb2 = (bits2 >> (tailbits)) & 3
                print "\ttailbits: %d\t\t dwb1: %s dwb2: %s" % (tailbits, bin(bits1 >> (tailbits)), bin(bits2 >> (tailbits)))
                if dwb2 != dwb1:
                    tailbits += 2
                    break

            # now, if we have a double syncword, iinm, tailbits + frontbits >= 16
            print "frontbits: %d\t\t tailbits: %d, bits: %s " % (frontbits, tailbits, bin((bits2>>tailbits & 0xffffffff)))
            if (frontbits + tailbits >= 16):
                tbits = bits2 >> (tailbits&0xffff)
                tbits &= (0xffffffff)
                print "tbits: %x" % tbits

                poss = tbits&0xffffffff
                if poss not in possDwords:
                    possDwords.append(poss)
            else:
                pass
                # FIXME: what if we *don't* have a double-sync word?  then we stop at AAblah or 55blah and take the next word?

            possDwords.reverse()
        return possDwords

#def test():

def visBits(data):
    pass



def getBit(data, bit):
    idx = bit / 8
    bidx = bit % 8
    char = data[idx]
    return (ord(char)>>(7-bidx)) & 1



def detectRepeatPatterns(data, size=64):
    c1 = 0
    c2 = 0
    d1 = 0
    p1 = 0
    while p1 < (8*len(data)-size-8):
        d1 <<= 1
        d1 |= getBit(data, p1)
        d1 &= ((1<<(size)) - 1)

        if c1 < (size):
            p1 += 1
            c1 += 1
            continue

        d2 = 0
        p2 = p1+size
        while p2 < (8*len(data)):
            d2 <<= 1
            d2 |= getBit(data, p2)
            d2 &= ((1<<(size)) - 1)

            if c2 < (size):
                p2 += 1
                c2 += 1
                continue

            if d1 == d2:
                s1 = p1 - c1
                s2 = p2 - c2
                length = 0
                # complete the pattern until the numbers differ or meet
                while True:
                    p1 += 1
                    p2 += 1
                    b1 = getBit(data,p1)
                    b2 = getBit(data,p2)

                    if p1 == s2 or b1 != b2:
                        length = p1 - s1
                        c1 = 0
                        c2 = 0
                        p1 -= size
                        p2 -= size
                        break
                print "success:"
                print "  * bit idx1: %4d (%4d bits) - '%s'" % (s1, length, bin(d1))
                print "  * bit idx2: %4d (%4d bits) - '%s'" % (s2, length, bin(d2))
            #else:
            #    print "  * idx1: %d - '%s'  * idx2: %d - '%s'" % (p1, d1, p2, d2)
            p2 += 1
        p1 += 1


                    

                
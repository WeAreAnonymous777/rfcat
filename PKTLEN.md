# Introduction #

The length of the transmission or reception of a data packet is controlled by the single byte register PKTLEN, in conjunction with the 2-bit control field PKTCTRL0.LENGTH\_CONFIG.

PKTCTRL0.LENGTH\_CONFIG is described in the CC1111 documentation as having the following possible values:

  * 00 - Fixed packet length mode. Length configured in PKTLEN register.
  * 01 - Variable packet length mode. Packet length configured by first byte after SYNC word.
  * 10 - Reserved.
  * 11 - Reserved.

However, mode '10' is described in the [CC1110 documentation](http://www.ti.com/litv/pdf/slau259c) as a special 'Infinite' mode. In other words, while this mode is set, PKTLEN is not checked and transmission or reception will continue until manually stopped.


# Details #

When the radio is active, an internal single byte counter is incremented each time a byte is sent or received. When the internal counter matches the packet length, transmission or reception stops. The internal counter is reset to zero only when the radio first enters TX or RX mode, so packet length must be correctly set up before starting.

In practice, the only mode for which this needs any additional understanding of what's going on is 'Infinite' mode. This is because during transmission the internal counter will be overflowing every 256 bytes. i.e. it will get to 255, then, as a single byte register cannot hold a value greater than 255, it will reset to 0. In order to transmit or receive the correct number of bytes, the software must calculate how many bytes will be in the final block and pre-set PKTLEN so that when the radio is kicked out of Infinite mode the counter will match the next time it reaches that value (which may be 0).

Radio mode can be changed while the radio is active, allowing Infinite mode to be exited by simply setting PKTCTRL0.LENGTH\_CONFIG to '00' as soon as the final block is reached - i.e. once the number of bytes left to transmit is less than 256.

# Pseudocode #

This illustrates the internal working of the chip:

## Fixed Length ##

```
while INTERNAL COUNTER is not equal to PKTLEN
    send/receive next byte
    increment INTERNAL COUNTER
```

## Variable Length ##

```
set PKTLEN to value of first byte
skip first byte
while INTERNAL COUNTER is not equal to PKTLEN
    send/receive next byte
    increment INTERNAL COUNTER
```

## Infinite Mode ##

Software must perform:

```
set PKTLEN to mod(TOTAL LENGTH, 256)
while bytes are being processed
    if BYTES REMAINING are less than 256
        switch to FIXED LENGTH mode
```

the chip will perform:

```
while PKTCTRL0.LENGTH_CONFIG is equal to 10
    send/receive next byte
    increment INTERNAL COUNTER
while INTERNAL COUNTER is not equal to PKTLEN
    send/receive next byte
    increment INTERNAL COUNTER
```

thus, if Infinite mode is exited at the right moment by entering Fixed Length mode, packet transmission or reception will continue until the correct total number of bytes have been processed.
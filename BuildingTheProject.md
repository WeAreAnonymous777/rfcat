# Introduction #

This page will give information about how to build to software for your dongle, this page assumes a Linux based operating system is used.

# Details #

In order to build the software for the dongle the following two things are needed:

<ul>
<li>SDCC compiler</li>
<li>CC1111USB software</li>
</ul>

## SDCC compiler ##

The software is compiled using the SDCC (Small Device C Compiler). This compiler is open source and support the 8051 core that is included in the CC111x chips.

The version of this compiler that should definitely work is 2.9.0. This can be downloaded from [here](http://sourceforge.net/projects/sdcc/files/). Follow the included instructions to install the SDCC compiler.

## RfCat software ##

The RfCat software is the library provided on this site. Because a release isn't available yet the code has to be obtained from the repository.

The software can be checked out using the following command:
`hg clone https://code.google.com/p/rfcat/`

The project is split into two parts:  firmware and software.  The software is python code that interfaces to LIBUSB (dependency) to talk to the USB dongle.  The firmware must be built and flashed onto the USB dongle before RfCat will work properly

In order to build the firmware, one of the following commands can be issued (from within the firmware/ directory):
<ul>
<li>Chronos dongle <code>make RfCatChronos.hex</code></li>
<li>CC1111EMK <code>make RfCatDons.hex</code></li>
<li>IM-Me dongle <code>make immeSniff.hex</code></li>
</ul>

The resulting hex image is located in the `firmware/bins` folder and can be loaded into the dongle using a [CC Debugger](http://www.ti.com/tool/cc-debugger) or a [GoodFET](http://goodfet.sourceforge.net/).
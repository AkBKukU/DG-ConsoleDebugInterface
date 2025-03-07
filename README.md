# Data General microNOVA Console Debug Interface
The Data General microNOVA can be outfitted with an Async card with a Console Debug ROM that provides a memory monitor interface. This allows directly reading and writing to memory, executing instructions, and setting break points directly over a serial interface.

This would make it possible to fully interface with the computer and peripherals from a modern computer with just a USB serial adapter.


## The Project
The purpose of this software is to provide a software front-end to the Console Debug to control it from a modern computer. The primary goals are as follows:

- **Read Memory:** Be able to dump regions of memory directly over serial.
- **Load Software:** Write software directly into memory to run it.
- **Receive Data:** Software running on the computer could transfer data to a modern system.
- **Debug:** If sufficient development tools are created on a modern system it would be possible to use the Debug features when developing software. This may be possible to implement as a [Gdbserver](https://en.wikipedia.org/wiki/Gdbserver).


## microNOVA System Notes
- **Octal:** The microNOVA Console Debug interface uses an Octal syntax, that is values are represented from 0-7. I will be indicating these values with a prefix of `0o`. For example, the number `12` would be `0o15`.


## References
- **[microNOVA Programmers Reference](http://www.novasareforever.org/user/archive/public/docs/dg/hw/cpu/microNOVA/015-000050-00__microNOVA_Computer_Programmers_Reference__1976.002.pdf)**
- - **Page 45:** The operation of the console debug interface
- [microNOVA Technical Reference](http://www.novasareforever.org/user/archive/public/docs/dg/hw/cpu/microNOVA/014-000073-03__microNOVA_Computer_Systems_Technical_Reference__1977-Jan.pdf)
- - **Page 14:** The console debug ROM resides in address range 0o77400-0o77777


## Console Debug Commands

The console has two main states, "waiting" and "displaying a value". All commands are entered as a postfix after a value, if you are in the "waiting" state you will need to enter a value first. The Console Debug interface can also do addition and subtraction on any inputs used for values or addresses.

Only one breakpoint may be set at a time.

*"n" represents a value or address and capitalization of commands matters*

- `n A`: Reads internal CPU register
- `n /`: Reads the contents of a memory address and opens it for editing
- `n [Carriage Return]`: Enters `n` value into the last displayed value as an address, the goes back to waiting.
- `n [New Line]`: Enters `n` value into the last displayed value as an address, then displays value of next address.
- `n B`: Sets breakpoint at address
- `D`: Remove breakpoint
- `n R`: Begins execution starting at given address
- `P`: Resume execution if interrupted
- `n L`: Loads program from given device code and executes it
- `K`: Cancel current entry and returns to waiting










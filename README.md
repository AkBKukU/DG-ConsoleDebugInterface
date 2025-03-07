# Data General microNOVA Console Debug Interface
The Data General microNOVA can be outfitted with an Async card with a Console Debug ROM that provides a memory monitor interface. This allows directly reading and writing to memory, executing instructions, and setting break points directly over a serial interface.

This would make it possible to fully interface with the computer and peripherals from a modern computer with just a USB serial adapter.

## microNOVA System Notes
- **Octal:** The microNOVA Console Debug interface uses an Octal syntax, that is values are represented from 0-7. I will be indicating these values with a prefix of `0o`. For example, the number `12` would be `0o15`.

## References
- **[microNOVA Programmers Programmers](http://www.novasareforever.org/user/archive/public/docs/dg/hw/cpu/microNOVA/015-000050-00__microNOVA_Computer_Programmers_Reference__1976.002.pdf)**
- - **Page 45:** The operation of the console debug interface
- [microNOVA Technical Reference](http://www.novasareforever.org/user/archive/public/docs/dg/hw/cpu/microNOVA/014-000073-03__microNOVA_Computer_Systems_Technical_Reference__1977-Jan.pdf)  
- - **Page 14:** The console debug ROM resides in address range 0o77400-0o77777
# BGGP3
BGGP3 Writeup:

When I saw the prompt for BGGP suggesting a crash includes I immediately asked a few questions to work out the legality of crashing hardware. Basically this was to find out if I could build a Gameboy ROM that would "crash" i.e just get stuck in an infinite loop and never acepted input.

Great - on a technicality the "BIOS" of a gameboy is considered software. This does mean my score won't be amazing, since one of the highest scoring components is authoring and having a patch accepted. I don't think Nintendo are accepting updates to their 33 year old handheld.

Some options however for a crash easily present itself, the Gameboy's BIOS is 256 bytes (more in different versions) of code that perform 2 validation checks to ensure the cart/ROM is real. The first check is to ensure that the Nintendo logo is stored at 0x104-0x133. (This was an attempt at preventing illegal/unauthorised carts from being produced through legal means (as displaying the logo would infringe on Nintendo's copy right), but Sega tried this and lost the case against Accolade who produced cards on the Sega Genesis).

The second check is to validate the title and details/hardware of the ROM using the following checksum: (https://gbdev.io/pandocs/The_Cartridge_Header.html#the-cartridge-header)
```
x = 0
i = $0134
while i <= $014C
	x = x - [i] - 1
```
Because the point of BGGP is to make the smallest binary possible, while also causing a crash, we could simply create a single byte ROM, this would fail the Logo check and crash the gameboy, scoring a grand total of 4096-1 = 4095 points, not bad for a single byte.

But, we've got some bonus points up for grabs, and one of them is to hijack execution and print or return "3".
One way we can do this is to simply make the Nintendo Logo a 3. Since this is displayed before the check happens (the whole point of the check was to show the logo and therefor make the roms ilegally breaking copywrite) we can mark this off and score ourselves a nice extra set of points.

This logo is drawn differently from other sprites (8x8 sprites use a continous 2 bytes known as 2BPP https://www.huderlem.com/demos/gameboy2bpp.html), and uses a single byte per segment per 4x segment, a bit frustrating since it means we'll have to create a bunch of whitespace to get our 3 in the right location anyway. Since it's using a direct translation of binary to pixels drawn we can craft a 3 using the following sample:
```
XXXX = f
...X = 1
...X = 1
XXXX = f

...X = 1
...X = 1
XXXX = f
.... = 0
```
putting this together we get f1 1f (alignment space) 11 f0. Giving us a total rom size of 26 bytes which makes our score 4096-26+2048 = 6118 points. Discussions with the BGGP team suggest that since you can write this to any location on a physical ROM the points are scored from the first byte used to the last byte. In this case the header starts at the first byte even though the first control byte for a ROM is technically $100

![](/CrashonLogoLoad.PNG)

That gives us two our of 3 lots of bonus points, lets try for the third. Program counter with all 3s.
Initially I thought that this would be impossible, given setting the program counter to 3333 is a valid memory space on a gameboy, albiet way out of the control of a BGGP exercise. Speaking again to the BGGP organisers, as long as we hit 3333 in our memory sequence we're okay, also any variable of 3 is supposed to count. In this case we could jump into 3333 after our code but this is banking on an inconsistent memory setting to crash (we will largely nopsled forever and eventually hit undef memory.) The alternative is jumping to 0x03 or 0x33, in this case I chose 0x33 since it's tighter and the nopsled just mentioned lets us get back to the first instruction creating an infinte loop. The area before the header is "supposed" to be where you setup handlers for interupts and reset instructions. Crucially, this isn't checked and you can do whatever you like with it if you aren't really using them (we definitely aren't). A neat visual representation of this is the Sonic 3D "Secret Level Select" (https://www.youtube.com/watch?v=ZZs2HUW9tDA).

So now that we've got an idea of how to create our crash with a valid program header for scoring, we'll have to redraw the logo and properly this time, and then create a new drawn image so that we can still score our full points.

Luckily, some very handy resources exist for this https://daid.github.io/gameboy-assembly-by-example/ (specifically https://daid.github.io/rgbds-live/#https://raw.githubusercontent.com/daid/gameboy-assembly-by-example/master/graphics/initial-vram-graphics.asm). Now the code listed here is much longer than we need, caring about properly turning on and off the LCD screen before drawning, but since we don't care about anything like that, we can just draw our 3 and be done with it.

Culling all the lines so we just have an image copy loop gets us the following:

![](/ImageCopyLoop.PNG)

We could slot this in at 150 since that's the first section after the Nintendo header, OR since this is BGGP and we want all the points we can snag, the Gameboy colour BIOS only checks the top half of the nintendo logo, allowing us to completely butcher the lower half and jam our code in there.

Taking the reverse engineered CGB BIOS from (https://github.com/ISSOtm/gb-bootroms/blob/master/src/cgb.asm) we've got 24 bytes to work with.
```
LogoTopHalf:
    db $CE,$ED, $66,$66, $CC,$0D, $00,$0B, $03,$73, $00,$83, $00,$0C, $00,$0D, $00,$08, $11,$1F, $88,$89, $00,$0E
; The boot ROM only checks for the top half, but the full logo is present anyways
; for the two games that need it displayed
LogoBottomHalf:
    db $DC,$CC, $6E,$E6, $DD,$DD, $D9,$99, $BB,$BB, $67,$63, $6E,$0E, $EC,$CC, $DD,$DC, $99,$9F, $BB,$B9, $33,$3E
```

So in the bottom half of the logo we can set everything to:
```
21 2b 01 1e 10 06 80 2a 02 03 1d 20 fa c3 33 00
```
and still have 8 bytes left over.

Since we still have to have a 8 to draw we have to place that in memory, this time we'll use the 8 left over bytes, overlap the starting byte with the 00 from the previous piece of code and stick the rest into the checksum section of the cartridge header: 
```
00 02 00 05 00 01 00 02 00 01 00 05 00 02
```

Finally in order to get this code to execute, we have to have a valid checksum. Using the calculation from before we subtract 01, 05, 02 from e7 (0-(4c-34) bytes checked) That gives us df which we can slot in right after the final 00 02. This value will then be subtracted from the checksum, giving us 0 and letting us have no additional bytes but has the unfortunate side affect of underlining our 3 when drawn. I did try to only draw a select few bytes in multiple ways, but in order to cut down 2 extra bytes we have to do live with it to have a stable image, otherwise the loop is misaligned and it causes many headaches.

![](/ShearingMisalignment.PNG)

This lets us get all of our code and image slotted into less than a full cart header on a gameboy color bios, netting us 58 bytes total written to a cart starting from 0x100 for the following:
```
c3 1c 01 00 ce ed 66 66 cc 0d 00 0b 03 73 00 83
00 0c 00 0d 00 08 11 1f 88 89 00 0e 21 2b 01 1e
10 06 80 2a 02 03 1d 20 fa c3 33 00 02 00 05 00
01 00 02 00 01 00 05 00 02 df
```

And leaving a final score of 4096-58+1024+1024+2048 = 8134.

![](/FinalRom.PNG)

The explanation of the full entry is:

1. ```c3 1c 01 00 ```= c3 is jmp and takes a 16 byte header, 00 is spare space before the logo if more code wanted to be used.
2. ```ce ed 66 66 cc 0d 00 0b 03 73 00 83 00 0c 00 0d 00 08 11 1f 88 89 00 0e ```= Top half of Nintendo logo.
3. ```21 2b 01 ```= 21 opcode for LD HL,(value) in this case 0x012d, the starting location of our binary for the drawn 3 (litle endian)
4. ```1e 0e ```= 11 opcode for LD E,(value) in this case 0x1 for 16 bytes to copy (setting size of graphic) (I tried changing this to remove the line but because of the junk in register C not doing so will cause tearing and misalignment)
5. ```06 80 ```= 06 opcode for LD B,(value) in this case 0x80 is the memory mapping for VRAM, the location for drawing graphics to screen (This was LD BC before but by making this change and using a graphics size of 0x10 we can avoid tearing and handle the fact that C=0x13 on boot).
6. ```2a ```= LD A,(HL+) puts the value of HL's pointer into A and increments HL for the next byte
7. ```02 ```= LD (BC),A puts the value of A (our graphic byte) into the memory location of BC (VRAM)
8. ```03 ```= INC BC moves the VRAM pointer to the next location so we aren't drawing on a single pixel.
9. ```1d ```= DEC E counts down the number of bytes to copy
10. ```20 fa ```= JR NZ,a8 jumps to the relative signed location in memory if the Z flag is not set (from previous call) fa is -5 which puts us back to 6. to continue the loop
11. ```c3 33 00 ```= JMP to 0x0033 to score our extra points for pointer control. (to far for a relative jmp to hit 33 which would have saved an extra point)
12. ```00 02 00 05 00 01 00 02 00 01 00 05 00 02 ```= Hex representation of the graphic 3 (NB the first 00 overlaps with the previous code)
13. ```df ```= value to neutralize checksum and save extra space

![](/ASMCode.PNG)

References:
* https://gbdev.io/pandocs/
* https://daid.github.io/gameboy-assembly-by-example/
* https://github.com/ISSOtm/gb-bootroms
* https://rgbds.gbdev.io/ (Installed Arch BTW)
* https://www.pastraiser.com/cpu/gameboy/gameboy_opcodes.html
* http://bgb.bircd.org/ (Gameboy Debugger)
* https://visualboyadvancepc.com/
* https://www.hhdsoftware.com/free-hex-editor

#https://gbdev.io/pandocs/Tile_Data.html

drawgrid = b"00001111"
"""
			[1, 1, 1, 1, 1, 1, 1, 1]
			[0, 0, 0, 1, 1, 1, 1, 1]
			[1, 1, 1, 1, 1, 1, 1, 1]
			[1, 1, 1, 1, 1, 1, 1, 1]
			[0, 0, 0, 0, 0, 1, 1, 1]
			[1, 1, 1, 1, 1, 1, 1, 1]
			[1, 1, 1, 1, 1, 1, 1, 1]]"""
			
def possibleSubsets(N):
	for i in range(255):
		for j in range(255):
			if(i | j == N):
				print(hex(i) + " " + hex(j))
			
#possibleSubsets(drawgrid, len(drawgrid))


print("bars")
possibleSubsets(255)

print("mids")
possibleSubsets(7)

print("semi")
possibleSubsets(31)
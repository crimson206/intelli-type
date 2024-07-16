# core
convert -delay 100 -loop 0 image1.png image2.png image3.png image4.png image5.png output.gif

# ~5 times reduced
convert output.gif -resize 800x600 resized_output.gif




# nothing changed
convert output.gif -optimize -colors 256 optimized_output.gif

# nothing changed
gifsicle -O3 output.gif -o optimized_output.gif

# didnt work
convert output.gif -quality 85 optimized_output.gif

# didnt work
convert output.gif -fuzz 10% -layers Optimize optimized_output.gif

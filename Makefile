# Generate some examples

all: eins.avi zwei.avi drei.avi

eins.bml:
	./txt2blink.py -1 "Die upLUG ist die Potsdamer Linux User Group." > $@

zwei.bml:
	./txt2blink.py -2 "Wir haben uns zum Ziel gesetzt, die Verbreitung und das Verständnis von Freier Software, wie z.B. Linux, zu fördern." > $@

drei.bml:
	./txt2blink.py -3 "Wir unterstützen sowohl Anfänger als auch Profis bei ihren Fragen und Problemen, die auf der Mailingliste oder bei den regelmäßigen Treffen geklärt werden können." > $@

%.gif:%.bml
	b2gif $< > $@
	gimp -i -b '(let* ((filename "$@") (image (car (gimp-file-load RUN-NONINTERACTIVE filename filename))) (drawable (car (gimp-image-get-active-layer image)))) (gimp-image-scale image 206 320) (gimp-file-save RUN-NONINTERACTIVE image drawable filename filename) (gimp-image-delete image)) (gimp-quit 0)'

%.avi:%.gif
	mencoder -nosound -fps 20 -ovc lavc -lavcopts vcodec=mpeg4:mbd=1:v4mv:gray:vbitrate=50:vpass=1 $< -o $@
	mencoder -nosound -fps 20 -ovc lavc -lavcopts vcodec=mpeg4:mbd=1:v4mv:gray:vbitrate=50:vpass=2 $< -o $@

#!/bin/sh
# Script to syncronize an event listing on the Web to Blinkenlight movies in a
# local directory, using one movie per day.

# Either put these in the $PATH or insert the full path here:
GETEVENTS=getevents.py
TXT2BLINK=txt2blink.py
XMLSTARLET=xmlstarlet

if [ "$2" == "" ]; then
	echo "Usage: $0 source-URL target-directory"
	exit 1
fi

cd "$2"

# Fetch current event listing and make movies.
# Intention of the temporary files: At all points in time there should be only
# valid .bml files. Check if the contents have changed, because generating
# the movie costs CPU.
$GETEVENTS $1 | while read date; do
	read text
	if [ -e $date.bml ]; then
		lasttext=$($XMLSTARLET sel -t -v /blm/header/description $date.bml)
		if [ "$lasttext" == "$text" ]; then
			cp $date.bml $date.bml.tmp
		else
			$TXT2BLINK -2 "$text" > $date.bml.tmp
		fi
	else
		$TXT2BLINK -2 "$text" > $date.bml.tmp
	fi
done

shopt -s nullglob

# Remove obsolete events or overwrite with updates
for old in [0-9]*.bml; do
	if [ -e $old.tmp ]; then
		mv -f $old.tmp $old
	else
		rm $old
	fi
done

# Add new events
for new in *.bml.tmp; do
	mv -f $new $(basename $new .tmp)
done


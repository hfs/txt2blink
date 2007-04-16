#!/bin/sh
# Script to syncronize an event listing on the Web to Blinkenlight movies in a
# local directory, using one movie per day.

# Either put these in the $PATH or insert the full path here:
GETEVENTS=getevents.py
TXT2BLINK=txt2blink.py

if [ "$2" == "" ]; then
	echo "Usage: $0 source-URL target-directory"
	exit 1
fi

cd "$dir"

# Fetch current event listing and make movies.
# Intention of the temporary files: At all points in time there should be some
# valid .bml files
$GETEVENTS $1 | while read date; do
	read text
	$TXT2BLINK -2 "$text" > $date.bml.tmp
done

# Remove obsolete events or overwrite with updates
for old in *.bml; do
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


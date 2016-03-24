#!/bin/zsh

filelist=(./totest/*)

for file1 in $filelist; do
    filelist=(${filelist:#$file1})
    for file2 in $filelist; do
		for file in "$file1"/*; do [[ -f "$file" ]] && d1+=( "$(md5sum < "$file")" ); done
		for file in "$file2"/*; do [[ -f "$file" ]] && d2+=( "$(md5sum < "$file")" ); done 
		[[ "$(sort <<< "${d1[*]}")" == "$(sort <<< "${d2[*]}")" ]] && echo $file1 $file2 "Same" || echo  $file1 $file2 "Different"
    done
done



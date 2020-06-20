#!/bin/zsh
wav_dir=$1
output_dir=$2
song_num=$3
process_num=$4
size=$(echo "$song_num / $process_num" | bc)

echo "each process handle $size / $song_num songs" 
more=$(echo "($song_num % $process_num) > 0" | bc)
command=""

for ((i=0; i<$process_num + $more; i++))
do
    begin=$(echo "$size * $i + 1" | bc)

    end=$(echo "$size * ($i+1) + 1" | bc)
   
    command="${command}python3 vocal_separation.py $wav_dir $output_dir  $begin $end & "
    echo "python3 vocal_separation.py $wav_dir $output_dir  $begin $end &"
done

eval $command

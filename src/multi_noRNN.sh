#!/bin/zsh
wav_path=$1
vocal_path=$2
output_path=$3
song_num=$4
process_num=$5
size=$(echo "$song_num / $process_num" | bc)

echo "each process handle $size / $song_num songs" 
more=$(echo "($song_num % $process_num) > 0" | bc)
echo "$more"
command=""

for ((i=0; i<$process_num + $more; i++))
do
    begin=$(echo "$size * $i + 1" | bc)

    end=$(echo "$size * ($i+1) + 1" | bc)
   
    command="${command}python3 noRNN.py $wav_path $vocal_path $output_path  $begin $end & "
    echo "python3 noRNN.py $wav_path $vocal_path $output_path  $begin $end &"
done

eval $command

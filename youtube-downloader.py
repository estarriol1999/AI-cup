import os
import sys

if __name__ == '__main__':

    THE_FOLDER = sys.argv[1] 
    downloader = sys.argv[2]
    store_dir = sys.argv[3]
    print(f'{THE_FOLDER}')


    for song_dir in os.listdir(THE_FOLDER):
        if not os.path.isdir(os.path.join(THE_FOLDER, song_dir)):
            continue

        youtube_link_path = os.path.join(THE_FOLDER, song_dir, f'{song_dir}_link.txt')

        print ("---Youtube link path:", youtube_link_path)

        try:
            with open(youtube_link_path, 'r') as yt_link:
                link= yt_link.readline()
                print ("------Youtube link:", link)
                dest = os.path.join(store_dir, f'{song_dir}.tmp')
                audio_format = f'--audio-format wav'
                audio_quality = f'--audio-quality 2'
                download_quality = f'-f best'
                os.system(f'{downloader} -x {audio_format} {audio_quality} -o {dest} {link}')
        except:
            print ("------Error: YT link file not exist or can't be read")
        


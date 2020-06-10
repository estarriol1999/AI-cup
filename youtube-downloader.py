import os
import sys

if __name__ == '__main__':

    THE_FOLDER = sys.argv[1] 
    downloader = sys.argv[2]
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
                os.system(f'{downloader} -x --audio-format \'wav\' -o \'./wav/{song_dir}.wav\' \'{link}\'')
                print ("------ Download Success", link)
        except:
            print ("------Error: YT link file not exist or can't be read")
        


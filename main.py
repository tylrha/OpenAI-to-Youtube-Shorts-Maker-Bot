import concurrent.futures
import openai, os, random, time
from gtts import gTTS
import moviepy.editor as mp
from mutagen.mp3 import MP3
from pytube import Playlist, YouTube
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip

openai.api_key = "Your aPI Key"
videoHeight = 1920


audiopath = 'tts/'
videopath = 'finalvideo/'



def audioMaker(i, q):
    q = q.strip('\n')
    response = openai.Completion.create(
        model="text-davinci-002",
        prompt=q,
        temperature=0.7,
        max_tokens=500,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    print(q, 'done')
    tts = gTTS(text=response["choices"][0]["text"], tld='ca', slow=False)
    if os.path.exists(f"tts/{q.replace(' ', '_')}.mp3"):
        newfilename = '_' + q.replace(' ', '_') + '.mp3'
        tts.save(f"tmp/{newfilename.replace(' ', '_')}.mp3")
        os.replace(f"tmp/{newfilename.replace(' ', '_')}.mp3", f"tts/{newfilename.replace(' ', '_')}.mp3")
        print('iteration', i, q, 'saved')
    else:
        tts.save(f"tmp/{q.replace(' ', '_')}.mp3")
        os.replace(f"tmp/{q.replace(' ', '_')}.mp3", f"tts/{q.replace(' ', '_')}.mp3")
        print('iteration', i, q, 'saved')


def videoMaker():
    aflist = os.listdir(path='tts/')
    for i, fname in enumerate(aflist):
        retry = 0
        if fname.endswith('.mp3'):
            while True:
                randomVideo = random.choice(os.listdir('bgvideo/'))
                if randomVideo.endswith('.mp4'):
                    backgroundVideo = VideoFileClip('bgvideo/' + randomVideo).without_audio().resize(height=videoHeight).crop(x1=1166.6, y1=0, x2=2246.6, y2=1920)
                    audioFileDuration = MP3(audiopath + fname).info.length
                    if  audioFileDuration < 60:
                        audioDuration = audioFileDuration
                        audioClip = mp.CompositeAudioClip([AudioFileClip(audiopath + fname)])
                        print('video length is shorter than 60 secs', audioDuration)
                    else:
                        audioDuration = 60
                        audioClip = mp.CompositeAudioClip([AudioFileClip(audiopath + fname)]).subclip(0, 60)
                    videoDuration = backgroundVideo.duration
                    if videoDuration >= audioDuration:
                        randRange = random.randrange(30, int(videoDuration - audioDuration))
                        videoSubClip = backgroundVideo.subclip(randRange, randRange + audioDuration)
                        print('found a video longer than audio')

                        videoSubClip.audio = audioClip
                        videoSubClip.write_videofile('tmp/' + fname.replace('.mp3', '.mp4'), fps=30, audio_codec='aac',
                                                     audio_bitrate='192k', verbose=True, threads=os.cpu_count())
                        os.replace(audiopath + fname, 'usedaudio/' + fname)
                        os.replace('tmp/'+ fname.replace('.mp3', '.mp4'), videopath + fname.replace('.mp3', '.mp4'))
                        break
                    else:
                        retry += 1
                        print('video is shorter than your fucking dick, retrying : ', retry + 1)
                        if retry > 10:
                            print('Audio probably too long, skipping after 10 tries. Skipping audio', fname)
                            os.replace(audiopath + fname, 'audiotoolong/' + fname)
                            break


def backgroundVideoDownloader():
    opt = int(input('1. Playlist\n2.Video\n3. Download built in List of Videos Or any other key to return\n  Wachawannado? : '))
    if opt == 1:
        p = Playlist(input('What is the playlist link? : '))
        n = int(input('How many videos do you want to download?\n Hit 0 for all : '))
        for i, video in enumerate(p.videos):
            vidtitle = str(random.randint(100000, 1000000)) + '.mp4'
            print('Downloading', vidtitle)
            video.streams.filter(res="1080p").first().download(output_path='tmp/', filename=vidtitle, timeout=30,
                                                               max_retries=3, skip_existing=False)
            if os.path.exists('bgvideo/' + vidtitle):
                altvidtitle = str(random.randint(100000, 1000000)) + '.mp4'
                os.replace('tmp/' + vidtitle, 'bgvideo/' + altvidtitle)
            else:
                os.replace('tmp/' + vidtitle, 'bgvideo/' + vidtitle)
            print(i + 1, video.title, 'downloaded as', vidtitle)
            if i + 1 == n:
                break
    elif opt == 2:
        vidtitle = str(random.randint(100000, 1000000)) + '.mp4'
        p = YouTube(input('What is the video link? : '))
        p.streams.filter(res="1080p").first().download(output_path='tmp/', filename=vidtitle, skip_existing=False)
        if os.path.exists('bgvideo/' + vidtitle):
            altvidtitle = str(random.randint(100000, 1000000)) + '.mp4'
            os.replace('tmp/' + vidtitle, 'bgvideo/' + altvidtitle)
            print(p.title, 'downloaded as', altvidtitle)
        else:
            os.replace('tmp/' + vidtitle, 'bgvideo/' + vidtitle)
            print(p.title, 'downloaded as', vidtitle)
        print(p.title, 'downloaded')
    elif opt == 3:
        builtInListOfVideos = ["https://www.youtube.com/watch?v=vw5L4xCPy9Q", "https://www.youtube.com/watch?v=2X9QGY__0II", "https://www.youtube.com/watch?v=n_Dv4JMiwK8", "https://www.youtube.com/watch?v=qGa9kWREOnE"]
        for v in builtInListOfVideos:
            vidtitle = str(random.randint(100000, 1000000)) + '.mp4'
            YouTube(v).streams.filter(res="1080p").first().download(output_path='tmp/', filename=vidtitle, skip_existing=False)
            if os.path.exists('bgvideo/' + vidtitle):
                altvidtitle = str(random.randint(100000, 1000000)) + '.mp4'
                os.replace('tmp/' + vidtitle, 'bgvideo/' + altvidtitle)
                print(p.title, 'downloaded as', altvidtitle)
            else:
                os.replace('tmp/' + vidtitle, 'bgvideo/' + vidtitle)
                print(p.title, 'downloaded as', vidtitle)
            print(YouTube(v).title, 'downloaded')
    else:
        print('returning to main menu')
        return


if __name__ == '__main__':
    if not os.path.exists(audiopath):
        os.mkdir('tts')
    if not os.path.exists('audiotoolong/'):
        os.mkdir('audiotoolong')
    if not os.path.exists('bgvideo/'):
        os.mkdir('bgvideo')
    if not os.path.exists(videopath):
        os.mkdir('finalvideo')
    if not os.path.exists('tmp/'):
        os.mkdir('tmp')
    if not os.path.exists('usedaudio/'):
        os.mkdir('usedaudio')
    try:
        while True:
            wachawannado = int(input(
                '1. Make Audio from list in conditions.txt\n2. Input conditions manually to make audio\n3. Make videos from available audio\n4. Download new backgrounds\n5. Be the quitter that you are\nWachawannado? : '))
            if wachawannado == 1:
                if os.path.exists('q.txt'):
                    with open('q.txt', 'r') as q:
                        with concurrent.futures.ProcessPoolExecutor(max_workers=64) as executor:
                            for i, lines in enumerate(q):
                                executor.submit(audioMaker, i=i, q=lines)

                else:
                    print('wheres the fucking file? Create q.txt or hit 2 in the main menu')
            elif wachawannado == 2:
                audioMaker(q=input('Type a well worded clearly formatted question: '), i=1)
            elif wachawannado == 3:
                videoMaker()
            elif wachawannado == 4:
                backgroundVideoDownloader()
            elif wachawannado == 5:
                print('fuckin quitters')
                break
            else:
                print('\nWTF, try that again\n')

    except KeyboardInterrupt:
        tmpdir = os.listdir('tmp/')
        if not tmpdir:
            print('\ntmp folder is empty, now fuck off')
        else:
            for i, file in enumerate(tmpdir):
                os.remove('tmp/' + file)
            print(f'\n{i + 1} files cleared from the tmp folder. now fuck off')

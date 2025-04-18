from flask import Flask, render_template, request, send_file
import yt_dlp
import whisper
import moviepy.editor as mp
import openai
import os
import uuid

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['youtube_url']
        video_id = uuid.uuid4().hex
        filename = f"static/{video_id}.mp4"

        ydl_opts = {'outtmpl': filename}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        model = whisper.load_model("base")
        result = model.transcribe(filename)
        transcription = result["text"]

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Tu es un expert en contenu TikTok."},
                {"role": "user", "content": f"Résume cette vidéo en un script captivant de 60 secondes : {transcription}"}
            ]
        )
        summary = response["choices"][0]["message"]["content"]

        clip = mp.VideoFileClip(filename).subclip(0, 60)
        short_path = f"static/{video_id}_60s.mp4"
        clip.write_videofile(short_path)

        return render_template('index.html', summary=summary, video_url=short_path)

    return render_template('index.html')

import os
import srt
from google.cloud import speech

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="./autotrans.json"


# parameters about the audio file
sample_rate_hertz = 44100
language_code = "en-US"
audio_channel_count = 2
encoding = 'LINEAR16'
out_file = "subtitle"
max_chars = 40
storage_uri = 'gs://' + 'autotrans' + '/' +'ok.wav'

def long_running_recognize(uri):
    """
    Transcribe long audio file from Cloud Storage using asynchronous speech
    recognition

    Args:
      storage_uri URI for audio file in GCS, e.g. gs://[BUCKET]/[FILE]
    """

    # print("Transcribing {} ...".format(args.storage_uri))
    client = speech.SpeechClient()

    # Encoding of audio data sent.
    operation = client.long_running_recognize(
        config=
        {
            "enable_word_time_offsets": True,
            "enable_automatic_punctuation": True,
            "sample_rate_hertz": sample_rate_hertz,
            "language_code": language_code,
            "audio_channel_count": audio_channel_count,
            "encoding": encoding,
        },
        audio={"uri": storage_uri},
    )
    response = operation.result()

    subs = []

    for result in response.results:
        # First alternative is the most probable result
        # alternative = result.alternatives[0]
        # subs.append(alternative)
        # print(u"Transcript: {}".format(alternative.transcript))

        subs = break_sentences( subs, result.alternatives[0])

    print("Transcribing finished")
    return subs



def break_sentences(subs, alternative):
    firstword = True
    charcount = 0
    idx = len(subs) + 1
    content = ""

    for w in alternative.words:
        if firstword:
            # first word in sentence, record start time
            # start = w.start_time.ToTimedelta()
            start = w.start_time

        charcount += len(w.word)
        content += " " + w.word.strip()

        if ("." in w.word or "!" in w.word or "?" in w.word or
                charcount > max_chars or
                ("," in w.word and not firstword)):
            # break sentence at: . ! ? or line length exceeded
            # also break if , and not first word
            subs.append(srt.Subtitle(index=idx,
                                     start=start,
                                    #  end=w.end_time.ToTimedelta(),
                                     end=w.end_time,
                                     content=srt.make_legal_content(content)))
            firstword = True
            idx += 1
            content = ""
            charcount = 0
        else:
            firstword = False
    return subs


def write_srt(subs):
    srt_file = out_file + ".srt"
    print("Writing {} subtitles to: {}".format(language_code, srt_file))
    f = open(srt_file, 'w')
    f.writelines(srt.compose(subs))
    f.close()
    return


def write_txt(subs):
    txt_file = out_file + ".txt"
    print("Writing text to: {}".format(txt_file))
    f = open(txt_file, 'w')
    for s in subs:
        f.write(s.content.strip() + "\n")
    f.close()
    return


def autosub(uri):
    # url = "https://storage.cloud.google.com/sage_ff14/ok.wav"
    subs = long_running_recognize(uri)

    write_srt(subs)
    write_txt(subs)
    

if __name__ == "__main__":
    autosub(storage_uri)
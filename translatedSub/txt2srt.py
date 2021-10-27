import os
from google.cloud import translate
import srt

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="./autotrans.json"
project_id = "autotrans-330303"

en_srt =  'subtitle.srt'
csv_uri = 'index.csv'


def load_srt(filename):
    # load original .srt file
    # parse .srt file to list of subtitles
    print("Loading {}".format(filename))
    with open(filename) as f:
        text = f.read()
    return list(srt.parse(text))


def process_translations(subs, indexfile):
    # read index.csv and foreach translated file,

    print("Updating subtitles for each translated language")
    with open(indexfile) as f:
        lines = f.readlines()
    # copy orig subs list and replace content for each line
    for line in lines:
        index_list = line.split(",")
        lang = index_list[1]
        langfile = index_list[2].split("/")[-1]
        # langfile = '/'+langfile
        lang_subs = update_srt(lang, langfile, subs)
        write_srt(lang, lang_subs)
    return


def update_srt(lang, langfile, subs):
    # change subtitles' content to translated lines

    with open(langfile) as f:
        lines = f.readlines()
    i = 0
    for line in lines:
        subs[i].content = line
        i += 1
    return subs


def write_srt(lang, lang_subs):
    filename = lang + ".srt"
    f = open(filename, "w")
    f.write(srt.compose(lang_subs, strict=True))
    f.close()
    print("Wrote SRT file {}".format(filename))
    return


def main():
    subs = load_srt(en_srt)
    process_translations(subs, csv_uri)


if __name__ == "__main__":
    main()



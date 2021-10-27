import os
from google.cloud import translate
import srt

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="./autotrans.json"
project_id = "autotrans-330303"


en_uri = 'gs://' + 'autotrans' + '/' +'subtitle.txt'
jp_uri = 'gs://' + 'autotrans' + '/' +'translated/' 
location = "us-central1"
source_lang =  "en-US"
target_lang = "ja"


def batch_translate_text(input_uri, output_uri, project_id, location, source_lang, target_lang):
    from time import sleep
    # call batch translate against orig.txt

    client = translate.TranslationServiceClient()

    target_language_codes = target_lang.split(",")
    gcs_source = {"input_uri": input_uri}
    mime_type = "text/plain"
    input_configs_element = {"gcs_source": gcs_source, "mime_type": mime_type}
    input_configs = [input_configs_element]
    gcs_destination = {"output_uri_prefix": output_uri}
    output_config = {"gcs_destination": gcs_destination}
    parent = f"projects/{project_id}/locations/{location}"

    operation = client.batch_translate_text(
        request={
            "parent": parent,
            "source_language_code": source_lang,
            "target_language_codes": target_language_codes,
            "input_configs": input_configs,
            "output_config": output_config,
        })

    # Initial delay
    total_wait_secs = 90
    print(f"Waiting for operation to complete... {total_wait_secs:.0f} secs")

    delay_secs = 10
    sleep(90)
    while not operation.done():
        # Exponential backoff
        delay_secs *= 1.1
        total_wait_secs += delay_secs
        print(f"Checking again in: {delay_secs:.0f} seconds | total wait: {total_wait_secs:.0f} secs")
        sleep(delay_secs)

    response = operation.result()
    print(u"Total Characters: {}".format(response.total_characters))
    print(u"Translated Characters: {}".format(response.translated_characters))


def main():
    batch_translate_text(en_uri, jp_uri, project_id, location, source_lang, target_lang)

if __name__ == "__main__":
    main()



from gtts import gTTS
from prompt_toolkit.shortcuts import ProgressBar

def from_text(text, lang='en', slow=False):
    return gTTS(text=text, lang=lang, slow=slow)

def from_comment(topic, conversation=False):
    pass

def list2mp3(text_list, lang='en', slow=False, out="out.mp3"):
    with open(out, 'wb') as mp3:
        with ProgressBar() as pb:
            for i in pb(range(len(text_list))):
                tts = from_text(text=text_list[i], lang=lang, slow=slow)
                tts.write_to_fp(mp3)

if __name__ == "__main__":
    l = ["murillo", "bruna","vida","miguel"]
    list2mp3(l, lang="pt-BR", out="/tmp/teste_lista.mp3")

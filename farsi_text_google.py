from googletrans import Translator
translator = Translator()


def translate(text:str):
    hihi=translator.translate(text)
    return str(hihi.text)

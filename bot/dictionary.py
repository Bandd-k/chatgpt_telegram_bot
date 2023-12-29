import requests

def get_word_definition(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    response = requests.get(url)
    if response.status_code == 200:
        word_data = response.json()
        if isinstance(word_data, list) and len(word_data) > 0:
            entry = word_data[0]
            word_info = f"Word: {entry.get('word')}\n"
            phonetics = entry.get('phonetics', [])
            if phonetics:
                phonetic_text = phonetics[0].get('text', '')
                audio = phonetics[0].get('audio', '')
                word_info += f"Phonetic: {phonetic_text}\n"
                if audio:
                    word_info += f"Audio: {audio}\n"

            meanings = entry.get('meanings', [])
            if meanings:
                for meaning in meanings:
                    part_of_speech = meaning.get('partOfSpeech', '')
                    word_info += f"\nPart of Speech: {part_of_speech.title()}\n"
                    definitions = meaning.get('definitions', [])
                    for definition in definitions:
                        word_info += f"- Definition: {definition.get('definition', '')}\n"
                        example = definition.get('example', '')
                        if example:
                            word_info += f"  Example: {example}\n"
                    synonyms = meaning.get('synonyms', [])
                    if synonyms:
                        word_info += f"  Synonyms: {', '.join(synonyms)}\n"
                    antonyms = meaning.get('antonyms', [])
                    if antonyms:
                        word_info += f"  Antonyms: {', '.join(antonyms)}\n"

            return word_info
        else:
            return "Word not found."
    else:
        return "Failed to retrieve the definition."
    
def get_word_definition_html(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    response = requests.get(url)
    if response.status_code == 200:
        word_data = response.json()
        if isinstance(word_data, list) and len(word_data) > 0:
            entry = word_data[0]
            html_output = f"<b>{entry.get('word')}</b>\n"
            
            phonetics = entry.get('phonetics', [])
            if phonetics:
                phonetic_text = phonetics[0].get('text', '')
                audio = phonetics[0].get('audio', '')
                html_output += f"Phonetic: <code>{phonetic_text}</code>\n"
                if audio:
                    html_output += f"<a href=\"{audio}\">Listen to pronunciation</a>\n"

            meanings = entry.get('meanings', [])
            if meanings:
                for meaning in meanings:
                    part_of_speech = meaning.get('partOfSpeech', '')
                    html_output += f"\n<i>{part_of_speech.title()}</i>\n"
                    definitions = meaning.get('definitions', [])
                    for definition in definitions:
                        html_output += f"• Definition: {definition.get('definition', '')}\n"
                        example = definition.get('example', '')
                        if example:
                            html_output += f"  Example: <i>{example}</i>\n"
                    synonyms = meaning.get('synonyms', [])
                    if synonyms:
                        html_output += f"  Synonyms: <i>{', '.join(synonyms)}</i>\n"
                    antonyms = meaning.get('antonyms', [])
                    if antonyms:
                        html_output += f"  Antonyms: <i>{', '.join(antonyms)}</i>\n"

            source_urls = entry.get('sourceUrls', [])
            if source_urls:
                html_output += "\nSources:\n"
                for url in source_urls:
                    html_output += f"<a href=\"{url}\">{url}</a>\n"

            return html_output
        else:
            return "<p>Word not found.</p>"
    else:
        return "<p>Failed to retrieve the definition.</p>"

    
def get_word_definition_markdown(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    response = requests.get(url)
    if response.status_code == 200:
        word_data = response.json()
        if isinstance(word_data, list) and len(word_data) > 0:
            entry = word_data[0]
            markdown_output = f"*{entry.get('word')}*\n"
            
            phonetics = entry.get('phonetics', [])
            if phonetics:
                phonetic_text = phonetics[0].get('text', '')
                audio = phonetics[0].get('audio', '')
                markdown_output += f"Phonetic: `{phonetic_text}`\n"
                if audio:
                    markdown_output += f"[Listen to pronunciation]({audio})\n"

            meanings = entry.get('meanings', [])
            if meanings:
                for meaning in meanings:
                    part_of_speech = meaning.get('partOfSpeech', '')
                    markdown_output += f"\n_{part_of_speech.title()}_\n"
                    definitions = meaning.get('definitions', [])
                    for definition in definitions:
                        markdown_output += f"• Definition: {definition.get('definition', '')}\n"
                        example = definition.get('example', '')
                        if example:
                            markdown_output += f"  Example: _{example}_\n"
                    synonyms = meaning.get('synonyms', [])
                    if synonyms:
                        markdown_output += f"  Synonyms: _{', '.join(synonyms)}_\n"
                    antonyms = meaning.get('antonyms', [])
                    if antonyms:
                        markdown_output += f"  Antonyms: _{', '.join(antonyms)}_\n"

            source_urls = entry.get('sourceUrls', [])
            if source_urls:
                markdown_output += "\nSources:\n" + "\n".join(f"[{url}]({url})" for url in source_urls) + "\n"

            return markdown_output
        else:
            return "Word not found."
    else:
        return "Failed to retrieve the definition."




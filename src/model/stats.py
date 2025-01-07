# This file is part of Foobar.

# Foobar is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <https://www.gnu.org/licenses/>.


class Stats:
    def __init__(self):
        self.stop_words = self._step_words()

    def _step_words(self):
        return [
            '', '"', '“', '”', 'a', 'ante', 'bajo', 'cabe', 'e', 'cada', 'sea',
            'con', 'contra', 'de', 'desde', 'durante', 'en', 'estos', 'ya',
            'entre', 'hacia', 'hasta', 'mediante', 'para', 'por', '%',
            'según', 'sin', 'so', 'sobre', 'tras', 'versus', 'vía', 'parece',
            'el', 'un', 'la', 'una', 'lo', 'los', 'unos', 'las', 'son',
            'unas', 'pero', 'tambien', 'y', 'te', 'que', 'del', 'al',
            'se', 'le', 'les', 'es', 'sus', 'del', 'no', 'este', 'nunca',
            'mas', 'porque', 'cuando', 'ese', 'este', 'su', 'esos', 'fue',
            'como', 'tiene', 'muy', 'o', 'más', '|', 'me', 'mi', 'eso',
            'mucho', 'ha', 'esta', '$', 'nos', 'ser', 'tu', 'vos', 'si',
            'sino', 'también', 'puede', '+', '-', 'hay', 'está', 'estas',
            'estaba', 'era', 'esa', 'ella', 'tipo', 'mis', 'todo', 'donde'
        ]

    def _sentences_count(self, news_content):
        sentences = news_content.split('.')
        return len(sentences)

    def _paragraphs_count(self, news_content):
        paragraphs = news_content.split('\n')
        paragraphs = [ p for p in paragraphs if len(p)>0 and p != ' ']
        return len(paragraphs)

    def _word_freq(self, news_content):
        """Compute word Frequency of new."""
        word_freq = {}
        words = news_content.split(' ')
        word_count = len(words)

        for word in words:
            word = word.lower().strip().strip(',.\n\r')
            if word in self.stop_words:
                continue

            if word not in word_freq.keys():
                word_freq[word] = 1
            else:
                word_freq[word] += 1

        word_freq = {
            k: v for k, v in sorted(
                word_freq.items(),
                key=lambda item: item[1]
            )
        }
        return word_count, word_freq

    def run(self, noticia):
        wc, wf = self._word_freq(noticia['body'])
        sentences = self._sentences_count(noticia['body'])
        paragraphs = self._paragraphs_count(noticia['body'])
        noticia['word_count'] = wc
        noticia['word_freq'] = wf
        noticia['sentences'] = sentences
        noticia['paragraphs'] = paragraphs

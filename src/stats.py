class Stats:
    def __init__(self):
        self.stop_words = self._step_words()

    def _step_words(self):
        return [
            '', 'a', 'ante', 'bajo', 'cabe', 'e', 'cada', 'sea',
            'con', 'contra', 'de', 'desde', 'durante', 'en', 'estos'
            'entre', 'hacia', 'hasta', 'mediante', 'para', 'por',
            'según', 'sin', 'so', 'sobre', 'tras', 'versus', 'vía',
            'el', 'un', 'la', 'una', 'lo', 'los', 'unos', 'las', 'son'
            'unas', 'pero', 'tambien', 'y', 'te', 'que', 'del', 'al',
            'se', 'le', 'les', 'es', 'sus', 'del', 'no', 'este', 'nunca',
            'mas', 'porque', 'cuando', 'ese', 'este', 'su', 'esos', 'fue',
            'como', 'tiene', 'muy', 'o', 'más', '|', 'me', 'mi', 'eso',
            'mucho', 'ha', 'esta', '$', 'nos', 'ser', 'tu', 'vos', 'si', 'sino'
        ]

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
        noticia['word_count'] = wc
        noticia['word_freq'] = wf

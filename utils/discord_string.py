class DiscordString:
    _txt: str

    def __init__(self, init=None):
        self._txt = '' if init is None else init

    def __repr__(self):
        return f'<DiscordString>'

    def __str__(self):
        return self._txt

    def __add__(self, other: 'DiscordString'):
        joined = DiscordString(str(self) + str(other))
        return joined

    def __radd__(self, other: 'DiscordString'):
        joined = DiscordString(str(other) + str(self))
        return joined

    def clear(self) -> 'DiscordString':
        self._txt = ''
        return self

    def add(self, msg) -> 'DiscordString':
        if not isinstance(msg, str):
            msg = str(msg)
        self._txt += msg
        return self

    def pre(self, msg) -> 'DiscordString':
        toggle = self.toggle_pre_block if '\n' in msg or '\r' in msg else self.toggle_pre_line

        toggle()
        self.add(msg)
        toggle()

        return self

    def code(self, msg, language) -> 'DiscordString':
        self.toggle_pre_block(language)
        self.add(msg)
        self.toggle_pre_block()

        return self

    def toggle_pre_line(self) -> 'DiscordString':
        self._txt += '`'
        return self

    def toggle_pre_block(self, language=None) -> 'DiscordString':
        self._txt += '```'
        if language:
            if not isinstance(language, str):
                language = str(language)
            self._txt += language
        return self

    def bold(self, msg) -> 'DiscordString':
        self.toggle_bold()
        self.add(msg)
        self.toggle_bold()
        return self

    def toggle_bold(self) -> 'DiscordString':
        self._txt += '**'
        return self

    def italic(self, msg) -> 'DiscordString':
        self.toggle_italic()
        self.add(msg)
        self.toggle_italic()
        return self

    def toggle_italic(self) -> 'DiscordString':
        self._txt += '_'
        return self

    def emoji(self, msg) -> 'DiscordString':
        if not isinstance(msg, str):
            msg = str(msg)
        self._txt += f':{msg}:'
        return self

    def newline(self) -> 'DiscordString':
        self._txt += '\n'
        return self

    def nl(self) -> 'DiscordString':
        return self.newline()

    def spoiler(self, msg) -> 'DiscordString':
        self.toggle_spoiler()
        self.add(msg)
        self.toggle_spoiler()

        return self

    def toggle_spoiler(self) -> 'DiscordString':
        self._txt += '||'
        return self

    def strikethrough(self, msg) -> 'DiscordString':
        self.toggle_strikethrough()
        self.add(msg)
        self.toggle_strikethrough()

        return self

    def toggle_strikethrough(self) -> 'DiscordString':
        self._txt += '~~'
        return self

    def join(self, sep: str, itr, key=None):
        if key is None:
            def str_key(e):
                return str(e)
        else:
            def str_key(e):
                return str(key(e))

        list_str = sep.join(map(str_key, itr))

        self.add(list_str)

        return self

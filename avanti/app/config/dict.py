class Dict(dict):
    """ Умеет возвращать значения по ключам "в глубину" - с точками.
    Например:
        d = Dict({'a': {'b': 1}})
        assert d['a.b'] == 1
    """

    def __getitem__(self, key):
        if '.' in key:
            _, _, value = self._walk_to(key)
            return value
        return super().__getitem__(key)

    def __setitem__(self, key: str, value):
        if '.' in key:
            container, ikey, ival = self._walk_to(key, add_default=True)
            if container is None:
                raise KeyError(f'invalid key {key}')
            container[ikey] = value
        else:
            super().__setitem__(key, value)

    def _walk_to(self, key: str, *, add_default: bool = False):
        """Walk the dict to the key. If add_default is True empty dict values
        will be set for the missed keys on the way."""
        keys = key.split('.')
        container = self
        for key in keys[:-1]:
            default = dict() if add_default else None
            next_container = container.get(key, default)
            if default is not None:
                container[key] = next_container
            if next_container is None:
                return None, None, None
            container = next_container
        ikey = keys[-1]
        ival = container.get(keys[-1])
        return container, ikey, ival

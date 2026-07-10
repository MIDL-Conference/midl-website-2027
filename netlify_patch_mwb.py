# netlify_patch_mwb.py
# 让 mwb 在 Netlify 上不要开 multiprocessing.Pool（避免 SemLock 报错）
import multiprocessing.pool as mpp

class DummyResult:
    def __init__(self, value):
        self._value = value
    def get(self, timeout=None):
        return self._value

class DummyPool:
    def __enter__(self): return self
    def __exit__(self, *a): return False

    def map(self, func, it):
        return list(map(func, it))

    def starmap(self, func, iterable):
        return [func(*args) for args in iterable]

    def imap_unordered(self, func, it):
        # 保持接口，顺序其实无所谓
        return iter(map(func, it))

    def apply(self, func, args=(), kwds=None):
        if kwds is None: kwds = {}
        return func(*args, **kwds)

    def apply_async(self, func, args=(), kwds=None, callback=None, error_callback=None):
        try:
            val = self.apply(func, args, kwds)
            if callback:
                callback(val)
            return DummyResult(val)
        except Exception as e:
            if error_callback:
                error_callback(e)
            raise

    def close(self): pass
    def join(self): pass
    def terminate(self): pass

# 把 Pool 替换成单进程版本
mpp.Pool = lambda *a, **k: DummyPool()

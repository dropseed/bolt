# Cache

A simple cache using the database.

The Plain Cache stores JSON-serializable values in a `CachedItem` model.
Cached data can be set to expire after a certain amount of time.

Access to the cache is provided through the `Cached` class.

```python
from bolt.cache import Cached


cached = Cached("my-cache-key")

if cached.exists():
    print("Cache hit and not expired!")
    print(cached.value)
else:
    print("Cache miss!")
    cached.set("a JSON-serializable value", expiration=60)

# Delete the item if you need to
cached.delete()
```

Expired cache items can be cleared with `bolt cache clear-expired`.
You can run this on a schedule through various cron-like tools or [bolt-worker](../../../bolt-worker/bolt/worker/).

## Installation

Add `bolt.cache` to your `INSTALLED_PACKAGES`:

```python
# app/settings.py
INSTALLED_PACKAGES = [
    # ...
    "bolt.cache",
]
```

## CLI

- `bolt cache clear-expired` - Clear all expired cache items
- `bolt cache clear-all` - Clear all cache items
- `bolt cache stats` - Show cache statistics

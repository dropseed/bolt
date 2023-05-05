# bolt-requestlog

The request log stores a local history of HTTP requests and responses during `bolt work` (Django runserver).

The request history will make it easy to see redirects,
400 and 500 level errors,
form submissions,
API calls,
webhooks,
and more.

[Watch on YouTube](https://www.youtube.com/watch?v=AwI7Pt5oZnM)

Requests can be re-submitted by clicking the "replay" button.

[![Django request log](https://user-images.githubusercontent.com/649496/213781414-417ad043-de67-4836-9ef1-2b91404336c3.png)](https://user-images.githubusercontent.com/649496/213781414-417ad043-de67-4836-9ef1-2b91404336c3.png)

## Installation

```python
# settings.py
INSTALLED_APPS += [
    "boltrequestlog",
]

MIDDLEWARE = MIDDLEWARE + [
    # ...
    "boltrequestlog.RequestLogMiddleware",
]
```

The default settings can be customized if needed:

```python
# settings.py
REQUESTLOG_IGNORE_URL_PATHS = [
    "/sw.js",
    "/favicon.ico",
    "/admin/jsi18n/",
]
REQUESTLOG_KEEP_LATEST = 50
REQUESTLOG_URL = "/requestlog/"
```

## Tailwind CSS

This package is styled with [Tailwind CSS](https://tailwindcss.com/),
and pairs well with [`bolt-tailwind`](https://github.com/boltpackages/bolt-tailwind).

If you are using your own Tailwind implementation,
you can modify the "content" in your Tailwind config to include any bolt packages:

```js
// tailwind.config.js
module.exports = {
  content: [
    // ...
    ".venv/lib/python*/site-packages/bolt*/**/*.{html,js}",
  ],
  // ...
}
```

If you aren't using Tailwind, and don't intend to, open an issue to discuss other options.

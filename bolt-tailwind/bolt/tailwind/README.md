# bolt-tailwind

Integrate Tailwind CSS without JavaScript or npm.

Use [Tailwind CSS](https://tailwindcss.com/) with [Django](https://www.djangoproject.com/) *without* requiring JavaScript or npm.

Made possible by the [Tailwind standalone CLI](https://tailwindcss.com/blog/standalone-cli).

```console
$ bolt tailwind
Usage: bolt tailwind [OPTIONS] COMMAND [ARGS]...

  Tailwind CSS

Options:
  --help  Show this message and exit.

Commands:
  compile  Compile a Tailwind CSS file
  init     Install Tailwind, create a tailwind.config.js...
  update   Update the Tailwind CSS version
```

## Installation

First, install `bolt-tailwind` from [PyPI](https://pypi.org/project/bolt-tailwind/):

```sh
pip install bolt-tailwind
```

Create a new `tailwind.config.js` file in your project root:

```sh
bolt tailwind init
```

This will also create a `tailwind.css` file at `static/src/tailwind.css` where additional CSS can be added.
You can customize where these files are located if you need to,
but this is the default (requires `STATICFILES_DIR = BASE_DIR / "static"`).

The `src/tailwind.css` file is then compiled into `dist/tailwind.css` by running `tailwind compile`:

```sh
bolt tailwind compile
```

When you're working locally, add `--watch` to automatically compile as changes are made:

```sh
bolt tailwind compile --watch
```

Then include the compiled CSS in your base template `<head>`:

```html
{% tailwind_css %}
```

In your repo you will notice a new `.bolt` directory that contains `tailwind` (the standalone CLI binary) and `tailwind.version` (to track the version currently installed).
You should add `.bolt` to your `.gitignore` file.

## Updating Tailwind

This package manages the Tailwind versioning by comparing `.bolt/tailwind.version` to the `FORGE_TAILWIND_VERSION` variable that is injected into your `tailwind.config.js` file.

```js
const FORGE_TAILWIND_VERSION = "3.0.24"

module.exports = {
  theme: {
    extend: {},
  },
  plugins: [
    require("@tailwindcss/forms"),
  ],
}
```

When you run `tailwind compile`,
it will automatically check whether your local installation needs to be updated and will update it if necessary.

You can use the `update` command to update your project to the latest version of Tailwind:

```sh
tailwind update
```

## Adding custom CSS

If you need to actually write some CSS,
it should be done in `app/static/src/tailwind.css`.

```css
@tailwind base;


@tailwind components;

/* Add your own "components" here */
.btn {
    @apply bg-blue-500 hover:bg-blue-700 text-white;
}

@tailwind utilities;

/* Add your own "utilities" here */
.bg-pattern-stars {
    background-image: url("/static/images/stars.png");
}

```

[Read the Tailwind docs for more about using custom styles →](https://tailwindcss.com/docs/adding-custom-styles)

## Deployment

If possible, you should add `static/dist/tailwind.css` to your `.gitignore` and run the `bolt tailwind compile --minify` command as a part of your deployment pipeline.

When you run `bolt tailwind compile`, it will automatically check whether the Tailwind standalone CLI has been installed, and install it if it isn't.

When using Bolt on Heroku, we do this for you automatically in our [Bolt buildpack](https://github.com/boltpackages/heroku-buildpack-bolt/blob/master/bin/files/post_compile).

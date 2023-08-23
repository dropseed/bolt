import datetime
from itertools import islice

from jinja2.utils import htmlsafe_json_dumps

from bolt.utils.html import format_html
from bolt.utils.timesince import timesince, timeuntil
from bolt.utils.timezone import localtime


def json_script(value, id):
    return format_html(
        '<script type="application/json" id="{}">{}</script>',
        id,
        htmlsafe_json_dumps(value),
    )


default_filters = {
    # The standard Python ones
    "strftime": datetime.datetime.strftime,
    "strptime": datetime.datetime.strptime,
    # To convert to user time zone
    "localtime": localtime,
    "timeuntil": timeuntil,
    "timesince": timesince,
    "json_script": json_script,
    "islice": islice,  # slice for dict.items()
}

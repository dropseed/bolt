"""Database functions that do comparisons or type conversions."""
from django.db import NotSupportedError
from django.db.models.expressions import Func, Value
from django.db.models.fields import TextField
from django.db.models.fields.json import JSONField
from bolt.utils.regex_helper import _lazy_re_compile


class Cast(Func):
    """Coerce an expression to a new field type."""

    function = "CAST"
    template = "%(function)s(%(expressions)s AS %(db_type)s)"

    def __init__(self, expression, output_field):
        super().__init__(expression, output_field=output_field)

    def as_sql(self, compiler, connection, **extra_context):
        extra_context["db_type"] = self.output_field.cast_db_type(connection)
        return super().as_sql(compiler, connection, **extra_context)

    def as_sqlite(self, compiler, connection, **extra_context):
        db_type = self.output_field.db_type(connection)
        if db_type in {"datetime", "time"}:
            # Use strftime as datetime/time don't keep fractional seconds.
            template = "strftime(%%s, %(expressions)s)"
            sql, params = super().as_sql(
                compiler, connection, template=template, **extra_context
            )
            format_string = "%H:%M:%f" if db_type == "time" else "%Y-%m-%d %H:%M:%f"
            params.insert(0, format_string)
            return sql, params
        elif db_type == "date":
            template = "date(%(expressions)s)"
            return super().as_sql(
                compiler, connection, template=template, **extra_context
            )
        return self.as_sql(compiler, connection, **extra_context)

    def as_mysql(self, compiler, connection, **extra_context):
        template = None
        output_type = self.output_field.get_internal_type()
        # MySQL doesn't support explicit cast to float.
        if output_type == "FloatField":
            template = "(%(expressions)s + 0.0)"
        # MariaDB doesn't support explicit cast to JSON.
        elif output_type == "JSONField" and connection.mysql_is_mariadb:
            template = "JSON_EXTRACT(%(expressions)s, '$')"
        return self.as_sql(compiler, connection, template=template, **extra_context)

    def as_postgresql(self, compiler, connection, **extra_context):
        # CAST would be valid too, but the :: shortcut syntax is more readable.
        # 'expressions' is wrapped in parentheses in case it's a complex
        # expression.
        return self.as_sql(
            compiler,
            connection,
            template="(%(expressions)s)::%(db_type)s",
            **extra_context,
        )


class Coalesce(Func):
    """Return, from left to right, the first non-null expression."""

    function = "COALESCE"

    def __init__(self, *expressions, **extra):
        if len(expressions) < 2:
            raise ValueError("Coalesce must take at least two expressions")
        super().__init__(*expressions, **extra)

    @property
    def empty_result_set_value(self):
        for expression in self.get_source_expressions():
            result = expression.empty_result_set_value
            if result is NotImplemented or result is not None:
                return result
        return None


class Collate(Func):
    function = "COLLATE"
    template = "%(expressions)s %(function)s %(collation)s"
    # Inspired from
    # https://www.postgresql.org/docs/current/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS
    collation_re = _lazy_re_compile(r"^[\w\-]+$")

    def __init__(self, expression, collation):
        if not (collation and self.collation_re.match(collation)):
            raise ValueError("Invalid collation name: %r." % collation)
        self.collation = collation
        super().__init__(expression)

    def as_sql(self, compiler, connection, **extra_context):
        extra_context.setdefault("collation", connection.ops.quote_name(self.collation))
        return super().as_sql(compiler, connection, **extra_context)


class Greatest(Func):
    """
    Return the maximum expression.

    If any expression is null the return value is database-specific:
    On PostgreSQL, the maximum not-null expression is returned.
    On MySQL, Oracle, and SQLite, if any expression is null, null is returned.
    """

    function = "GREATEST"

    def __init__(self, *expressions, **extra):
        if len(expressions) < 2:
            raise ValueError("Greatest must take at least two expressions")
        super().__init__(*expressions, **extra)

    def as_sqlite(self, compiler, connection, **extra_context):
        """Use the MAX function on SQLite."""
        return super().as_sqlite(compiler, connection, function="MAX", **extra_context)


class JSONObject(Func):
    function = "JSON_OBJECT"
    output_field = JSONField()

    def __init__(self, **fields):
        expressions = []
        for key, value in fields.items():
            expressions.extend((Value(key), value))
        super().__init__(*expressions)

    def as_sql(self, compiler, connection, **extra_context):
        if not connection.features.has_json_object_function:
            raise NotSupportedError(
                "JSONObject() is not supported on this database backend."
            )
        return super().as_sql(compiler, connection, **extra_context)

    def as_postgresql(self, compiler, connection, **extra_context):
        copy = self.copy()
        copy.set_source_expressions(
            [
                Cast(expression, TextField()) if index % 2 == 0 else expression
                for index, expression in enumerate(copy.get_source_expressions())
            ]
        )
        return super(JSONObject, copy).as_sql(
            compiler,
            connection,
            function="JSONB_BUILD_OBJECT",
            **extra_context,
        )


class Least(Func):
    """
    Return the minimum expression.

    If any expression is null the return value is database-specific:
    On PostgreSQL, return the minimum not-null expression.
    On MySQL, Oracle, and SQLite, if any expression is null, return null.
    """

    function = "LEAST"

    def __init__(self, *expressions, **extra):
        if len(expressions) < 2:
            raise ValueError("Least must take at least two expressions")
        super().__init__(*expressions, **extra)

    def as_sqlite(self, compiler, connection, **extra_context):
        """Use the MIN function on SQLite."""
        return super().as_sqlite(compiler, connection, function="MIN", **extra_context)


class NullIf(Func):
    function = "NULLIF"
    arity = 2

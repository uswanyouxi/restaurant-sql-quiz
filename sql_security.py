
from pglast import parse_sql, ast, visitors
from pglast.parser import ParseError


class UnsafeQueryError(ValueError):
    """Raised when a SQL query is not allowed."""


ALLOWED_TABLES = {
    "restaurants",
    "menu_items",
    "orders",
}

ALLOWED_FUNCTIONS = {
    "count",
    "sum",
    "avg",
    "min",
    "max",
    "round",
    "coalesce",
    "nullif",
    "lower",
    "upper",
    "length",
    "abs",
}

ALLOWED_NODE_TYPES = {
    "SelectStmt",
    "RangeVar",
    "RangeSubselect",
    "JoinExpr",
    "RangeTblRef",
    "FromExpr",
    "ResTarget",
    "ColumnRef",
    "A_Const",
    "A_Expr",
    "BoolExpr",
    "NullTest",
    "FuncCall",
    "SortBy",
    "TypeCast",
    "TypeName",
    "String",
    "Integer",
    "Float",
    "Boolean",
    "Null",
    "A_Star",
    "Alias",
    "CommonTableExpr",
    "WithClause",
    "GroupingSet",
    "CoalesceExpr",
    "CaseExpr",
    "CaseWhen",
    "CaseTestExpr",
    "SubLink",
    "List",
}


def validate_sql(sql: str) -> str:
    """Validate a read-only quiz query using PostgreSQL AST."""

    if not isinstance(sql, str) or not sql.strip():
        raise UnsafeQueryError("Please enter a SQL query.")

    try:
        statements = parse_sql(sql)
    except ParseError as error:
        raise UnsafeQueryError("Invalid SQL syntax.") from error

    if len(statements) != 1:
        raise UnsafeQueryError(
            "Only one SQL statement is allowed."
        )

    statement = statements[0].stmt

    if not isinstance(statement, ast.SelectStmt):
        raise UnsafeQueryError(
            "Only SELECT queries are allowed."
        )

    for node in visitors.Visitor()(statement):
        pass




    # Collect CTE names defined in this query.
    # Each name must be unqualified (no schema).
    cte_names = set()

    class CTECollector(visitors.Visitor):
        def visit(self, ancestors, node):
            if isinstance(node, ast.CommonTableExpr):
                cte_names.add(node.ctename.lower())

    CTECollector()(statement)

    def check_node(node):
        node_type = type(node).__name__

        if node_type not in ALLOWED_NODE_TYPES:
            raise UnsafeQueryError(
                f"SQL feature not allowed: {node_type}"
            )

       
        if isinstance(node, ast.RangeVar):
            table = node.relname.lower()
            schema = node.schemaname

            # CTE references must not specify a schema.
            if schema is None and table in cte_names:
                return

            # All real database tables must be allowlisted.
            if table not in ALLOWED_TABLES:
                raise UnsafeQueryError(
                    "Only restaurant data tables are allowed."
                )

            if schema not in (None, "public"):
                raise UnsafeQueryError(
                    "Only the public schema is allowed."
                )


        if isinstance(node, ast.FuncCall):
            function_name = ".".join(
                part.sval.lower() for part in node.funcname
            )

            if function_name not in ALLOWED_FUNCTIONS:
                raise UnsafeQueryError(
                    "This SQL function is not allowed."
                )

        if isinstance(node, ast.SelectStmt):
            if node.intoClause is not None:
                raise UnsafeQueryError(
                    "SELECT INTO is not allowed."
                )

            if node.lockingClause:
                raise UnsafeQueryError(
                    "Row locking is not allowed."
                )

    class SecurityVisitor(visitors.Visitor):
        def visit(self, ancestors, node):
            check_node(node)

    SecurityVisitor()(statement)

    return sql.strip()

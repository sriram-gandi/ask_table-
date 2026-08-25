import re


def preprocess_sql(
    sql: str
) -> str:

    if not sql:

        raise ValueError(
            "SQL query is empty"
        )

    sql = sql.strip()

    sql = re.sub(
        r"^```sql",
        "",
        sql,
        flags=re.IGNORECASE
    )

    sql = re.sub(
        r"^```",
        "",
        sql
    )

    sql = sql.replace(
        "```",
        ""
    )

    sql = sql.strip()

    forbidden_keywords = [

        "DROP",
        "DELETE",
        "UPDATE",
        "INSERT",
        "ALTER",
        "CREATE",
        "ATTACH",
        "DETACH"
    ]

    upper_sql = sql.upper()

    for keyword in forbidden_keywords:

        if keyword in upper_sql:

            raise ValueError(
                f"Forbidden SQL keyword: "
                f"{keyword}"
            )

    if not upper_sql.startswith(
        "SELECT"
    ):

        raise ValueError(
            "Only SELECT queries are allowed"
        )

    return sql
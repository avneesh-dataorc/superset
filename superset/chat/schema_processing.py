from superset import db
from superset.models.core import Database
import logging
from sqlalchemy.engine.reflection import Inspector

logger = logging.getLogger(__name__)


def get_superset_database(dbid):
    """Fetch the Superset Database object for a given dbid."""
    database = db.session.query(Database).filter_by(id=dbid).first()

    if not database:
        raise ValueError(f"Database with ID {dbid} not found.")

    return database

def get_schemas_and_tables(dbid):
    """Fetch schemas, tables, and column details from the database."""
    database = get_superset_database(dbid)

    # Use a context manager to get the SQLAlchemy engine
    with database.get_sqla_engine() as engine:
        inspector = Inspector.from_engine(engine)

        # Get all schemas
        schemas = inspector.get_schema_names()

        schema_tables = {}
        for schema in schemas:
            tables = inspector.get_table_names(schema=schema)

            table_details = []
            for table in tables:
                # Fetch column details for the table
                columns = inspector.get_columns(table, schema=schema)

                # Fetch table description (comment)
                table_comment = inspector.get_table_comment(table, schema=schema).get("text", "")

                table_details.append({
                    "table": table,
                    "description": table_comment,
                    "columns": [
                        {
                            "name": col["name"],
                            "type": str(col["type"]),
                            "comment": col.get("comment", "")  # Fetch column comments if available
                        }
                        for col in columns
                    ],
                })

            schema_tables[schema] = table_details

    return schema_tables


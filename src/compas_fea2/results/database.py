import json
import sqlite3

import h5py
import numpy as np

from compas_fea2.base import FEAData


class ResultsDatabase(FEAData):
    """Base class for results databases.
    
    This class serves as a base for different types of results databases,
    such as SQLite, HDF5, and JSON. It provides a common interface for
    accessing and manipulating results data associated with a problem.
    
    The job of this class is to manage the results database for a given problem,
    allowing for the retrieval and storage of results in various formats. It reads
    the data from a Parser and provides methods to access results sets, extract fields,
    and perform queries on the results.
    
    Parameters
    ----------
    problem : object
        The problem instance containing the model and database path.
    **kwargs : dict
        Additional keyword arguments for initialization.
        
    Attributes
    ----------
    problem : object
        The problem instance associated with this results database.
    model : object
        The model instance associated with the problem.
    """
    def __init__(self, problem, **kwargs):
        super().__init__(**kwargs)
        self._registration = problem

    @property
    def problem(self):
        return self._registration

    @property
    def model(self):
        return self.problem.model

    @classmethod
    def sqlite(cls, problem, **kwargs) -> "SQLiteResultsDatabase":
        return SQLiteResultsDatabase(problem, **kwargs)

    @classmethod
    def hdf5(cls, problem, **kwargs):
        return HDF5ResultsDatabase(problem, **kwargs)

    @classmethod
    def json(cls, problem, **kwargs):
        return JSONResultsDatabase(problem, **kwargs)


class JSONResultsDatabase(ResultsDatabase):
    """JSON wrapper class to store and access FEA results."""
    
    def __init__(self, problem, **kwargs):
        super().__init__(problem=problem, **kwargs)
        raise NotImplementedError("JSONResultsDatabase is not implemented yet.")

    # def get_results_set(self, filename, field):
    #     """Get a set of results from a JSON file."""
    #     with open(filename, "r") as f:
    #         data = json.load(f)
    #     return data[field]


class HDF5ResultsDatabase(ResultsDatabase):
    """HDF5 wrapper class to store and access FEA results."""

    def __init__(self, problem, **kwargs):
        super().__init__(problem, **kwargs)
        raise NotImplementedError("HDF5ResultsDatabase is not implemented yet.")
    
    # def save_to_hdf5(self, key, data):
    #     """Save data to the HDF5 database."""
    #     with h5py.File(self.db_path, "a") as hdf5_file:
    #         group = hdf5_file.require_group(key)
    #         for k, v in data.items():
    #             if isinstance(v, (int, float, np.ndarray)):
    #                 group.create_dataset(k, data=np.array(v))
    #             elif isinstance(v, list) and all(isinstance(i, (int, float)) for i in v):
    #                 group.create_dataset(k, data=np.array(v, dtype="f8"))
    #             elif isinstance(v, list) and all(isinstance(i, FEAData) for i in v):
    #                 # sub_group = group.require_group(k)
    #                 for i, obj in enumerate(v):
    #                     obj.save_to_hdf5(self.db_path, f"{key}/{k}/element_{i}")
    #             elif isinstance(v, dict):
    #                 group.attrs[k] = json.dumps(v)
    #             elif isinstance(v, str):
    #                 group.attrs[k] = v
    #             else:
    #                 print(f"Warning: Skipping {k} (Unsupported type {type(v)})")

    # def load_from_hdf5(self, key):
    #     """Load data from the HDF5 database."""
    #     data = {}
    #     with h5py.File(self.db_path, "r") as hdf5_file:
    #         if key not in hdf5_file:
    #             raise KeyError(f"Key '{key}' not found in HDF5 database.")
    #         group = hdf5_file[key]
    #         for k in group.keys():
    #             if k.startswith("element_"):
    #                 data.setdefault("elements", {})[int(k.split("_")[-1])] = self.load_from_hdf5(f"{key}/{k}")
    #             else:
    #                 dataset = group[k][:]
    #                 data[k] = dataset.tolist() if dataset.shape != () else dataset.item()
    #         for k, v in group.attrs.items():
    #             if isinstance(v, str) and (v.startswith("[") or v.startswith("{")):
    #                 try:
    #                     data[k] = json.loads(v)
    #                 except json.JSONDecodeError:
    #                     data[k] = v
    #             else:
    #                 data[k] = v
    #     return data

    # def extract_field(self, field_name):
    #     """Extract a specific field group from the HDF5 database."""
    #     with h5py.File(self.db_path, "r") as hdf5_file:
    #         if field_name in hdf5_file:
    #             return {key: hdf5_file[field_name][key][:] for key in hdf5_file[field_name].keys()}
    #         else:
    #             raise KeyError(f"Field '{field_name}' not found in HDF5 database.")

    # def get_max_value(self, field_name):
    #     """Get the maximum value of a specific field."""
    #     with h5py.File(self.db_path, "r") as hdf5_file:
    #         if field_name in hdf5_file:
    #             return max([np.max(hdf5_file[field_name][key][:]) for key in hdf5_file[field_name].keys()])
    #         else:
    #             raise KeyError(f"Field '{field_name}' not found in HDF5 database.")

    # def get_results_at_element(self, element_id):
    #     """Retrieve results for a specific element."""
    #     with h5py.File(self.db_path, "r") as hdf5_file:
    #         element_key = f"elements/element_{element_id}"
    #         if element_key in hdf5_file:
    #             return {key: hdf5_file[element_key][key][:] for key in hdf5_file[element_key].keys()}
    #         else:
    #             raise KeyError(f"Element '{element_id}' not found in HDF5 database.")

    # def get_results_at_node(self, node_id):
    #     """Retrieve results for a specific node."""
    #     with h5py.File(self.db_path, "r") as hdf5_file:
    #         node_key = f"nodes/node_{node_id}"
    #         if node_key in hdf5_file:
    #             return {key: hdf5_file[node_key][key][:] for key in hdf5_file[node_key].keys()}
    #         else:
    #             raise KeyError(f"Node '{node_id}' not found in HDF5 database.")


class SQLiteResultsDatabase(ResultsDatabase):
    """sqlite3 wrapper class to access the SQLite database.
    
    This class provides methods to connect to the SQLite database,
    execute queries, and retrieve results from the database.
    
    The tables of the database are created based on the
    `output_cls.sqltable_schema` property, which defines the schema
    for each field output class. The results are stored in the database
    in a structured format, allowing for efficient querying and retrieval.
    
    Parameters
    ----------
    problem : object
        The problem instance containing the model and database path.
    **kwargs : dict
        Additional keyword arguments for initialization.
        
    Attributes
    ----------
    db_uri : str
        The URI of the SQLite database.
    connection : sqlite3.Connection
        The connection object to the SQLite database.
    cursor : sqlite3.Cursor
        The cursor object for executing SQL queries.
    table_names : list
        The names of all tables in the database.
    fields : list
        The names of all fields in the database, excluding the 'fields' table.
        
    Methods
    -------
    db_connection()
        Create and return a connection to the SQLite database.
    execute_query(query, params=None)
        Execute a previously-defined query and return the result set.
    table_names()
        Get the names of all tables in the database.
    fields()
        Get the names of all fields in the database, excluding the 'fields' table.
    column_names(table_name)
        Get the names of all columns in a given table.
    get_table(table_name)
        Get a table from the database.
    get_column_values(table_name, column_name)
        Get all the values in a given column from a table.
    get_column_unique_values(table_name, column_name)
        Get all the unique values in a given column from a table.
    get_rows(table_name, columns_names, filters, func=None)
        Get all the rows in a given table that match the filtering criteria
        and return the values for each column.
    to_result(results_set, results_func, field_name)
        Convert a set of results in the database to the appropriate result object.
    create_table_for_output_class(output_cls, results)
        Reads the table schema from `output_cls.get_table_schema()` and creates the table in the
        given database. 
        """

    def __init__(self, problem, **kwargs):
        super().__init__(problem=problem, **kwargs)

        self.db_uri = problem.path_db
        self.connection = self.db_connection()
        self.cursor = self.connection.cursor()

    def db_connection(self):
        """
        Create and return a connection to the SQLite database.

        Returns
        -------
        sqlite3.Connection
            The database connection.
        """
        if not self.db_uri:
            raise ValueError("Database URI is not set. Please provide a valid database path.")
        if not self.db_uri.endswith(".db"):
            raise ValueError("Database URI must end with '.db'. Please provide a valid SQLite database file.")
        if not self.problem.path:
            raise ValueError("Problem path is not set. Please provide a valid problem path.")
        return sqlite3.connect(self.db_uri)

    def execute_query(self, query, params=None):
        """
        Execute a previously-defined query.
        This method connects to the database, executes the query with
        the provided parameters, and returns the result set.
        
        Example
        -------
        >>> db = SQLiteResultsDatabase(problem)
        >>> result = db.execute_query("SELECT * FROM my_table WHERE id = ?", (1,))
        >>> print(result)

        Parameters
        ----------
        query : str
            The SQL query to execute.
        params : tuple, optional
            The parameters to bind to the query.

        Returns
        -------
        list
            The result set.
        """
        self.connection = self.db_connection()
        self.cursor = self.connection.cursor()
        self.cursor.execute(query, params or ())
        result_set = self.cursor.fetchall()
        self.connection.close()
        return result_set

    # =========================================================================
    #                       Query methods
    # =========================================================================
    @property
    def table_names(self):
        """
        Get the names of all tables in the database.

        Returns
        -------
        list
            A list of table names.
        """
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [row[0] for row in self.cursor.fetchall()]

    @property
    def fields(self):
        """
        Get the names of all fields in the database, excluding the 'fields' table.

        Returns
        -------
        list
            A list of field names.
        """
        return [c for c in self.table_names if c != "fields"]

    def column_names(self, table_name):
        """
        Get the names of all columns in a given table.

        Parameters
        ----------
        table_name : str
            The name of the table.

        Returns
        -------
        list
            A list of column names.
        """
        self.cursor.execute(f"PRAGMA table_info({table_name});")
        return [row[1] for row in self.cursor.fetchall()]

    def get_table(self, table_name):
        """
        Get a table from the database.

        Parameters
        ----------
        table_name : str
            The name of the table.

        Returns
        -------
        list of tuples
            The table data.
        """
        query = f"SELECT * FROM {table_name}"
        return self.execute_query(query)

    def get_column_values(self, table_name, column_name):
        """
        Get all the values in a given column from a table.

        Parameters
        ----------
        table_name : str
            The name of the table.
        column_name : str
            The name of the column.

        Returns
        -------
        list
            A list of values from the specified column.
        """
        query = f"SELECT {column_name} FROM {table_name}"
        return self.execute_query(query)

    def get_column_unique_values(self, table_name, column_name):
        """
        Get all the unique values in a given column from a table.

        Parameters
        ----------
        table_name : str
            The name of the table.
        column_name : str
            The name of the column.

        Returns
        -------
        set
            The unique column values.
        """
        return set(self.get_column_values(table_name, column_name))

    def get_rows(self, table_name, columns_names, filters, func=None):
        """
        Get all the rows in a given table that match the filtering criteria
        and return the values for each column.

        Parameters
        ----------
        table_name : str
            The name of the table.
        columns_names : list
            Name of each column to retrieve. The results are output in the same
            order.
        filters : dict
            Filtering criteria as {"column_name":[admissible values]}
        func : str, optional
            SQL function to apply to the columns. Default is None.

        Returns
        -------
        list of lists
            List with each row as a list.
        """
        filter_conditions = " AND ".join([f"{k} IN ({','.join(['?' for _ in v])})" for k, v in filters.items()])
        if not func:
            query = f"SELECT {', '.join(columns_names)} FROM {table_name} WHERE {filter_conditions}"
        else:
            query = f"SELECT {', '.join(columns_names)}  FROM {table_name} WHERE {filter_conditions} ORDER BY ({func[1]}) {func[0]} LIMIT 1"
        params = [item for sublist in filters.values() for item in sublist]
        return self.execute_query(query, params)

    # =========================================================================
    #                       FEA2 Methods
    # =========================================================================
    
    def to_result(self, result_line, results_func, field_name):
        """
        Convert a result line in the database to the appropriate
        result object.

        Parameters
        ----------
        result_line : dict
            A dictionary representing a single row of results from the database.
        results_func : str
            The function to call on the part to get the member (it can be a node
            or an element).
        field_name : str
            The name of the field to extract from the results. 
            
        Returns
        -------
        object
            An instance of the result class corresponding to the field name,
            initialized with the data from the result line.
        """
        if "step" in result_line:
            result_line.pop("step")
        m = getattr(self.model, results_func)(result_line.pop("key"))[0]
        if not m:
            raise ValueError(f"Member not in {self.model}")        
        return m.results_cls[field_name](m, **result_line)

    def to_results(self, results_set, results_func, field_name):
        """
        Convert a set of results data in the database to the appropriate
        result object.

        Parameters
        ----------
        results_set : list of tuples
            The set of results retrieved from the database.
        results_func : str
            The function to call on the part to get the member (it can be a node
            or an element).
        field_name : str
            The name of the field to extract from the results.

        Returns
        -------
        dict
            Dictionary grouping the results per Step.
        """
        results = {}
        for r in results_set:
            step = self.problem.find_step_by_name(r.pop("step"))
            results.setdefault(step, [])
            results[step].append(self.to_result(r, results_func, field_name))
        return results











    def add_results_to_output_class_table(self, output_cls, results):
        """
        Reads the table schema from `output_cls.get_table_schema()`
        and creates the table in the given database.

        Parameters
        ----------
        output_cls : _Output subclass
            A class like NodeOutput that implements `get_table_schema()`.
        connection : sqlite3.Connection
            SQLite3 connection object.
        results : list of tuples
            Data to be inserted into the table.
        """
        cursor = self.connection.cursor()

        schema = output_cls.sqltable_schema
        table_name = schema["table_name"]
        columns_info = schema["columns"]

        # Build CREATE TABLE statement:
        columns_sql_str = ", ".join([f"{col_name} {col_def}" for col_name, col_def in columns_info])
        create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql_str})"
        cursor.execute(create_sql)
        self.connection.commit()

        # Insert data into the table:
        insert_columns = [col_name for col_name, col_def in columns_info if "PRIMARY KEY" not in col_def.upper()]
        col_names_str = ", ".join(insert_columns)
        placeholders_str = ", ".join(["?"] * len(insert_columns))
        sql = f"INSERT INTO {table_name} ({col_names_str}) VALUES ({placeholders_str})"
        cursor.executemany(sql, results)
        self.connection.commit()

import pyodbc
import pandas as pd


class DAIPoolDB:
    server = 'web3.database.windows.net'
    database = 'web3ct'
    username = 'freeman'
    password = '{19081789d@}'
    driver = '{ODBC Driver 17 for SQL Server}'

    def __init__(self):
        self.connect = pyodbc.connect('DRIVER=' + DAIPoolDB.driver + ';SERVER=tcp:' + DAIPoolDB.server +
                                      ';PORT=1433;DATABASE=' + DAIPoolDB.database + ';UID=' + DAIPoolDB.username +
                                      ';PWD=' + DAIPoolDB.password)
        self.cursor = self.connect.cursor()

    def close(self):
        self.cursor.close()
        self.connect.close()

    def execute_sql_code(self, sql_code):
        self.cursor.execute(sql_code)
        return self.cursor.fetchall()

    def get_col_names(self, table):
        sql_code = ("SELECT COLUMN_NAME "
                    "FROM INFORMATION_SCHEMA.COLUMNS "
                    f"WHERE TABLE_NAME = \'{table}\' "
                    "ORDER BY ORDINAL_POSITION")
        self.cursor.execute(sql_code)
        return [item[0] for item in self.cursor.fetchall()]

    def insert_df(self, df, table):
        self.cursor.execute(f"SET IDENTITY_INSERT {table} ON")

        col_names = self.get_col_names(table)
        df = df[col_names]
        col_names_str = ','.join(col_names)
        for index, row in df.iterrows():
            attrs_str = ','.join(
                [str(row[col_name]) if type(row[col_name]) != str else "\'" + row[col_name] + "\'" for col_name in
                 col_names]
            )

            sql_code = f"INSERT INTO {table} ({col_names_str}) VALUES ({attrs_str})"
            # print(sql_code)
            self.cursor.execute(sql_code)
        self.connect.commit()

        self.cursor.execute(f"SET IDENTITY_INSERT {table} OFF")

    def insert_df_with_dict(self, df, table, data_db_attr_dict):
        self.cursor.execute(f"SET IDENTITY_INSERT {table} ON")

        col_names = self.get_col_names(table)
        df = df[[data_db_attr_dict[col_name] for col_name in col_names]]
        col_names_str = ','.join(col_names)
        for index, row in df.iterrows():
            attrs_str = ','.join(
                [str(row[data_db_attr_dict[col_name]]) if type(row[data_db_attr_dict[col_name]]) != str else "\'" + row[
                    data_db_attr_dict[col_name]] + "\'" for col_name in
                 col_names]
            )

            sql_code = f"INSERT INTO {table} ({col_names_str}) VALUES ({attrs_str})"
            # print(sql_code)
            self.cursor.execute(sql_code)
        self.connect.commit()

        self.cursor.execute(f"SET IDENTITY_INSERT {table} OFF")

    def insert_csv(self, path, table):

        df = pd.read_csv(path)
        self.insert_df(df, table)

    def insert_csv_with_dict(self, path, table, data_db_attr_dict):

        df = pd.read_csv(path)
        self.insert_df_with_dict(df,table,data_db_attr_dict)


myDB = DAIPoolDB()
test_table = "Course"
sql = '''SELECT  Course.Name, Course.Teacher, Credit.Grade
FROM  Course AS course
    INNER JOIN Credit AS credit ON credit.CourseId = course.CourseId
    INNER JOIN Student AS student ON student.StudentId = credit.StudentId
    INNER JOIN Person AS person ON person.PersonId = student.PersonId
WHERE person.FirstName = 'Noe'
    AND person.LastName = 'Coleman\''''
result = myDB.execute_sql_code(sql)
print(result)
print(myDB.get_col_names(test_table))
myDB.insert_csv("testCSV.csv", test_table)

test_data_db_attr_dict = {"CourseId": "ci", "Teacher": "t", "Name": "n"}
myDB.insert_csv_with_dict("testCSV1.csv", test_table, test_data_db_attr_dict)

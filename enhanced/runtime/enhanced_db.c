#include <sqlite3.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

sqlite3* enhanced_db_open(char* path) {
    sqlite3* db;
    int rc = sqlite3_open(path, &db);
    if (rc) {
        fprintf(stderr, "Can't open database: %s\n", sqlite3_errmsg(db));
        return NULL;
    }
    return db;
}

void enhanced_db_close(sqlite3* db) {
    if (db) {
        sqlite3_close(db);
    }
}

void enhanced_db_exec(sqlite3* db, char* sql) {
    char* err_msg = 0;
    int rc = sqlite3_exec(db, sql, 0, 0, &err_msg);
    if (rc != SQLITE_OK) {
        fprintf(stderr, "SQL error: %s\n", err_msg);
        sqlite3_free(err_msg);
    }
}

// Simplified query that returns a mock JSON string for now.
char* enhanced_db_query(sqlite3* db, char* table, char* conditions) {
    // In a real implementation, we would build a SELECT query,
    // execute it, and format the result as a JSON string.
    // For now, return a mock result.
    return "[[\"mock_col\"], [\"mock_val\"]]";
}


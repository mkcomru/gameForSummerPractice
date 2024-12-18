import sqlite3

class DB:
    def __init__(self, db_file):
        # Initialisation
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.commit = self.conn.commit

    def get_level(self):
        # Get user's level
        result = self.cursor.execute("SELECT `level` FROM `user`")
        return result.fetchone()[0]

    def set_level(self, level):
        # Set user's level
        self.cursor.execute("UPDATE `user` SET `level` = ?", (level,))
        self.conn.commit()

    def level_up(self):
        # Level +1
        self.cursor.execute("UPDATE `user` SET `level` = `level` + 1")
        self.commit()

    def set_top(self, N, X):
        # Set user's top #N via X-score
        self.cursor.execute(f"UPDATE `user` SET `top_{N}` = {X}")
        self.commit()

    def set_display(self, N):
        # Set display status as N
        self.cursor.execute(f"UPDATE `user` SET `display` = {N}")
        self.commit()

    def get_top(self, N):
        # Get user's top #N
        result = self.cursor.execute(f"SELECT `top_{N}` FROM `user`")
        return result.fetchone()[0]

    def get_display(self):
        # Get display status
        result = self.cursor.execute("SELECT `display` FROM `user`")
        return result.fetchone()[0]

    def close(self):
        # Close connection
        self.conn.close()

    def clear(self):
        # Clear DB file
        self.cursor.execute(f"DELETE FROM `user` WHERE `level` = level")
        self.cursor.execute("INSERT INTO `user` (`level`) VALUES (1)")
        self.commit()
# model/schema.py

from .db import db_connect
from .constants import (
    REGISTRAR_TABLE,
    PAYMENT_TABLE,
    PENDING_TABLE,
    STUDENT_TABLE,
    STRANDS_TABLE,
    REPORTS_TABLE,
    ENROLLMENT_REPORTS_TABLE,
    SLOTS_TABLE  # <-- ADDED
)
from .helpers import table_exists, column_exists
from .schedule import schedule_label_for_section


def ensure_strands_table_and_seed():
    conn = db_connect()
    cur = conn.cursor()
    cur.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {STRANDS_TABLE} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL UNIQUE
        ) ENGINE=InnoDB
        """
    )
    conn.commit()

    # Seed default strands
    strands = ["STEM", "ABM", "HUMSS", "GAS", "TVL"]
    for s in strands:
        cur.execute(f"INSERT IGNORE INTO {STRANDS_TABLE} (name) VALUES (%s)", (s,))
    conn.commit()
    cur.close()
    conn.close()


def ensure_registrars_table():
    conn = db_connect()
    cur = conn.cursor()
    cur.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {REGISTRAR_TABLE} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            registrar_id VARCHAR(20) UNIQUE NOT NULL,
            full_name VARCHAR(150),
            email VARCHAR(150) UNIQUE NOT NULL,
            contact_number VARCHAR(50),
            username VARCHAR(50),
            password VARCHAR(255),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB
        """
    )
    conn.commit()
    cur.close()
    conn.close()


def _ensure_fk_with_mapping(cur, table, fk_col, text_col, ref_table, ref_col, fk_name):
    """Safely adds a foreign key and maps existing text data to the new ID column."""
    if not column_exists(table, fk_col):
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {fk_col} INT NULL")

    # Auto-map existing text values to the ID column
    if text_col:
        try:
            cur.execute(f"""
                UPDATE {table} t
                JOIN {ref_table} r ON t.{text_col} = r.name
                SET t.{fk_col} = r.{ref_col}
                WHERE t.{fk_col} IS NULL
            """)
        except Exception:
            pass

    # Apply the constraint
    cur.execute(
        """
        SELECT CONSTRAINT_NAME 
        FROM information_schema.KEY_COLUMN_USAGE 
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND CONSTRAINT_NAME = %s
        """, (table, fk_name)
    )
    if not cur.fetchone():
        try:
            cur.execute(
                f"""
                ALTER TABLE {table} 
                ADD CONSTRAINT {fk_name} 
                FOREIGN KEY ({fk_col}) REFERENCES {ref_table}({ref_col}) 
                ON UPDATE CASCADE ON DELETE SET NULL
                """
            )
        except Exception as e:
            print(f"Notice: Could not add FK {fk_name} to {table}: {e}")


def ensure_payment_queue_table():
    ensure_strands_table_and_seed()
    conn = db_connect()
    cur = conn.cursor()
    cur.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {PAYMENT_TABLE} (
          id INT AUTO_INCREMENT PRIMARY KEY,
          student_id VARCHAR(20) NOT NULL UNIQUE,
          first_name VARCHAR(100) NOT NULL,
          last_name VARCHAR(100) NOT NULL,
          email VARCHAR(150),
          contact_number VARCHAR(50),
          grade_level VARCHAR(10),
          strand VARCHAR(20),
          form_137 VARCHAR(20),
          form_138 VARCHAR(20),
          birth_certificate VARCHAR(20),
          section VARCHAR(50),
          schedule VARCHAR(50) DEFAULT '',
          assignments TEXT,
          payment_status VARCHAR(15) DEFAULT 'Unpaid',
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB
        """
    )
    conn.commit()

    # Ensure it is connected to the Strands table for the ERD
    _ensure_fk_with_mapping(cur, PAYMENT_TABLE, "strand_id", "strand", STRANDS_TABLE, "id", "fk_payment_strand")

    conn.commit()
    cur.close()
    conn.close()


def ensure_pending_enrollments_table_and_columns():
    ensure_strands_table_and_seed()
    conn = db_connect()
    cur = conn.cursor()
    cur.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {PENDING_TABLE} (
          id INT AUTO_INCREMENT PRIMARY KEY,
          first_name VARCHAR(100),
          last_name VARCHAR(100),
          email VARCHAR(150),
          contact_number VARCHAR(50),
          grade_level VARCHAR(20),
          strand VARCHAR(50),
          form_137 VARCHAR(20),
          form_138 VARCHAR(20),
          birth_certificate VARCHAR(20),
          section VARCHAR(50),
          schedule VARCHAR(50) DEFAULT '',
          adviser VARCHAR(150),
          teacher_assignments TEXT,
          payment_status VARCHAR(20) DEFAULT 'Unpaid',
          submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          student_id VARCHAR(20) UNIQUE
        ) ENGINE=InnoDB
        """
    )
    conn.commit()

    # Ensure it is connected to the Strands table for the ERD
    _ensure_fk_with_mapping(cur, PENDING_TABLE, "strand_id", "strand", STRANDS_TABLE, "id", "fk_pending_strand")

    conn.commit()
    cur.close()
    conn.close()


def ensure_student_optional_columns():
    ensure_strands_table_and_seed()
    ensure_registrars_table()

    if not table_exists(STUDENT_TABLE):
        conn = db_connect()
        cur = conn.cursor()
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {STUDENT_TABLE} (
              id INT AUTO_INCREMENT PRIMARY KEY,
              student_id VARCHAR(12) UNIQUE,
              first_name VARCHAR(100),
              last_name VARCHAR(100),
              email VARCHAR(150),
              contact_number VARCHAR(30),
              grade_level ENUM('11','12'),
              strand VARCHAR(50),
              form_137 VARCHAR(20),
              form_138 VARCHAR(20),
              birth_certificate VARCHAR(20),
              status ENUM('Pending','Enrolled','Dropped') DEFAULT 'Pending',
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB
            """
        )
        conn.commit()
        cur.close()
        conn.close()

    conn = db_connect()
    cur = conn.cursor()

    columns_to_add = [
        ("section", "VARCHAR(50)"),
        ("schedule", "VARCHAR(50) DEFAULT ''"),
        ("adviser", "VARCHAR(100)"),
        ("payment_status", "VARCHAR(20)"),
        ("payment_approved", "TINYINT(1) DEFAULT 0"),
        ("paid_at", "DATETIME"),
        ("enrolled_at", "DATETIME"),
        ("teacher_assignments", "TEXT"),
        ("assignments", "TEXT")
    ]

    for col, definition in columns_to_add:
        if not column_exists(STUDENT_TABLE, col):
            try:
                cur.execute(f"ALTER TABLE {STUDENT_TABLE} ADD COLUMN {col} {definition}")
            except Exception as e:
                print(f"Could not add column {col}: {e}")

    # Map existing ERD Connections
    _ensure_fk_with_mapping(cur, STUDENT_TABLE, "registrar_id", None, REGISTRAR_TABLE, "id", "fk_student_registrar")
    _ensure_fk_with_mapping(cur, STUDENT_TABLE, "strand_id", "strand", STRANDS_TABLE, "id", "fk_student_strand")

    conn.commit()
    cur.close()
    conn.close()


def ensure_reports_table_and_seed():
    ensure_strands_table_and_seed()
    conn = db_connect()
    cur = conn.cursor(dictionary=True)

    cur.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {REPORTS_TABLE} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            strand VARCHAR(20),
            daily INT DEFAULT 0,
            weekly INT DEFAULT 0,
            monthly INT DEFAULT 0,
            yearly INT DEFAULT 0,
            total INT DEFAULT 0,
            updated_at DATETIME
        ) ENGINE=InnoDB
        """
    )

    _ensure_fk_with_mapping(cur, REPORTS_TABLE, "strand_id", "strand", STRANDS_TABLE, "id", "fk_reports_strands")

    cur.execute(f"SELECT id, name FROM {STRANDS_TABLE} ORDER BY name ASC")
    strand_rows = cur.fetchall() or []

    for s in strand_rows:
        cur.execute(f"SELECT id FROM {REPORTS_TABLE} WHERE strand_id=%s LIMIT 1", (s["id"],))
        if not cur.fetchone():
            cur.execute(
                f"""
                INSERT INTO {REPORTS_TABLE}
                    (strand, strand_id, daily, weekly, monthly, yearly, total, updated_at)
                VALUES (%s, %s, 0, 0, 0, 0, 0, NOW())
                """,
                (s["name"], s["id"])
            )
    conn.commit()
    cur.close()
    conn.close()


# --- NEW: SLOTS DATABASE MANAGEMENT ---

def ensure_slots_table_and_seed():
    """Creates the Slots table and populates the default 50 max slots for every section."""
    conn = db_connect()
    cur = conn.cursor()

    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {SLOTS_TABLE} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            strand VARCHAR(50) NOT NULL,
            grade_level VARCHAR(10) NOT NULL,
            section VARCHAR(50) NOT NULL,
            schedule VARCHAR(50) DEFAULT '',
            max_slots INT DEFAULT 50,
            taken_slots INT DEFAULT 0,
            available_slots INT DEFAULT 50,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_section (strand, grade_level, section)
        ) ENGINE=InnoDB
    """)

    for col, definition in [
        ("schedule", "VARCHAR(50) DEFAULT ''"),
        ("taken_slots", "INT DEFAULT 0"),
        ("updated_at", "DATETIME DEFAULT CURRENT_TIMESTAMP"),
    ]:
        if not column_exists(SLOTS_TABLE, col):
            cur.execute(f"ALTER TABLE {SLOTS_TABLE} ADD COLUMN {col} {definition}")

    strands = ["STEM", "ABM", "HUMSS", "GAS", "TVL"]
    grades = ["11", "12"]
    sections = ["1", "2", "3"]

    # Initialize all empty sections to 50 slots
    for strand in strands:
        for grade in grades:
            for sec in sections:
                section_name = f"{strand}{grade} - {sec}"
                schedule = schedule_label_for_section(section_name)
                cur.execute(f"SELECT id FROM {SLOTS_TABLE} WHERE strand=%s AND grade_level=%s AND section=%s",
                            (strand, grade, section_name))
                if not cur.fetchone():
                    cur.execute(f"""
                        INSERT INTO {SLOTS_TABLE}
                            (strand, grade_level, section, schedule, max_slots, taken_slots, available_slots, updated_at)
                        VALUES (%s, %s, %s, %s, 50, 0, 50, NOW())
                    """, (strand, grade, section_name, schedule))
                else:
                    cur.execute(
                        f"UPDATE {SLOTS_TABLE} SET schedule=%s WHERE strand=%s AND grade_level=%s AND section=%s",
                        (schedule, strand, grade, section_name)
                    )

    conn.commit()
    cur.close()
    conn.close()


def sync_all_slots():
    """
    Recalculates available slots securely by scanning the enrolled and pending tables.
    Updates the SLOTS_TABLE to ensure perfect data consistency for the charts.
    """
    ensure_slots_table_and_seed()
    conn = db_connect()
    cur = conn.cursor(dictionary=True)

    has_payment = table_exists(PAYMENT_TABLE)
    has_students = table_exists(STUDENT_TABLE)

    cur.execute(f"SELECT id, strand, grade_level, section, max_slots FROM {SLOTS_TABLE}")
    slots = cur.fetchall()

    for slot in slots:
        strand = slot['strand']
        grade = slot['grade_level']
        section = slot['section']
        max_s = slot['max_slots']

        # Format string to strip extra spaces preventing mismatch (e.g. "STEM11 - 1" -> "STEM11-1")
        clean_sec = section.replace(" ", "")

        enrolled = 0
        if has_students and column_exists(STUDENT_TABLE, "status"):
            cur.execute(f"""
                SELECT COUNT(*) as c FROM {STUDENT_TABLE} 
                WHERE strand=%s AND grade_level=%s AND REPLACE(section, ' ', '')=%s AND status='Enrolled'
            """, (strand, grade, clean_sec))
            res = cur.fetchone()
            if res:
                enrolled = res['c']

        pending = 0
        if has_payment:
            cur.execute(f"""
                SELECT COUNT(*) as c FROM {PAYMENT_TABLE} 
                WHERE strand=%s AND grade_level=%s AND REPLACE(section, ' ', '')=%s
            """, (strand, grade, clean_sec))
            res = cur.fetchone()
            if res:
                pending = res['c']

        taken = enrolled + pending
        available = max(0, max_s - taken)

        cur.execute(
            f"UPDATE {SLOTS_TABLE} SET taken_slots=%s, available_slots=%s, updated_at=NOW() WHERE id=%s",
            (taken, available, slot['id'])
        )

    conn.commit()
    cur.close()
    conn.close()


def ensure_enrollment_reports_table():
    """Creates the full-detail enrollment report table visible in phpMyAdmin."""
    conn = db_connect()
    cur = conn.cursor()

    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {ENROLLMENT_REPORTS_TABLE} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id VARCHAR(20) NOT NULL UNIQUE,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            full_name VARCHAR(220),
            email VARCHAR(150),
            contact_number VARCHAR(50),
            grade_level VARCHAR(20),
            strand VARCHAR(50),
            section VARCHAR(50),
            schedule VARCHAR(50),
            form_137 VARCHAR(20),
            form_138 VARCHAR(20),
            birth_certificate VARCHAR(20),
            status VARCHAR(30),
            payment_status VARCHAR(30),
            registrar_db_id INT NULL,
            registrar_account VARCHAR(50),
            registrar_name VARCHAR(150),
            enrolled_at DATETIME NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_enrollment_reports_strand (strand),
            INDEX idx_enrollment_reports_registrar (registrar_db_id)
        ) ENGINE=InnoDB
    """)

    for col, definition in [
        ("first_name", "VARCHAR(100)"),
        ("last_name", "VARCHAR(100)"),
        ("full_name", "VARCHAR(220)"),
        ("email", "VARCHAR(150)"),
        ("contact_number", "VARCHAR(50)"),
        ("grade_level", "VARCHAR(20)"),
        ("strand", "VARCHAR(50)"),
        ("section", "VARCHAR(50)"),
        ("schedule", "VARCHAR(50)"),
        ("form_137", "VARCHAR(20)"),
        ("form_138", "VARCHAR(20)"),
        ("birth_certificate", "VARCHAR(20)"),
        ("status", "VARCHAR(30)"),
        ("payment_status", "VARCHAR(30)"),
        ("registrar_db_id", "INT NULL"),
        ("registrar_account", "VARCHAR(50)"),
        ("registrar_name", "VARCHAR(150)"),
        ("enrolled_at", "DATETIME NULL"),
        ("updated_at", "DATETIME DEFAULT CURRENT_TIMESTAMP"),
    ]:
        if not column_exists(ENROLLMENT_REPORTS_TABLE, col):
            cur.execute(f"ALTER TABLE {ENROLLMENT_REPORTS_TABLE} ADD COLUMN {col} {definition}")

    conn.commit()
    cur.close()
    conn.close()

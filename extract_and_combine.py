import csv
import os
import shutil
import sqlite3
import sys
import zipfile

connection = sqlite3.connect("voiceedge_cdr.sqlite3")


def bp():
    pass


def init_db():
    cursor = connection.cursor()
    with open("initdb.sql", "r") as initsql:
        sql = initsql.read()
        cursor.executescript(sql)


def close_db():
    connection.close()


def unzip_without_overwrite(src_path, dst_dir):
    with zipfile.ZipFile(src_path, "r") as zf:
        members = zf.infolist()
        for idx, member in enumerate(members):
            print(f"[{idx+1}/{len(members)}] {member.filename}")
            file_path = os.path.join(dst_dir, member.filename)
            file_exists = os.path.exists(file_path)
            print(f"{file_path} exists: {file_exists}")
            if not file_exists:
                zf.extract(member, dst_dir)
        print()


def insert_row(row):
    insert_sql = "INSERT INTO call_detail_record (account, btn, from_number, " \
                 "from_place, dialed_number, to_number, to_place, pbx_id, " \
                 "account_code, date_and_time, type_of_call, cdr_type, " \
                 "duration, charge, rate_center, da_ind, oa_ind, " \
                 "tf_payphone_indr, land_mobile_indr) VALUES (?, ?, ?, ?, ?, " \
                 "?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

    cursor = connection.cursor()
    cursor.execute("begin")
    try:
        cursor.execute(
            insert_sql,
            tuple(row)
        )
        cursor.execute("commit")
    except sqlite3.Error as e:
        print(f"failed to add row\n{e}")
        cursor.execute("rollback")


def main():
    init_db()

    processed_dir = os.path.join(os.getcwd(), "processed")
    if not os.path.exists(processed_dir):
        os.mkdir(processed_dir)

    zip_files = [x for x in os.listdir() if x.endswith(".zip")]
    for idx, zipFile in enumerate(zip_files):
        print(f"[{idx+1}/{len(zip_files)}] Unzipping {zipFile}")
        unzip_without_overwrite(
            os.path.join(os.getcwd(), zipFile),
            os.path.join(os.getcwd(), "extracted")
        )
        shutil.move(zipFile, processed_dir)
    csv_files = [os.path.join(os.getcwd(), "extracted", x)
                 for x in os.listdir(os.path.join(os.getcwd(), "extracted"))
                 if x.endswith(".csv")]
    for csvFile in csv_files:
        print(csvFile)
        with open(csvFile, "r") as in_file:
            reader = csv.reader(in_file)
            try:
                for row in reader:
                    if reader.line_num == 1:
                        continue
                    print(row)
                    insert_row(row)
                    bp()
            except csv.Error as e:
                sys.exit("file {}, line {}: {}"
                         .format(in_file, reader.line_num, e))
        shutil.move(csvFile, processed_dir)


if __name__ == "__main__":
    main()

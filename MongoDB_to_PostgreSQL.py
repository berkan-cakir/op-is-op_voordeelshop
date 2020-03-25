import psycopg2
from pymongo import MongoClient
from foreign_key_links import *
import bson
import csv
import os

cnx = psycopg2.connect("dbname=huwebshop user=postgres password=postgres")  # TODO: edit this.
cursor = cnx.cursor()

limit = -1
client = MongoClient('localhost', 27017)
db = client["huwebshop"]


def get_values(normalized, collection, values, get_fk):
    counter = 0
    normalized_list = []
    upload_values = []
    for entry in collection.find():
        upload = []
        for value in values:
            if value == "x":
                upload = [counter]
            elif "-" in value:
                array_structure = value.split("-")
                array_value = entry
                try:
                    for sep in array_structure:
                        array_value = array_value[sep]
                except KeyError:
                    array_value = None
                upload.append(array_value)
            elif value == "?":
                upload.append(get_fk(entry))
            else:
                if value in entry:
                    if type(entry[value]) == bson.objectid.ObjectId:
                        upload.append(str(entry[value]))
                    else:
                        upload.append(entry[value])
                else:
                    upload.append(None)

        if not [i for i in upload if i in normalized_list] and normalized or not normalized:
            upload_values.append(tuple(upload))
            normalized_list.extend(upload)
            counter += 1

        if counter == limit and not normalized and limit != -1:
            break

    return upload_values


def get_path(file_name):
    # Getting the path to save the file
    script_dir = os.path.dirname(__file__)
    rel_path = f"excel_files/{file_name}.csv"
    abs_file_path = os.path.join(script_dir, rel_path)
    return abs_file_path


def create_csv_file(table_name, upload_values, headers):
    # Writing the upload values to a csv file.
    print(f"Creating the {table_name} database contents...")
    with open(get_path(table_name), 'w', newline='') as csvout:
        writer = csv.DictWriter(csvout, fieldnames=headers)
        writer.writeheader()
        for value in upload_values:
            writer.writerow({'_id': value[0], 'brand': value[1]})
    print(f"Finished creating and uploading the {table_name} database contents.")


def create_table(normalized, table_name, db_name, values, headers, get_fk=None):
    collection = db[db_name]
    cursor.execute(f"DELETE FROM {table_name};")

    upload_values = get_values(normalized, collection, values, get_fk)
    create_csv_file(table_name, upload_values, headers)


if __name__ == "__main__":
    # init()
    # create_table(True, "brand", "products", ["x", "brand"], ["_id", "brand"])
    # create_table(True, "category", "products", ["x", "category"], ["_id", "category"])
    # create_table(True, "sub_category", "products", ["x", "sub_category"], ["_id", "sub_category"])
    # create_table(True, "sub_sub_category", "products", ["x", "category"], ["_id", "sub_sub_category"])
    # create_table(True, "color", "products", ["x", "color"], ["_id", "color"])
    # create_table(True, "gender", "products", ["x", "gender"], ["_id", "gender"])
    # create_table(False, "profiles", "profiles", ["_id", "recommendations-segment", "order-count"], ["_id", "recommendation_segment", "order_count"])
    # create_table(False, "sessions", "sessions", ["has_sale", "user_agent-device-family", "user_agent-device-brand", "user_agent-os-familiy", "?"], ["sessions_id", "has_sale", "device_family", "device_brand", "os", "profid"], link_profile_session)
    cursor.close()
    cnx.close()
from utils.mongo import hospitals_collection


def get_hospitals_for_staff(hospital_name):
    return list(hospitals_collection().find({"name": hospital_name}, {"_id": 0}))


def update_hospital_capacity(hospital_name, beds_available, icu_available, ventilators_available):
    result = hospitals_collection().update_one(
        {"name": hospital_name},
        {"$set": {
            "beds_available": int(beds_available),
            "icu_available": int(icu_available),
            "ventilators_available": int(ventilators_available),
        }},
    )
    return result.modified_count > 0 or result.matched_count > 0


def get_hospital_capacity(hospital_name):
    return hospitals_collection().find_one(
        {"name": hospital_name},
        {"_id": 0, "name": 1, "beds_available": 1, "icu_available": 1,
         "ventilators_available": 1, "beds_total": 1},
    )

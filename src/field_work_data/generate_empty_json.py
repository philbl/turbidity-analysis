from pathlib import Path
import json
import fire


adcp_turbidity_dict = {
    "geo_coordinates": {
            "lat": None, "lon": None
        },
    "time": ""
}


measurement_dict = {
    "geo_coordinates": {
            "lat": None, "lon": None
        },
    "time": "",
    "notes": "",
    "depth": None,
    "measures": []
}


def generate_measurements_list_dict(number_of_spatial_turbidty_measures):
    return [measurement_dict for i in range(number_of_spatial_turbidty_measures)]


def generate_data_dict(number_of_spatial_turbidty_measures):
    measurements_list_dict = generate_measurements_list_dict(number_of_spatial_turbidty_measures)
    return {
        "date": "",
        "estuary_name": "",
        "participants": [],
        "notes": "",
        "ADCP": adcp_turbidity_dict,
        "turbidity_probe": adcp_turbidity_dict,
        "spatial_turbidity_measurement": {
            "turbidity_unit": "FNU",
            "depth_unit": "meter",
            "measurements_list": measurements_list_dict
        }
    }


def generate_empty_json(file_path, number_of_spatial_turbidty_measures):
    field_dict = generate_data_dict(number_of_spatial_turbidty_measures)
    if Path(file_path).is_file() is False:
        with open(file_path, "w") as f:
            json.dump(field_dict, f, indent=2)
    else:
        raise ValueError("file exists")



if __name__ == "__main__":
    fire.Fire(generate_empty_json)

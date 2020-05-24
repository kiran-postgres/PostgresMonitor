from flask import jsonify


def format_data(records):
    if "Exception" not in records[0]:
        data = dict()
        data['columns'] = records.pop(0)
        data['records'] = records

        try:
            json_data = jsonify({
                "status": "success",
                "data": data
            })

            return json_data
        except Exception as err:
            json_data = jsonify({
                "status": "failure",
                "data": str(err)
            })

            return json_data
    else:
        # If there is an exception, Return the Exception.
        json_data = jsonify({
            "status": "failure",
            "data": records[0]
        })

        return json_data




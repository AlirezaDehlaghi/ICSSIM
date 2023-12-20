import paho.mqtt.client as paho

def read_mqtt_params(path):
    params = {}

    try:
        with open(path, 'r') as file:
            for line in file:
                if not line.strip():
                    continue

                if line.strip().startswith("#"):
                    continue
                # Split each line into key and value using ':' as the delimiter
                key, value = map(str.strip, line.split(':', 1))
                params[key] = value

    except FileNotFoundError:
        err_msg = 'Error: File not found.'
        raise Exception(err_msg)
    except Exception as e:
        err_msg = 'Error: cannot read from File.' + e.__str__()
        raise Exception(err_msg)

    return params





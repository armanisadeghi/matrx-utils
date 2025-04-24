from matrx_utils.socket.schema.conversions.conversion_functions import convert_broker_data


CUSTOM_CONVERSIONS = {
    "convert_broker_data": lambda value: convert_broker_data(value),
}



def convert_broker_data(broker):
    return {
        **broker,
        "id": broker.get("id", broker.get("name"), broker.get("official_name")),
        "name": broker.get("name", broker.get("official_name")),
        "value": broker.get("value") or broker.get("defaultValue"),
        "ready": True,
    }


class SyncData:
    def __init__(self, **params) -> None:
        self.obj_type: str = params.get("obj_type", "")
        self.obj_data: dict = params.get("obj_data", "")
        self.obj_cmd: str = params.get("obj_cmd", "")

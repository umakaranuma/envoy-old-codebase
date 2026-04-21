class RequestPreprocessor:
    @staticmethod
    def clean_nullable_fields(data: dict, nullable_fields: list):
        for field in nullable_fields:
            if field in data and (data[field] == "" or data[field] is None):
                data[field] = None
        return data

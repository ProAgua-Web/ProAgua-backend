class InvalidReferenceException(ValueError):
    def __init__(self, ref_name, ref_id, message=None):
        self.ref_name = ref_name
        self.ref_id = ref_id

        if message is None:
            message = f"Invalid reference to {ref_name} with ID={ref_id}"
        
        super().__init__(message)
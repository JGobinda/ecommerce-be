def validate_instance_file_name(instance, file_field="file", file_name="file_name"):
    import os
    # checking if file is updated or not, if updated then directory to the file is given by:
    # os.path.split(self.file.name)[0] ==> (<file_directory>, <file_name_with_extension>)
    # if <file_directory> is empty ie. '' then we can replace the new file name received in request.
    # otherwise let the file name as it is.
    if hasattr(instance, file_field) and not os.path.split(getattr(instance, file_field).name)[0]:
        setattr(instance, file_name, getattr(instance, file_field).name)

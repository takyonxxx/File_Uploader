class TemplateBase:
    """
    A class that only accepts kwargs if attributes are pre-defined.
    Automatically binds given kwargs to self
    Usage:
        class NewTemplate(TemplateBase):
            ... define acceptable fields here
    """
    def __init__(self, **kwargs):
        for field_name, field_value in kwargs.items():
            if hasattr(self, field_name):
                _nested_template = getattr(self, field_name)
                if _nested_template and self.__class__.__bases__[0] in _nested_template.__bases__:
                    setattr(self, field_name, _nested_template(**field_value))
                else:
                    setattr(self, field_name, field_value)
            else:
                raise ValueError(
                    f"{self.__class__.__name__} got an "
                    f"unexpected keyword argument: {field_name}"
                )


class ExampleTemplateBase(TemplateBase):
    """
    Only used as an example for nested template definitions
    """
    test_field = None


class FileTemplate(TemplateBase):
    # file_source = None
    file_repository = None
    file_description = None
    file_path = None
    file_dir_path = None
    file_path_length = None
    content = None
    number = None
    metadata = type('FileMetaData', (TemplateBase,), {  # Nested example 1
        "file_name": None,
        "file_size": None,
        "file_source": None,
        "last_access_time": None,
        "create_time": None
    })
    example_field = ExampleTemplateBase  # Nested example 2

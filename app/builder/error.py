class Error(Exception):

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class ExistenceProjectError(Error):
    pass


class ExistenceVirtualBoxError(Error):
    pass


class PackageNotFoundError(Error):
    pass


class ScriptNotFoundError(Error):
    pass


class JsonConfigCopiedError(Error):
    pass


class FileExtesionError(Error):
    pass


class EmptyScriptError(Error):
    pass


class NoFileToUploadError(Error):
    pass


class UploadNameConflictError(Error):
    pass

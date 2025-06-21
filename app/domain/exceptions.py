class DomainException(Exception):
    """Base domain exception."""

    pass


class TaskListNotFoundException(DomainException):
    """Raised when a task list is not found."""

    pass


class TaskNotFoundException(DomainException):
    """Raised when a task is not found."""

    pass


class InvalidTaskStatusException(DomainException):
    """Raised when an invalid task status is provided."""

    pass


class InvalidTaskPriorityException(DomainException):
    """Raised when an invalid task priority is provided."""

    pass


class TaskListNameAlreadyExistsException(DomainException):
    """Raised when a task list name already exists."""

    pass


class TaskTitleAlreadyExistsException(DomainException):
    """Raised when a task title already exists in the same list."""

    pass


class InvalidDueDateException(DomainException):
    """Raised when an invalid due date is provided."""

    pass


class ValidationError(DomainException):
    """Raised when validation fails."""

    pass


# Aliases for backwards compatibility
TaskListNotFoundError = TaskListNotFoundException
TaskNotFoundError = TaskNotFoundException
TaskListAlreadyExistsError = TaskListNameAlreadyExistsException
TaskAlreadyExistsError = TaskTitleAlreadyExistsException

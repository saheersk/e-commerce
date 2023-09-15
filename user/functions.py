

def generate_form_error(form):
    message = ""
    for field in form:
        if field.errors:
            message +=  field.errors
    for err in form.non_field_errors():
        message += str(err)

    return message     
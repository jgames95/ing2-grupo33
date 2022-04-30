import re


def validate(input_value, input_name, **kwargs):
    """
    Valid inputs
    input_value: requerido, contiene el valor del input a analizar
    input_name : requerido, contiene el nombre del input a analizar
    parametros opcionales
        required
        number
        max_length
        min_length
        decimal (acepta negativos)
        integer( acepta negativos)
        natural_number (no acepta negativos)
    """
    if (
        "required" in kwargs
        and kwargs["required"] is True
        and input_value.strip() == ""
    ):
        return "El campo " + input_name + " es requerido"
    if (
        "natural_number" in kwargs
        and kwargs["natural_number"] is True
        and not input_value.isdigit()
    ):
        return "El campo " + input_name + " debe ser un numero natural "

    if "integer" in kwargs and kwargs["integer"] is True:
        try:
            int(input_value)
        except:
            return "El campo " + input_name + " debe ser un numero Entero "

    if "text" in kwargs and kwargs["text"] is True and not input_value.isalpha():
        return "El campo " + input_name + " debe contener solo letras "

    if "max_length" in kwargs and len(input_value) > int(kwargs["max_length"]):
        return (
            "El campo "
            + input_name
            + " debe contener como maximo "
            + kwargs["max_length"]
            + " caracteres"
        )

    if "min_length" in kwargs and len(input_value) < int(kwargs["min_length"]):
        return (
            "El campo "
            + input_name
            + " debe contener como minimo "
            + kwargs["min_length"]
            + " caracteres"
        )

    if "email" in kwargs and kwargs["email"] is True:
        # r=   ^comienza por [\w] cualquier caracter alfanumerico, + requiere
        # al menos 1 aparicion, @ el caracter

        emailRegex = r"(^[\w]+)@([\w]+)" + "." + "([\w]+)"
        match = re.search(emailRegex, input_value)
        if not match:
            return "El campo email no es valido"

    return True

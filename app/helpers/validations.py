import re
import datetime
from datetime import timedelta, date 


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
        decimal (acepta negativos) ??
        integer( acepta negativos)
        natural_number (no acepta negativos)
        text
        email
        coviddate (15 dias de dif)
        date (no puede estar en el futuro)
        futuredate (no puede estar en el pasado)
        appointmentdate (minimo 7 dias antes)
        valid_period (recibe una tupla con dos fechas, fecha1<=fecha2)
        yesterday (la fecha ingresada tiene que ser ayer o anterior)
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

    if "text" in kwargs and (kwargs["text"] is True) and (not (input_value.replace(" ", "")).isalpha()):
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

    if "coviddate" in kwargs and kwargs["coviddate"] is True:
        # date2 - date1 >= 15 dias
        format = "%Y-%m-%d" 
        date1 = datetime.datetime.strptime(input_value["date1"], format).date()
        date2 = datetime.datetime.strptime(input_value["date2"], format).date()
        if (date2 > date1):
            difference = abs(date2 - date1)
            if (difference.days >= 21):
                pass
            else:
                return "Tiene que haber pasado por lo menos 21 dias entre " + input_name
        else:
            return "La fecha de segunda " + input_name + " tiene que ser mayor a la fecha de la primera" + input_name

    if "date" in kwargs and kwargs["date"] is True:
        # date <= date.today
        format = "%Y-%m-%d" 
        date = datetime.datetime.strptime(input_value, format).date()
        if (date <= datetime.date.today()):
            pass
        else:
            return "El valor de " + input_name + " no puede estar en el futuro"

    if "futuredate" in kwargs and kwargs["futuredate"] is True:
        # date > date.today
        format = "%Y-%m-%d" 
        date = datetime.datetime.strptime(input_value, format).date()
        if (date > datetime.date.today()):
            pass
        else:
            return "El valor de " + input_name + " no puede estar en el pasado"

    if "appointmentdate" in kwargs and kwargs["appointmentdate"] is True:
        # appointmentdate - date >= 7 dias
        format = "%Y-%m-%d"
        date = datetime.datetime.strptime(input_value, format).date()
        date2 = datetime.date.today()
        if (date > date2):
            difference = abs(date - date2)
            if (difference.days >= 7):
                pass
            else:
                return "Elija una fecha para la que falten minimo 7 dias"
        else:
            return "La fecha no puede estar en el pasado"
    if "lessthanayear" in kwargs and kwargs["lessthanayear"] is True:
        format = "%Y-%m-%d" 
        date = datetime.datetime.strptime(input_value, format).date()
        difference = abs(datetime.date.today() - date)
        if (date <= datetime.date.today()):
            if (difference.days < 365):
                pass
            else:
                return "Solo ingrese Si, si se aplicó la vacuna hace menos de un año"
        else:
            return "El valor de " + input_name + " no puede estar en el futuro"
    
    if "valid_period" in kwargs and kwargs["valid_period"] is True:
        if (input_value[0]<=input_value[1]):
            pass
        else:
            return "Periodo de tiempo inválido. \n\nLa fecha inicial debe estar antes que la final."
    
    if "yesterday" in kwargs and kwargs["yesterday"] is True:
        yesterday = datetime.datetime.today() - timedelta(days=1)
        format = "%Y-%m-%d"
        date = datetime.datetime.strptime(input_value, format).date()
        if (date<=yesterday.date()):
            pass
        else:
            return "La fecha final debe ser del día de ayer o anterior."

    return True

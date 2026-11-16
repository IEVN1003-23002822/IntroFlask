from flask import Blueprint, jsonify, request
from database import mysql

alumnos_bp = Blueprint(
    'alumnos',
    __name__,
    url_prefix='/api/alumnos'
)

@alumnos_bp.route("/", methods=['GET'])
def lista_alumnos():
    try:
        cursor = mysql.connection.cursor()
        sql = "select * from alumnos"
        cursor.execute(sql)
        datos = cursor.fetchall()
        alumnos = []
        for fila in datos:
            alumno = {
                "matricula": fila[0], 
                "nombre": fila[1], 
                "apaterno": fila[2], 
                "amaterno": fila[3], 
                "correo": fila[4]
            }
            alumnos.append(alumno)
        return jsonify({'alumnos': alumnos, 'mensaje': "lista de alumnos", 'exito': True})
    except Exception as ex:
        return jsonify({'mensaje': f"Error al listar alumnos: {str(ex)}", 'exito': False}), 500

@alumnos_bp.route("/<string:matricula>", methods=['GET'])
def leer_alumno(matricula):
    cursor = None
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM alumnos WHERE matricula = %s", (matricula,))
        fila = cursor.fetchone()
        if fila is None:
            return jsonify({
                'mensaje': 'Alumno no encontrado',
                'exito': False
            }), 404
        
        alumno = {
            "matricula": fila[0],
            "nombre": fila[1],
            "apaterno": fila[2],
            "amaterno": fila[3],
            "correo": fila[4]
        }
        
        return jsonify({
            'alumno': alumno,
            'exito': True
        }), 200
    except Exception as ex:
        return jsonify({
            'mensaje': f'Error al consultar el alumno: {str(ex)}',
            'exito': False
        }), 500
    finally:
        if cursor is not None:
            cursor.close()

@alumnos_bp.route("/", methods=['POST'])
def registrar_alumno():
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        return jsonify({
            'mensaje': 'Se requiere un objeto JSON',
            'exito': False
        }), 400
        
    campos = ['matricula', 'nombre', 'apaterno', 'amaterno', 'correo']
    
    if any(
        campo not in datos
        or not isinstance(datos[campo], str)
        or not datos[campo].strip()
        for campo in campos
    ):
        return jsonify({
            'mensaje': 'Faltan campos obligatorios',
            'exito': False
        }), 400
        
    cursor = None
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO alumnos
                (matricula, nombre, apaterno, amaterno, correo)
                VALUES (%s, %s, %s, %s, %s)
        """, tuple(datos[campo].strip() for campo in campos))

        mysql.connection.commit()

        return jsonify({
            'mensaje': 'Alumno registrado correctamente',
            'exito': True
        }), 201

    except Exception as ex:
        mysql.connection.rollback()
        return jsonify({
            'mensaje': f'Error al registrar el alumno: {str(ex)}',
            'exito': False
        }), 500

    finally:
        if cursor is not None:
            cursor.close()

@alumnos_bp.route("/<string:matricula>", methods=['PUT'])
def modificar_alumno(matricula):
    cursor = None
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM alumnos WHERE matricula = %s", (matricula,))
        alumno = cursor.fetchone()
        if not alumno:
            return jsonify({
                "mensaje": "No existe un alumno con esa matricula"
            }), 404

        datos = request.get_json()
        nombre = datos['nombre']
        apaterno = datos['apaterno']
        amaterno = datos['amaterno']
        correo = datos['correo']

        sql = """
            UPDATE alumnos
            SET nombre=%s,
                apaterno=%s,
                amaterno=%s,
                correo=%s
            WHERE matricula=%s
        """
        cursor.execute(sql, (
            nombre,
            apaterno,
            amaterno,
            correo,
            matricula
        ))
        mysql.connection.commit()
        return jsonify({
            "mensaje": "Alumno modificado correctamente",
            "matricula": matricula
        }), 200

    except Exception as e:
        mysql.connection.rollback()
        return jsonify({
            "mensaje": f"Error al modificar el alumno: {str(e)}",
            "error": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()

@alumnos_bp.route("/<string:matricula>", methods=['DELETE'])
def eliminar_alumno(matricula):
    cursor = None
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT matricula FROM alumnos WHERE matricula = %s",
            (matricula,)
        )

        alumno = cursor.fetchone()
        if not alumno:
            return jsonify({
                "mensaje": "No existe un alumno con esa matricula"
            }), 404

        cursor.execute(
            "DELETE FROM alumnos WHERE matricula = %s",
            (matricula,)
        )

        mysql.connection.commit()
        return jsonify({
            "mensaje": "Alumno eliminado correctamente",
            "matricula": matricula
        }), 200

    except Exception as e:
        mysql.connection.rollback()
        return jsonify({
            "mensaje": f"Error al eliminar el alumno: {str(e)}",
            "error": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()
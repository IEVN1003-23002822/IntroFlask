from flask import Blueprint, jsonify, request
from database import mysql

maestros_bp = Blueprint(
    'maestros',
    __name__,
    url_prefix='/api/maestros'
)
    
@maestros_bp.route("/", methods=['GET'])
def lista_maestros():
    try:
        cursor = mysql.connection.cursor()
        sql = "select * from maestros"
        cursor.execute(sql)
        datos = cursor.fetchall()
        maestros = []
        for fila in datos:
            maestro = {"idmaestro": fila[0], "nombre": fila[1], "apaterno": fila[2], "amaterno": fila[3], "correo": fila[4]}
            maestros.append(maestro)
        return jsonify({'maestros': maestros, 'mensaje': "lista de maestros", 'exito': True})
    except Exception as ex:
        return jsonify({'mensaje': f"Error al listar maestros: {str(ex)}", 'exito': False}), 500

@maestros_bp.route("/<int:idmaestro>", methods=['GET'])
def leer_maestro(idmaestro):
    cursor = None
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("select * FROM maestros WHERE idmaestro = %s", (idmaestro,))
        fila = cursor.fetchone()
        if fila is None:
            return jsonify({
                'mensaje': 'Maestro no encontrado',
                'exito': False
            }), 404
        
        maestro = {
            "idmaestro": fila[0],
            "nombre": fila[1],
            "apaterno": fila[2],
            "amaterno": fila[3],
            "correo": fila[4]
        }
        
        return jsonify({
            'maestro': maestro,
            'exito': True
        }), 200
    except Exception as ex:
        return jsonify({
            'mensaje': f'Error al consultar el maestro: {str(ex)}',
            'exito': False
        }), 500
    finally:
        if cursor is not None:
            cursor.close()

@maestros_bp.route("/", methods=['POST'])
def registrar_maestro():
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        return jsonify({
            'mensaje': 'Se requiere un objeto JSON',
            'exito': False
        }), 400
        
    campos = ['nombre', 'apaterno', 'amaterno', 'correo']
    
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
            INSERT INTO maestros
                (nombre, apaterno, amaterno, correo)
                VALUES (%s, %s, %s, %s)
        """, tuple(datos[campo].strip() for campo in campos))

        mysql.connection.commit()

        return jsonify({
            'mensaje': 'Maestro registrado correctamente',
            'exito': True
        }), 201

    except Exception as ex:
        mysql.connection.rollback()
        return jsonify({
            'mensaje': f'Error al registrar el maestro: {str(ex)}',
            'exito': False
        }), 500

    finally:
        if cursor is not None:
            cursor.close()

@maestros_bp.route("/<int:idmaestro>", methods=['PUT'])
def modificar_maestro(idmaestro):
    cursor = None
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM maestros WHERE idmaestro = %s", (idmaestro,))
        maestro = cursor.fetchone()
        if not maestro:
            return jsonify({
                "mensaje": "No existe un maestro con ese id"
            }), 404

        datos = request.get_json()
        nombre = datos['nombre']
        apaterno = datos['apaterno']
        amaterno = datos['amaterno']
        correo = datos['correo']

        sql = """
            UPDATE maestros
            SET nombre=%s,
                apaterno=%s,
                amaterno=%s,
                correo=%s
            WHERE idmaestro=%s
        """
        cursor.execute(sql, (
            nombre,
            apaterno,
            amaterno,
            correo,
            idmaestro
        ))
        mysql.connection.commit()
        return jsonify({
            "mensaje": "Maestro modificado correctamente",
            "idmaestro": idmaestro
        }), 200

    except Exception as e:
        mysql.connection.rollback()
        return jsonify({
            "mensaje": f"Error al modificar el maestro: {str(e)}",
            "error": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()

@maestros_bp.route("/<int:idmaestro>", methods=['DELETE'])
def eliminar_maestro(idmaestro):
    cursor = None
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT idmaestro FROM maestros WHERE idmaestro = %s",
            (idmaestro,)
        )

        maestro = cursor.fetchone()
        if not maestro:
            return jsonify({
                "mensaje": "No existe un maestro con ese id"
            }), 404

        cursor.execute(
            "DELETE FROM maestros WHERE idmaestro = %s",
            (idmaestro,)
        )

        mysql.connection.commit()
        return jsonify({
            "mensaje": "Maestro eliminado correctamente",
            "idmaestro": idmaestro
        }), 200

    except Exception as e:
        mysql.connection.rollback()
        return jsonify({
            "mensaje": f"Error al eliminar el maestro: {str(e)}",
            "error": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()
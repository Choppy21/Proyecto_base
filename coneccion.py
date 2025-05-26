import tkinter as tk
from tkinter import messagebox
import mysql.connector

# Conexión con la base de datos
conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Choppy21",
    database="sistema"
)
cursor = conexion.cursor()

# ---- Función para cerrar ventana y volver al menú ----
def volver_menu(ventana_actual):
    ventana_actual.destroy()
    ventana_principal.deiconify()

# ---- Pantalla de registro ----
def ventana_registro():
    ventana_principal.withdraw()
    registro = tk.Toplevel()
    registro.title("Registro de Alumno")
    registro.geometry("400x550")
    registro.configure(bg="#2C3E50")

    tk.Label(registro, text="Sistema de Registro", font=("Arial", 25, "bold"), fg="white", bg="#2C3E50").place(relx=0.5, rely=0.10, anchor="center")

    def registrar_alumno():
        nombre = entrada_nombre.get()
        email = entrada_email.get()
        telefono = entrada_telefono.get()
        password = entrada_password.get()
        confirmar_password = entrada_confirmar.get()

        if not nombre or not email or not telefono or not password or not confirmar_password:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        if password != confirmar_password:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return

        cursor.execute("SELECT * FROM usuario WHERE password = %s", (password,))
        if cursor.fetchone():
            messagebox.showerror("Error", "La contraseña ya ha sido utilizada, elige otra")
            return

        try:
            cursor.execute("INSERT INTO alumnos (nombre, email, telefono) VALUES (%s, %s, %s)", 
                           (nombre, email, telefono))
            conexion.commit()
            alumno_id = cursor.lastrowid
            cursor.execute("INSERT INTO usuario (alumno_id, password) VALUES (%s, %s)", 
                           (alumno_id, password))
            conexion.commit()
            messagebox.showinfo("Registro exitoso", f"Tu matrícula es: {alumno_id}")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Hubo un problema: {err}")

    tk.Label(registro, text="Nombre:", font=("Arial", 15), bg="#2C3E50", fg="white").place(relx=0.5, rely=0.20, anchor="center")
    entrada_nombre = tk.Entry(registro, font=("Arial", 15))
    entrada_nombre.place(relx=0.5, rely=0.25, anchor="center")

    tk.Label(registro, text="Email:", font=("Arial", 15), bg="#2C3E50", fg="white").place(relx=0.5, rely=0.32, anchor="center")
    entrada_email = tk.Entry(registro, font=("Arial", 15))
    entrada_email.place(relx=0.5, rely=0.37, anchor="center")

    tk.Label(registro, text="Teléfono:", font=("Arial", 15), bg="#2C3E50", fg="white").place(relx=0.5, rely=0.44, anchor="center")
    entrada_telefono = tk.Entry(registro, font=("Arial", 15))
    entrada_telefono.place(relx=0.5, rely=0.49, anchor="center")

    tk.Label(registro, text="Contraseña:", font=("Arial", 15), bg="#2C3E50", fg="white").place(relx=0.5, rely=0.56, anchor="center")
    entrada_password = tk.Entry(registro, show="*", font=("Arial", 15))
    entrada_password.place(relx=0.5, rely=0.61, anchor="center")

    tk.Label(registro, text="Confirmar Contraseña:", font=("Arial", 15), bg="#2C3E50", fg="white").place(relx=0.5, rely=0.68, anchor="center")
    entrada_confirmar = tk.Entry(registro, show="*", font=("Arial", 15))
    entrada_confirmar.place(relx=0.5, rely=0.73, anchor="center")

    tk.Button(registro, text="Registrar", font=("Arial", 15, "bold"), bg="#E74C3C", fg="white", command=registrar_alumno).place(relx=0.5, rely=0.81, anchor="center")
    tk.Button(registro, text="Volver al Menú", font=("Arial", 15, "bold"), bg="#3498DB", fg="white", command=lambda: volver_menu(registro)).place(relx=0.5, rely=0.90, anchor="center")

# ---- Pantalla de inscripción de materias ----
def ventana_materias(alumno_id):
    materias_window = tk.Toplevel()
    materias_window.title("Gestión de Materias")
    materias_window.geometry("400x500")
    materias_window.configure(bg="#2C3E50")

    tk.Label(materias_window, text="Materias Inscritas", font=("Arial", 25, "bold"), fg="white", bg="#2C3E50").place(relx=0.5, rely=0.05, anchor="center")

    listbox_inscritas = tk.Listbox(materias_window, selectmode=tk.SINGLE, font=("Arial", 12), bg="#ECF0F1", fg="black")
    listbox_inscritas.place(relx=0.5, rely=0.25, anchor="center", width=250, height=120)

    tk.Label(materias_window, text="Selecciona materias nuevas", font=("Arial", 15, "bold"), fg="white", bg="#2C3E50").place(relx=0.5, rely=0.5, anchor="center")
    listbox_materias = tk.Listbox(materias_window, selectmode=tk.MULTIPLE, font=("Arial", 12), bg="#ECF0F1", fg="black")
    listbox_materias.place(relx=0.5, rely=0.65, anchor="center", width=250, height=120)

    def actualizar_materias_inscritas():
        listbox_inscritas.delete(0, tk.END)
        cursor.execute("""
            SELECT m.id_m, m.nombre 
            FROM materia m
            INNER JOIN inscripcion i ON m.id_m = i.materia_id
            WHERE i.alumno_id = %s
        """, (alumno_id,))
        global materias_inscritas
        materias_inscritas = cursor.fetchall()
        for id_m, nombre in materias_inscritas:
            listbox_inscritas.insert(tk.END, f"{id_m} - {nombre}")

    def cargar_materias_disponibles():
        """ Carga todas las materias disponibles que el alumno aún no ha inscrito. """
        listbox_materias.delete(0, tk.END)
        cursor.execute("""
            SELECT id_m, nombre FROM materia
            WHERE id_m NOT IN (
                SELECT materia_id FROM inscripcion WHERE alumno_id = %s
            )
        """, (alumno_id,))
        global materias_disponibles
        materias_disponibles = cursor.fetchall()
        for id_m, nombre in materias_disponibles:
            listbox_materias.insert(tk.END, f"{id_m} - {nombre}")

    def guardar_inscripcion():
        seleccionadas_indices = listbox_materias.curselection()
        seleccionadas = [materias_disponibles[i][0] for i in seleccionadas_indices]

        if not seleccionadas:
            messagebox.showerror("Error", "Debes seleccionar al menos una materia")
            return

        try:
            for materia_id in seleccionadas:
                cursor.execute("INSERT INTO inscripcion (alumno_id, materia_id) VALUES (%s, %s)", (alumno_id, materia_id))
                conexion.commit()

            messagebox.showinfo("Inscripción exitosa", "Tus materias han sido registradas")
            actualizar_materias_inscritas()
            cargar_materias_disponibles()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Hubo un problema: {err}")

    def dar_baja_materia():
        seleccion = listbox_inscritas.curselection()
        if not seleccion:
            messagebox.showerror("Error", "Debes seleccionar una materia para dar de baja")
            return

        id_materia = materias_inscritas[seleccion[0]][0]

        try:
            cursor.execute("DELETE FROM inscripcion WHERE alumno_id = %s AND materia_id = %s", (alumno_id, id_materia))
            conexion.commit()
            messagebox.showinfo("Baja exitosa", f"Has dado de baja la materia con ID {id_materia}")
            actualizar_materias_inscritas()
            cargar_materias_disponibles()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Hubo un problema: {err}")

    tk.Button(materias_window, text="Inscribirse en nuevas materias", font=("Arial", 15, "bold"), bg="#27AE60", fg="white", command=guardar_inscripcion).place(relx=0.5, rely=0.85, anchor="center")
    tk.Button(materias_window, text="Dar de baja materia", font=("Arial", 15, "bold"), bg="#E74C3C", fg="white", command=dar_baja_materia).place(relx=0.5, rely=0.43, anchor="center")
    tk.Button(materias_window, text="Volver al Menú", font=("Arial", 15, "bold"), bg="#3498DB", fg="white", command=lambda: volver_menu(materias_window)).place(relx=0.5, rely=0.95, anchor="center")

    actualizar_materias_inscritas()
    cargar_materias_disponibles()

# ---- Pantalla de inicio de sesión ----
def ventana_login():
    ventana_principal.withdraw()
    login = tk.Toplevel()
    login.title("Inicio de Sesión")
    login.geometry("400x400")
    login.configure(bg="#2C3E50")

    tk.Label(login, text="Inicio de Sesión", font=("Arial", 25, "bold"), fg="white", bg="#2C3E50").place(relx=0.5, rely=0.15, anchor="center")

    def iniciar_sesion():
        alumno_id = entrada_id.get()
        password = entrada_password.get()

        if not alumno_id or not password:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
        
        director_id = "170706"
        director_password = "pep_ino68"

        if alumno_id == director_id and password == director_password:
            messagebox.showinfo("Acceso concedido", "Bienvenido Director")
            login.destroy()
            ventana_director()
            return

        consulta = "SELECT * FROM usuario WHERE alumno_id = %s AND password = %s"
        cursor.execute(consulta, (alumno_id, password))
        resultado = cursor.fetchone()

        if resultado:
            messagebox.showinfo("Acceso concedido", "Bienvenido al sistema")
            login.destroy()
            ventana_materias(int(alumno_id))
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")

    tk.Label(login, text="Matrícula:", font=("Arial", 15), bg="#2C3E50", fg="white").place(relx=0.5, rely=0.30, anchor="center")
    entrada_id = tk.Entry(login, font=("Arial", 15))
    entrada_id.place(relx=0.5, rely=0.40, anchor="center")

    tk.Label(login, text="Contraseña:", font=("Arial", 15), bg="#2C3E50", fg="white").place(relx=0.5, rely=0.50, anchor="center")
    entrada_password = tk.Entry(login, show="*", font=("Arial", 15))
    entrada_password.place(relx=0.5, rely=0.60, anchor="center")

    tk.Button(login, text="Ingresar", font=("Arial", 15, "bold"), bg="#E74C3C", fg="white", command=iniciar_sesion).place(relx=0.5, rely=0.75, anchor="center")
    tk.Button(login, text="Volver al Menú", font=("Arial", 12, "bold"), bg="#3498DB", fg="white", command=lambda: volver_menu(login)).place(relx=0.5, rely=0.9, anchor="center")

# ---- Panel de administración del director ----
def ventana_director():
    director_window = tk.Toplevel()
    director_window.title("Panel del Director")
    director_window.geometry("800x500")
    director_window.configure(bg="#2C3E50")

    tk.Label(director_window, text="Panel de Administración", font=("Arial", 25, "bold"), fg="white", bg="#2C3E50").place(relx=0.5, rely=0.10, anchor="center")
    tk.Button(director_window, text="Volver al Menú", font=("Arial", 15, "bold"), bg="#3498DB", fg="white", command=lambda: volver_menu(director_window)).place(relx=0.5, rely=0.85, anchor="center")

    tk.Label(director_window, text="Materias Registradas", font=("Arial", 15, "bold"), fg="white", bg="#2C3E50").place(relx=0.2, rely=0.15, anchor="center")
    listbox_materias = tk.Listbox(director_window, font=("Arial", 12), bg="#ECF0F1", fg="black")
    listbox_materias.place(relx=0.2, rely=0.4, anchor="center", width=250, height=200)

    tk.Label(director_window, text="Alumnos Inscritos", font=("Arial", 15, "bold"), fg="white", bg="#2C3E50").place(relx=0.8, rely=0.15, anchor="center")
    listbox_alumnos = tk.Listbox(director_window, font=("Arial", 12), bg="#ECF0F1", fg="black")
    listbox_alumnos.place(relx=0.8, rely=0.4, anchor="center", width=250, height=200)

   # ---- Listado de materias y alumnos ----
    def actualizar_listas():
        listbox_materias.delete(0, tk.END)
        cursor.execute("SELECT id_m, nombre FROM materia")
        materias = cursor.fetchall()
        for id_m, nombre in materias:
            listbox_materias.insert(tk.END, f"{id_m} - {nombre}")

        listbox_alumnos.delete(0, tk.END)
        cursor.execute("SELECT id_a, nombre FROM alumnos")
        alumnos = cursor.fetchall()
        for id_a, nombre in alumnos:
            listbox_alumnos.insert(tk.END, f"{id_a} - {nombre}")

    # ---- Agregar Materia ----
    def agregar_materia():
        nombre_materia = entrada_materia.get()
        if nombre_materia:
            cursor.execute("INSERT INTO materia (nombre) VALUES (%s)", (nombre_materia,))
            conexion.commit()
            messagebox.showinfo("Éxito", f"Materia {nombre_materia} agregada")
            actualizar_listas()

    # ---- Eliminar Materia ----
    def eliminar_materia():
        id_materia = entrada_materia.get()
        if id_materia:
            cursor.execute("SELECT * FROM materia WHERE id_m = %s", (id_materia,))
            existe = cursor.fetchone()
            
            if existe:
                try:
                    cursor.execute("DELETE FROM inscripcion WHERE materia_id = %s", (id_materia,))
                    cursor.execute("DELETE FROM materia WHERE id_m = %s", (id_materia,))
                    conexion.commit()

                    messagebox.showinfo("Éxito", f"Materia con ID {id_materia} eliminada")
                    actualizar_listas()
                except mysql.connector.Error as err:
                    messagebox.showerror("Error", f"No se pudo eliminar: {err}")
            else:
                messagebox.showerror("Error", "La materia no existe")

    # ---- Eliminar Alumno ----
    def eliminar_alumno():
        id_alumno = entrada_alumno.get()
        print(f"ID Capturado: {id_alumno}")
        if id_alumno:
            cursor.execute("SELECT * FROM alumnos WHERE id_a = %s", (id_alumno,))
            existe = cursor.fetchone()
            
            if existe:
                try:
                    cursor.execute("DELETE FROM inscripcion WHERE alumno_id = %s", (id_alumno,))
                    cursor.execute("DELETE FROM usuario WHERE alumno_id = %s", (id_alumno,))
                    cursor.execute("DELETE FROM alumnos WHERE id_a = %s", (id_alumno,))
                    conexion.commit()

                    messagebox.showinfo("Éxito", f"Alumno con ID {id_alumno} eliminado")
                    actualizar_listas()
                except mysql.connector.Error as err:
                    messagebox.showerror("Error", f"No se pudo eliminar: {err}")
            else:
                messagebox.showerror("Error", "El alumno no existe")

        else:
            messagebox.showerror("Error", "Debes ingresar un ID")

    tk.Label(director_window, text="Nombre/ID Materia:", font=("Arial", 15), bg="#2C3E50", fg="white").place(relx=0.5, rely=0.2, anchor="center")
    entrada_materia = tk.Entry(director_window, font=("Arial", 15))
    entrada_materia.place(relx=0.5, rely=0.25, anchor="center")

    tk.Button(director_window, text="Agregar Materia", font=("Arial", 15, "bold"), bg="#27AE60", fg="white", command=agregar_materia).place(relx=0.5, rely=0.35, anchor="center")
    tk.Button(director_window, text="Eliminar Materia", font=("Arial", 15, "bold"), bg="#E74C3C", fg="white", command=eliminar_materia).place(relx=0.5, rely=0.45, anchor="center")

    tk.Label(director_window, text="ID Alumno a Eliminar:", font=("Arial", 15), bg="#2C3E50", fg="white").place(relx=0.5, rely=0.60, anchor="center")
    entrada_alumno = tk.Entry(director_window, font=("Arial", 15))
    entrada_alumno.place(relx=0.5, rely=0.65, anchor="center")

    tk.Button(director_window, text="Eliminar Alumno", font=("Arial", 15, "bold"), bg="#E74C3C", fg="white", command=eliminar_alumno).place(relx=0.5, rely=0.75, anchor="center")

    actualizar_listas()

# ---- Menú principal ----
ventana_principal = tk.Tk()
ventana_principal.title("Menú Principal")
ventana_principal.geometry("400x300")
ventana_principal.configure(bg="#2C3E50")

tk.Label(ventana_principal, text="Bienvenido al Sistema", font=("Arial", 25, "bold"), fg="white", bg="#2C3E50").place(relx=0.5, rely=0.2, anchor="center")
tk.Label(ventana_principal, text="Selecciona una de las opciones", font=("Arial", 15, "bold"), fg="white", bg="#2C3E50").place(relx=0.5, rely=0.3, anchor="center")

tk.Button(ventana_principal, text="Registrar Usuario", font=("Arial", 15, "bold"), bg="#3498DB", fg="white", command=ventana_registro).place(relx=0.5, rely=0.48, anchor="center")
tk.Button(ventana_principal, text="Iniciar Sesión", font=("Arial", 15, "bold"), bg="#E74C3C", fg="white", command=ventana_login).place(relx=0.5, rely=0.65, anchor="center")

ventana_principal.mainloop()
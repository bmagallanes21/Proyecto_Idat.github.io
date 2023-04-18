from PyQt5.QtGui import QTextImageFormat, QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem, QMessageBox
from PyQt5.QtPrintSupport import QPrinter
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from PyQt5 import QtWidgets, uic, QtCore
import pyodbc
import pandas as pd
import matplotlib.pyplot as plt
import re

app = QtWidgets.QApplication([])

login = uic.loadUi("Login.ui")
entrar = uic.loadUi("Principal.ui")
error = uic.loadUi("Error.ui")
registro = uic.loadUi("Registro.ui")
exito = uic.loadUi("Exito.ui")
confirmar = uic.loadUi("confirmar.ui")

def conectar_bd():
    server = 'DESKTOP-M7K6180\SQLEXPRESS'
    database = 'BD_LOGIN'
    username = 'prueba'
    password = '123'
    cnxn = pyodbc.connect(f'Driver=SQL Server;Server={server};Database={database};UID={username};PWD={password}')
    return cnxn

def gui_login():
    name = login.lineEdit.text()
    password_input = login.lineEdit_2.text()
    if len(name)==0 or len(password_input)==0:
        login.label_5.show()
        login.label_5.setText("Ingrese todos los datos")
        QTimer.singleShot(3000, login.label_5.hide)
    else:  
        cnxn = conectar_bd()
        cursor = cnxn.cursor()
        cursor.execute("SELECT usuario, contrasena FROM usuarios WHERE usuario=? AND contrasena=?", (name, password_input))
        row = cursor.fetchone()
        if row is not None:
            entrar.show()
        else:
            error.show()
    login.lineEdit.setText("")
    login.lineEdit_2.setText("")

def agregar_producto():
    nombre = entrar.line_NOMBRE.text()
    descripcion = entrar.plainTextEdit.toPlainText()  
    marca = entrar.line_MARCA.text()
    modelo = entrar.line_MODELO.text()
    stock = entrar.line_STOCK.text()
    categoria = entrar.comboBox.currentText()
    codigo = entrar.line_COD.text()
    if not nombre or not descripcion or not marca or not modelo or not stock or not categoria or not codigo:
        entrar.label_AGREGAR.show()
        entrar.label_AGREGAR.setText("Por favor, ingrese todos los datos")
        QTimer.singleShot(5000, lambda: entrar.label_AGREGAR.setText(""))
        return

    try:
        stock_int = int(stock)
        if stock_int < 0:
            entrar.label_AGREGAR.show()
            entrar.label_AGREGAR.setText("Ingrese un número válido")
            QTimer.singleShot(5000, lambda: entrar.label_AGREGAR.setText(""))
            return
    except ValueError:
        entrar.label_AGREGAR.show()
        entrar.label_AGREGAR.setText("Ingrese un número válido")
        QTimer.singleShot(5000, lambda: entrar.label_AGREGAR.setText(""))
        return
    cnxn = conectar_bd()
    cursor = cnxn.cursor()
    cursor.execute("INSERT INTO productos (COD_PRODUCTOS, NOMBRE, DESCRIPCION, MARCA, MODELO, STOCK, CATEGORIA) VALUES (?, ?, ?, ?, ?, ?, ?)", (codigo, nombre, descripcion, marca, modelo, stock, categoria))
    cnxn.commit()
    QMessageBox.information(entrar, "Información", "Producto agregado exitosamente.") 
    entrar.line_NOMBRE.setText("")
    entrar.plainTextEdit.clear()
    entrar.line_MARCA.setText("")
    entrar.line_MODELO.setText("")
    entrar.line_COD.setText("")
    entrar.line_STOCK.setText("")
    entrar.comboBox.setCurrentIndex(0)

def cargar_codigo_producto():
    cnxn = conectar_bd()
    categoria = entrar.comboBox.currentText()
    query = f"SELECT MAX(COD_PRODUCTOS) FROM productos WHERE CATEGORIA = '{categoria}'"
    cursor = cnxn.cursor()
    cursor.execute(query)
    codigo = cursor.fetchone()[0]
    if not codigo:
        codigo = categoria + str(codigo)

    entrar.line_COD.setText(str(codigo))
entrar.comboBox.currentIndexChanged.connect(cargar_codigo_producto)

def cargar_datos_productos():
    cnxn = conectar_bd()
    query = 'SELECT COD_PRODUCTOS, NOMBRE, DESCRIPCION, MARCA, MODELO, STOCK, CATEGORIA FROM dbo.productos'
    cursor = cnxn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    table = entrar.table_PRODUCTO
    table.setColumnCount(len(data[0]))
    table.setRowCount(len(data))
    for i, row in enumerate(data):
        for j, item in enumerate(row):
            table.setItem(i, j, QtWidgets.QTableWidgetItem(str(item)))

def descargar_reporte():
    cnxn = conectar_bd()
    cursor = cnxn.cursor()
    cursor.execute('SELECT * FROM productos')
    data = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    df = pd.DataFrame.from_records(data, columns=columns)
    file_path, _ = QFileDialog.getSaveFileName(entrar, "Guardar archivo", "", "CSV (*.csv);;Excel (*.xlsx);;PDF (*.pdf)")

    if file_path:
        if file_path.endswith('.csv'):
            df.to_csv(file_path, index=False)
        elif file_path.endswith('.xlsx'):
            df.to_excel(file_path, index=False)
        elif file_path.endswith('.pdf'):
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            styles = getSampleStyleSheet()
            table_data = [columns] + [list(row) for row in data]
            table = Table(table_data, colWidths=[inch]*len(columns))
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,0), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 14),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                ('TEXTCOLOR', (0,1), (-1,-1), colors.black),
                ('ALIGN', (0,1), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,1), (-1,-1), 12),
                ('TOPPADDING', (0,1), (-1,-1), 12),
                ('BOTTOMPADDING', (0,1), (-1,-1), 12),
                ('GRID', (0,0), (-1,-1), 1, colors.black)
            ]))
            doc.build([table])
entrar.Button_REPORTE.clicked.connect(descargar_reporte)

def crear_grafica():
    cnxn = conectar_bd()
    cursor = cnxn.cursor()
    cursor.execute("SELECT CATEGORIA, SUM(STOCK) FROM productos GROUP BY CATEGORIA")
    datos = cursor.fetchall()
    categorias = [fila[0] for fila in datos]
    stock = [fila[1] for fila in datos]
    fig, ax = plt.subplots()
    ax.bar(categorias, stock)
    ax.set_xticklabels(categorias, rotation=45, ha='right')
    ax.set_xlabel('Categorías')
    ax.set_ylabel('Stock')
    ax.set_title('Stock por categoría')
    for i, v in enumerate(stock):
        ax.text(i, v, str(v), color='black', fontweight='bold', ha='center')
    return fig

def mostrar_informe():
    entrar.textBrowser_informe.clear()
    fig =crear_grafica()
    canvas = plt.gcf().canvas
    canvas.draw()
    pil_image = canvas.get_renderer().tostring_rgb()
    qimage = QImage(pil_image, canvas.get_width_height()[0], canvas.get_width_height()[1], QImage.Format_RGB888)
    pixmap = QPixmap.fromImage(qimage)
    pixmap = pixmap.scaled(entrar.textBrowser_informe.size(), Qt.KeepAspectRatio)
    fig.tight_layout()
    fig.savefig('grafica.png', dpi=100)
    cursor = entrar.textBrowser_informe.textCursor()
    formato_imagen = QTextImageFormat()
    formato_imagen.setName('grafica.png')
    cursor.insertImage(formato_imagen)
    QMessageBox.information(entrar, "Información", "El grafico se ha cargado correctamente.") 
entrar.Button_informe.clicked.connect(mostrar_informe)

def mostrar_tabla():
    cnxn = conectar_bd()
    cursor = cnxn.cursor()
    cursor.execute("SELECT * FROM productos")
    datos = cursor.fetchall()
    encabezados = [desc[0] for desc in cursor.description]
    tabla_html = '<table border="1">'
    tabla_html += '<tr>'
    for encabezado in encabezados:
        tabla_html += f'<th>{encabezado}</th>'
    tabla_html += '</tr>'
    for fila in datos:
        tabla_html += '<tr>'
        for valor in fila:
            tabla_html += f'<td>{valor}</td>'
        tabla_html += '</tr>'
    tabla_html += '</table>'
    entrar.textBrowser_informe.setHtml(tabla_html)   
    QMessageBox.information(entrar, "Información", "La tabla se ha cargado correctamente.") 
entrar.Button_tabla.clicked.connect(mostrar_tabla)

def guardar_archivo():
    dialogo = QFileDialog()
    dialogo.setDefaultSuffix('pdf')
    dialogo.setAcceptMode(QFileDialog.AcceptSave)
    dialogo.setNameFilter('PDF files (*.pdf);;PNG files (*.png)')
    if dialogo.exec_() == QFileDialog.Accepted:
        ruta_archivo = dialogo.selectedFiles()[0]
        formato = dialogo.selectedNameFilter()
        if formato == 'PDF files (*.pdf)':
            if not ruta_archivo.endswith('.pdf'):
                ruta_archivo += '.pdf'
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(ruta_archivo)
            entrar.textBrowser_informe.print_(printer)
            QMessageBox.information(entrar, "Guardado", "El archivo de PDF ha sido guardado correctamente.")
        elif formato == 'PNG files (*.png)':
            if not ruta_archivo.endswith('.png'):
                ruta_archivo += '.png'
            canvas = plt.gcf().canvas
            canvas.draw()
            pil_image = canvas.get_renderer().tostring_rgb()
            qimage = QImage(pil_image, canvas.get_width_height()[0], canvas.get_width_height()[1], QImage.Format_RGB888)
            qimage.save(ruta_archivo)
            QMessageBox.information(entrar, "Guardado", "El archivo de imagen ha sido guardado correctamente.")
entrar.Button_des.clicked.connect(guardar_archivo)

def actualizar_producto():
    campo = entrar.comboBox_ACTUALIZAR.currentText()
    valor = entrar.lineEdit_ACTUALIZAR.text()

    if entrar.table_ACTUALIZAR.currentRow() < 0:
        entrar.label_ACTUALIZAR_3.setText("Seleccione un producto para actualizar")
        QTimer.singleShot(3000, lambda: entrar.label_ACTUALIZAR_3.setText(""))
        return

    if not valor:
        entrar.label_ACTUALIZAR_2.setText("Ingrese un valor")
        QTimer.singleShot(3000, lambda: entrar.label_ACTUALIZAR_2.setText(""))
        return

    if re.match("^-[0-9]+$", valor):
        entrar.label_ACTUALIZAR_4.setText("Ingrese un número válido")
        QTimer.singleShot(3000, lambda: entrar.label_ACTUALIZAR_4.setText(""))
        return
    
    if campo == "STOCK":
        if not valor.isdigit():
            entrar.label_ACTUALIZAR_4.setText("Ingrese un valor numérico")
            QTimer.singleShot(3000, lambda: entrar.label_ACTUALIZAR_4.setText(""))
            return
        
    id_producto = entrar.table_ACTUALIZAR.item(entrar.table_ACTUALIZAR.currentRow(), 0).text()
    cnxn = conectar_bd()
    cursor = cnxn.cursor()
    cursor.execute(f"UPDATE productos SET {campo} = ? WHERE COD_PRODUCTOS = ?", (valor, id_producto))
    cnxn.commit()
    QMessageBox.information(entrar, "Información", "Producto actualizado correctamente.") 
    entrar.comboBox_ACTUALIZAR.setCurrentIndex(0)
    entrar.lineEdit_ACTUALIZAR.setText("")
entrar.Button_AGREGAR_2.clicked.connect(actualizar_producto)

def refrescar_tabla():
    cnxn = conectar_bd()
    query = 'SELECT COD_PRODUCTOS, NOMBRE, DESCRIPCION, MARCA, MODELO, STOCK, CATEGORIA FROM dbo.productos'
    cursor = cnxn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    table = entrar.table_PRODUCTO
    table.clearContents()
    table.setRowCount(len(data))
    for i, row in enumerate(data):
        for j, item in enumerate(row):
            table.setItem(i, j, QtWidgets.QTableWidgetItem(str(item)))

def mostrar_placa_madre():
    cnxn = conectar_bd()
    query = "SELECT COD_PRODUCTOS, NOMBRE, DESCRIPCION, MARCA, MODELO, STOCK, CATEGORIA FROM dbo.productos WHERE CATEGORIA = 'placa madre'"
    cursor = cnxn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    table = entrar.table_PRODUCTO
    table.setColumnCount(len(data[0]))
    table.setRowCount(len(data))
    for i, row in enumerate(data):
        for j, item in enumerate(row):
            table.setItem(i, j, QtWidgets.QTableWidgetItem(str(item)))
    entrar.tabWidget.setCurrentWidget(entrar.tab_PRODUCTOS)
entrar.boton_categoria_1.clicked.connect(mostrar_placa_madre)

def mostrar_memoria_ram():
    cnxn = conectar_bd()
    query = "SELECT COD_PRODUCTOS, NOMBRE, DESCRIPCION, MARCA, MODELO, STOCK, CATEGORIA FROM dbo.productos WHERE CATEGORIA = 'memoria ram'"
    cursor = cnxn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    table = entrar.table_PRODUCTO
    table.setColumnCount(len(data[0]))
    table.setRowCount(len(data))
    for i, row in enumerate(data):
        for j, item in enumerate(row):
            table.setItem(i, j, QtWidgets.QTableWidgetItem(str(item)))
    entrar.tabWidget.setCurrentWidget(entrar.tab_PRODUCTOS)
entrar.boton_categoria_2.clicked.connect(mostrar_memoria_ram)

def mostrar_tarjeta_video():
    cnxn = conectar_bd()
    query = "SELECT COD_PRODUCTOS, NOMBRE, DESCRIPCION, MARCA, MODELO, STOCK, CATEGORIA FROM dbo.productos WHERE CATEGORIA = 'tarjeta de video'"
    cursor = cnxn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    table = entrar.table_PRODUCTO
    table.setColumnCount(len(data[0]))
    table.setRowCount(len(data))
    for i, row in enumerate(data):
        for j, item in enumerate(row):
            table.setItem(i, j, QtWidgets.QTableWidgetItem(str(item)))
    entrar.tabWidget.setCurrentWidget(entrar.tab_PRODUCTOS)
entrar.boton_categoria_3.clicked.connect(mostrar_tarjeta_video)

def mostrar_procesadores():
    cnxn = conectar_bd()
    query = "SELECT COD_PRODUCTOS, NOMBRE, DESCRIPCION, MARCA, MODELO, STOCK, CATEGORIA FROM dbo.productos WHERE CATEGORIA = 'procesadores'"
    cursor = cnxn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    table = entrar.table_PRODUCTO
    table.setColumnCount(len(data[0]))
    table.setRowCount(len(data))
    for i, row in enumerate(data):
        for j, item in enumerate(row):
            table.setItem(i, j, QtWidgets.QTableWidgetItem(str(item)))
    entrar.tabWidget.setCurrentWidget(entrar.tab_PRODUCTOS)
entrar.boton_categoria_4.clicked.connect(mostrar_procesadores)

def mostrar_Almacenamiento():
    cnxn = conectar_bd()
    query = "SELECT COD_PRODUCTOS, NOMBRE, DESCRIPCION, MARCA, MODELO, STOCK, CATEGORIA FROM dbo.productos WHERE CATEGORIA = 'Almacenamiento'"
    cursor = cnxn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    table = entrar.table_PRODUCTO
    table.setColumnCount(len(data[0]))
    table.setRowCount(len(data))
    for i, row in enumerate(data):
        for j, item in enumerate(row):
            table.setItem(i, j, QtWidgets.QTableWidgetItem(str(item)))
    entrar.tabWidget.setCurrentWidget(entrar.tab_PRODUCTOS)
entrar.boton_categoria_5.clicked.connect(mostrar_Almacenamiento)

def mostrar_Refrigeración():
    cnxn = conectar_bd()
    query = "SELECT COD_PRODUCTOS, NOMBRE, DESCRIPCION, MARCA, MODELO, STOCK, CATEGORIA FROM dbo.productos WHERE CATEGORIA = 'Refrigeración'"
    cursor = cnxn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    table = entrar.table_PRODUCTO
    table.setColumnCount(len(data[0]))
    table.setRowCount(len(data))
    for i, row in enumerate(data):
        for j, item in enumerate(row):
            table.setItem(i, j, QtWidgets.QTableWidgetItem(str(item)))
    entrar.tabWidget.setCurrentWidget(entrar.tab_PRODUCTOS)
entrar.boton_categoria_6.clicked.connect(mostrar_Refrigeración)

def mostrar_Case():
    cnxn = conectar_bd()
    query = "SELECT COD_PRODUCTOS, NOMBRE, DESCRIPCION, MARCA, MODELO, STOCK, CATEGORIA FROM dbo.productos WHERE CATEGORIA = 'Case'"
    cursor = cnxn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    table = entrar.table_PRODUCTO
    table.setColumnCount(len(data[0]))
    table.setRowCount(len(data))
    for i, row in enumerate(data):
        for j, item in enumerate(row):
            table.setItem(i, j, QtWidgets.QTableWidgetItem(str(item)))
    entrar.tabWidget.setCurrentWidget(entrar.tab_PRODUCTOS)
entrar.boton_categoria_7.clicked.connect(mostrar_Case)

def mostrar_Periféricos():
    cnxn = conectar_bd()
    query = "SELECT COD_PRODUCTOS, NOMBRE, DESCRIPCION, MARCA, MODELO, STOCK, CATEGORIA FROM dbo.productos WHERE CATEGORIA = 'Periféricos'"
    cursor = cnxn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    table = entrar.table_PRODUCTO
    table.setColumnCount(len(data[0]))
    table.setRowCount(len(data))
    for i, row in enumerate(data):
        for j, item in enumerate(row):
            table.setItem(i, j, QtWidgets.QTableWidgetItem(str(item)))
    entrar.tabWidget.setCurrentWidget(entrar.tab_PRODUCTOS)
entrar.boton_categoria_8.clicked.connect(mostrar_Periféricos)

def bloquear_checkbox():
    if entrar.check_MN.isChecked():
        entrar.check_NM.setDisabled(True)
    elif entrar.check_NM.isChecked():
        entrar.check_MN.setDisabled(True)
    else:
        entrar.check_MN.setDisabled(False)
        entrar.check_NM.setDisabled(False)

def mostrar_productos():
    categoria = entrar.comboBox_BUSCAR.currentText()
    cnxn = conectar_bd()
    cursor = cnxn.cursor()
    if categoria == "Todos los productos":
        if entrar.check_MN.isChecked():
            cursor.execute("SELECT * FROM productos ORDER BY STOCK DESC")
        elif entrar.check_NM.isChecked():
            cursor.execute("SELECT * FROM productos ORDER BY STOCK ASC")
        else:
            cursor.execute("SELECT * FROM productos")
    else:
        if entrar.check_MN.isChecked():
            cursor.execute(f"SELECT * FROM productos WHERE CATEGORIA = ? ORDER BY STOCK DESC", (categoria,))
        elif entrar.check_NM.isChecked():
            cursor.execute(f"SELECT * FROM productos WHERE CATEGORIA = ? ORDER BY STOCK ASC", (categoria,))
        else:
            cursor.execute(f"SELECT * FROM productos WHERE CATEGORIA = ?", (categoria,))
    data = cursor.fetchall()
    entrar.table_BUSCAR.setRowCount(0)
    row_number = 0
    for row in data:
        entrar.table_BUSCAR.insertRow(row_number)
        column_number = 0
        for column in row:
            entrar.table_BUSCAR.setItem(row_number, column_number, QTableWidgetItem(str(column)))
            column_number += 1
        row_number += 1

    bloquear_checkbox()
entrar.check_MN.stateChanged.connect(mostrar_productos)
entrar.check_NM.stateChanged.connect(mostrar_productos)
entrar.comboBox_BUSCAR.currentIndexChanged.connect(mostrar_productos)

def buscar_producto(busqueda):
    cnxn = conectar_bd()
    query = 'SELECT COD_PRODUCTOS, NOMBRE, DESCRIPCION, MARCA, MODELO, STOCK, CATEGORIA FROM dbo.productos WHERE COD_PRODUCTOS LIKE ? OR NOMBRE LIKE ? OR DESCRIPCION LIKE ? OR MARCA LIKE ? OR MODELO LIKE ? OR CATEGORIA LIKE ?'
    cursor = cnxn.cursor()
    busqueda_param = f'%{busqueda}%'

    cursor.execute(query, (busqueda_param, busqueda_param, busqueda_param, busqueda_param, busqueda_param, busqueda_param))
    data = cursor.fetchall()

    table = entrar.table_BUSCAR
    if len(data) > 0:
        table.setColumnCount(len(data[0]))
        table.setRowCount(len(data))
        for i, row in enumerate(data):
            for j, item in enumerate(row):
                table.setItem(i, j, QtWidgets.QTableWidgetItem(str(item)))
        entrar.label_BUSCAR.setText("")
    else:
        table.clearContents()
        entrar.label_BUSCAR.setText("Dato no encontrado")
        entrar.show()
entrar.Button_BUSCAR.clicked.connect(lambda: buscar_producto(entrar.lineEdit_BUSCAR.text()))

def buscar_producto_principal(busqueda):
    cnxn = conectar_bd()
    query = 'SELECT COD_PRODUCTOS, NOMBRE, DESCRIPCION, MARCA, MODELO, STOCK, CATEGORIA FROM dbo.productos WHERE COD_PRODUCTOS LIKE ? OR NOMBRE LIKE ? OR DESCRIPCION LIKE ? OR MARCA LIKE ? OR MODELO LIKE ? OR CATEGORIA LIKE ?'
    cursor = cnxn.cursor()
    busqueda_param = f'%{busqueda}%'

    cursor.execute(query, (busqueda_param, busqueda_param, busqueda_param, busqueda_param, busqueda_param, busqueda_param))
    data = cursor.fetchall()

    table = entrar.table_BUSCAR
    if len(data) > 0:
        table.setColumnCount(len(data[0]))
        table.setRowCount(len(data))
        for i, row in enumerate(data):
            for j, item in enumerate(row):
                table.setItem(i, j, QtWidgets.QTableWidgetItem(str(item)))
        entrar.label_BUSCAR.setText("")
    else:
        table.clearContents()
        entrar.label_BUSCAR.setText("Dato no encontrado")
        entrar.show()
    QTimer.singleShot(5000, lambda: entrar.lineEdit_PRINCIPAL.clear())
    entrar.tabWidget.setCurrentIndex(2)
entrar.pushButton_PRINCIPAL.clicked.connect(lambda: buscar_producto_principal(entrar.lineEdit_PRINCIPAL.text()))

def buscar_producto_actualizar(busqueda):
    if not busqueda:
        return
    
    cnxn = conectar_bd()
    query = 'SELECT COD_PRODUCTOS, NOMBRE, DESCRIPCION, MARCA, MODELO, STOCK, CATEGORIA FROM dbo.productos WHERE COD_PRODUCTOS LIKE ? OR NOMBRE LIKE ? OR DESCRIPCION LIKE ? OR MARCA LIKE ? OR MODELO LIKE ? OR CATEGORIA LIKE ?'
    cursor = cnxn.cursor()
    busqueda_param = f'%{busqueda}%'

    cursor.execute(query, (busqueda_param, busqueda_param, busqueda_param, busqueda_param, busqueda_param, busqueda_param))
    data = cursor.fetchall()

    table = entrar.table_ACTUALIZAR
    if len(data) > 0:
        table.setColumnCount(len(data[0]))
        table.setRowCount(len(data))
        for i, row in enumerate(data):
            for j, item in enumerate(row):
                table.setItem(i, j, QtWidgets.QTableWidgetItem(str(item)))
        entrar.label_ACTUALIZAR_2.setText("")
        entrar.label_ACTUALIZAR.setText("")    
    else:
        table.clearContents()
        entrar.label_ACTUALIZAR.setText("Dato no encontrado")
        entrar.show()
    QTimer.singleShot(5000, lambda: entrar.lineEdit_BACTUALIZAR.clear())
    QTimer.singleShot(4000, lambda: entrar.label_ACTUALIZAR.setText(""))
    entrar.tabWidget.setCurrentIndex(4)
entrar.pushButton_ACTUALIZAR.clicked.connect(lambda: buscar_producto_actualizar(entrar.lineEdit_BACTUALIZAR.text()))

def refrescar_tabla_actualizar():
    cnxn = conectar_bd()
    query = 'SELECT COD_PRODUCTOS, NOMBRE, DESCRIPCION, MARCA, MODELO, STOCK, CATEGORIA FROM dbo.productos'
    cursor = cnxn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    table = entrar.table_ACTUALIZAR
    table.clearContents()
    table.setRowCount(len(data))
    for i, row in enumerate(data):
        for j, item in enumerate(row):
            table.setItem(i, j, QtWidgets.QTableWidgetItem(str(item)))

def confirmar_eliminar(): 
    if entrar.table_ACTUALIZAR.currentRow() < 0:
        entrar.label_ACTUALIZAR_3.setText("Seleccione un producto para eliminar")
        QTimer.singleShot(3000, lambda: entrar.label_ACTUALIZAR_3.setText(""))
        return
    
    confirmar.show()
    confirmar.Button_aceptar.clicked.connect(lambda: eliminar_producto())
    confirmar.Button_cancelar.clicked.connect(lambda: confirmar.close())

def eliminar_producto():
    id_producto = entrar.table_ACTUALIZAR.item(entrar.table_ACTUALIZAR.currentRow(), 0).text()
    cnxn = conectar_bd()
    cursor = cnxn.cursor()
    cursor.execute("DELETE FROM productos WHERE COD_PRODUCTOS = ?", (id_producto,))
    cnxn.commit()
    QMessageBox.information(entrar, "Información", "Producto eliminado exitosamente.") 
    mostrar_productos()
    confirmar.close()
entrar.Button_ELIMINAR_2.clicked.connect(confirmar_eliminar)

def gui_entrar():
    login.hide()
    entrar.tabWidget.tab()
    entrar.show()

def gui_error():
    login.hide()
    error.show()

def gui_registro():
    login.hide()
    registro.show()

def regresar_entrar():
    entrar.hide()
    login.label_5.setText("")
    login.show()    

def regresar_error():
    error.hide()
    login.label_5.setText("")
    login.show() 
    error.pushButton.setEnabled(False)
    tiempo_total = 10
    temporizador = QtCore.QTimer()
    temporizador.setInterval(1000)
    
    def actualizar_cuenta_regresiva():
        tiempo_restante = temporizador.property("tiempo_restante")
        error.pushButton.setText(f"Regresar ({tiempo_restante}s)")
        tiempo_restante -= 1
        temporizador.setProperty("tiempo_restante", tiempo_restante)
        if tiempo_restante == 0:
            temporizador.stop()
            error.pushButton.setEnabled(True)
            error.pushButton.setText("Regresar")

    temporizador.setProperty("tiempo_restante", tiempo_total)
    temporizador.timeout.connect(actualizar_cuenta_regresiva)
    temporizador.start()
error.pushButton.clicked.connect(regresar_entrar)

def gui_registro():
    nombre = registro.lineEdit.text()
    apellido = registro.lineEdit_2.text()
    direccion = registro.lineEdit_3.text()
    cargo = registro.lineEdit_4.text()
    fecha_inicio = registro.lineEdit_5.text()
    usuario = registro.lineEdit_6.text()
    contrasena = registro.lineEdit_7.text()

    if len(nombre) == 0 or len(apellido) == 0 or len(direccion) == 0 or len(cargo) == 0 or len(fecha_inicio) == 0 or len(usuario) == 0 or len(contrasena) == 0:
        registro.label_12.show()
        registro.label_12.setText("Ingrese todos los datos")
        registro.show()
        QTimer.singleShot(3000, registro.label_12.hide)
        return

    cnxn = conectar_bd()
    cursor = cnxn.cursor()
    cursor.execute("SELECT * FROM registro_usuarios WHERE usuario = ?", (usuario,))
    rows = cursor.fetchall()
    if len(rows) > 0:
        registro.label_12.show()
        registro.label_12.setText("El usuario ya está registrado")
        registro.show()
        return

    try:
        cursor = cnxn.cursor()
        cursor.execute("INSERT INTO registro_usuarios (nombre, apellido, direccion, cargo, fecha_inicio, usuario, contrasena) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (nombre, apellido, direccion, cargo, fecha_inicio, usuario, contrasena))
        cnxn.commit()

        if cursor.rowcount == 1:
            exito.show()
            registro.hide()
        else:
            registro.label_12.show()
            registro.label_12.setText("Error al insertar registro")
            registro.show()

    except Exception as e:
        registro.label_12.show()
        registro.label_12.setText("Error al insertar registro")
        registro.show()
        print(str(e))
    cursor.close()
    cnxn.close()
    registro.lineEdit.setText("")
    registro.lineEdit_2.setText("")
    registro.lineEdit_3.setText("")
    registro.lineEdit_4.setText("")
    registro.lineEdit_5.setText("")
    registro.lineEdit_6.setText("")
    registro.lineEdit_7.setText("")

def regresar_registro():
    registro.hide()
    registro.label_12.setText("")
    login.show()  

def regresar_exito():
    exito.hide()
    login.show()

def regresar_login(self):
    self.exito.hide()
    self.login.show()

def salir():
    app.exit()

login.pushButton.clicked.connect(gui_login)
login.pushButton_2.clicked.connect(gui_registro)
login.pushButton_3.clicked.connect(salir)  

entrar.Button_AGREGAR.clicked.connect(agregar_producto)
entrar.Button_SALIR.clicked.connect(regresar_entrar)
entrar.ButtoN_REFRESCAR.clicked.connect(refrescar_tabla)
entrar.ButtoN_REFRESCAR_2.clicked.connect(refrescar_tabla_actualizar)

error.pushButton.clicked.connect(regresar_error)
error.pushButton_3.clicked.connect(salir)

registro.pushButton.clicked.connect(regresar_registro)
registro.pushButton_2.clicked.connect(regresar_registro)
registro.pushButton.clicked.connect(gui_registro)
registro.pushButton_3.clicked.connect(salir) 

exito.pushButton.clicked.connect(regresar_exito)

login.show()
app.exec()

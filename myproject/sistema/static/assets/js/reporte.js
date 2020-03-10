$(document).ready(function() {    
	// DataTable initialisation
	$('#tablita').DataTable(
        {
			"dom": '<"dt-buttons"Bf><"clear">lirtp',
			"paging": true,
			"autoWidth": true,
            "language": {
            "sProcessing": "Procesando...",
            "sLengthMenu": "Mostrar _MENU_ registros",
            "sZeroRecords": "No se encontraron resultados",
            "sEmptyTable": "Ningún dato disponible en esta tabla =(",
            "sInfo": "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
            "sInfoEmpty": "Mostrando registros del 0 al 0 de un total de 0 registros",
            "sInfoFiltered": "(filtrado de un total de _MAX_ registros)",
            "sInfoPostFix": "",
            "sSearch": "Buscar:",
            "sUrl": "",
            "sInfoThousands": ",",
            "sLoadingRecords": "Cargando...",
            "oPaginate": {
                "sFirst": "Primero",
                "sLast": "Último",
                "sNext": "Siguiente",
                "sPrevious": "Anterior"
            },
            "oAria": {
                "sSortAscending": ": Activar para ordenar la columna de manera ascendente",
                "sSortDescending": ": Activar para ordenar la columna de manera descendente"
            },
            "buttons": {
                "copy": "Copiar",
                "colvis": "Visibilidad"
            }
        },
			"buttons": [
				{
					text: 'PDF',
					extend: 'pdfHtml5',
					filename: 'reporte_pdf',
					orientation: 'portrait', //portrait/landscape
					pageSize: 'A4', //A3 , A5 , A6 , legal , letter
                    exportOptions: {
                        columns: "thead th:not(.noExport)"
					},
						
					customize: function (doc) {
						
                        var titulo = $('.titulo_reporte').val();
                        console.log(titulo);
                        var telefono = $('.telefono_reporte').val();
						var direccion = $('.direccion_reporte').val();
						var generador = $('.generador').val();
						//Remove the title created by datatTables
						doc.content.splice(0,1);
						//Create a date string that we use in the footer. Format is dd-mm-yyyy
						var now = new Date();
						var jsDate = now.getDate()+'-'+(now.getMonth()+1)+'-'+now.getFullYear();
						var logo = $('.imagen').val();
						// Logo converted to base64
						// var logo = getBase64FromImageUrl('https://datatables.net/media/images/logo.png');
						// The above call should work, but not when called from codepen.io
						// So we use a online converter and paste the string in.
						// Done on http://codebeautify.org/image-to-base64-converter
						// It's a LONG string scroll down to see the rest of the code !!!
					    
                        // A documentation reference can be found at
						// https://github.com/bpampuch/pdfmake#getting-started
						// Set page margins [left,top,right,bottom] or [horizontal,vertical]
						// or one number for equal spread
						// It's important to create enough space at the top for a header !!!
						doc.pageMargins = [60,150,30,50];
						// Set the font size fot the entire document
						doc.defaultStyle.fontSize = 10;
						// Set the fontsize for the table header
						doc.styles.tableHeader.fontSize = 12;
						// Create a header object with 3 columns
						// Left side: Logo
						// Middle: brandname
						// Right side: A document title
						doc['header']=(function() {
							return {
								columns: [
                                    {
										image: logo,
										width: 100,
									},
									{
										alignment: 'center',
                                        italics: false,
                                        text:[{text: titulo + "\n ", bold:true, fontSize:22}, {text: direccion + "\n",fontSize:16}, {text: "Teléfono: " + telefono + "\n", fontSize:16 }, ],
										/*text: [{text: titulo + "\n ", bold=true, fontSize=18}, { text: direccion + " \n",fontSize=14},{text:telefono + "\n \n",fontSize =14}],
										*/fontSize: 18,
										margin: [10,10]
                                    },
                                    {
                                        alignment: 'right',
                                        fontSize: 10,
                                        text: ['Fecha ', { text: jsDate.toString()},{text: '\n Generado por: '+generador,fontSize:9}],
                                        width:80,
                                        margin:[0,10,0,0],
                                        alignment:'left',
									},
								],
								margin: 20
							}
						});
						// Create a footer object with 2 columns
						// Left side: report creation date
						// Right side: current page and total pages
						doc['footer']=(function(page, pages) {
							return {
								columns: [
                                   
									{
										alignment: 'right',
                                        fontSize: 10,
										text: ['pagina ', { text: page.toString() },	' de ',	{ text: pages.toString() }]
									}
								],
								margin: 20
							}
						});
				}
				}],
                
		});
});

$(document).ready(function() {    
	// DataTable initialisation
	tablita = $('#tablita').DataTable(
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
				},
			},
			
			initComplete: function() {
				array =[];
				dic=[];
				this.api().columns(columnasPermitidas).every(function() {
					var column = this;
					array.push(column.header().innerHTML);
				});
				var columnasPermitidas = $('.filtrecito');
                this.api().columns(columnasPermitidas).every(function() {
					var column = this;
					// console.log('');
					//console.log('header '+ column.header().innerHTML );
					// console.log('');
                    var select = $('<select id="'+column.index()+'" class="noExport" ><option value=""></option></select>')
                    .appendTo($(column.header()))
                    .on('change', function() {
						var edito = false;
						valor =$(this).val();
						clave=tablita['context'][0]['aoColumns'][column.index()]['sTitle'];
						if($(this).val()!=''){
							dic.forEach(function(element){
								if(element.key==clave){
									element.value=valor;
									edito=true;
								}
							});
							if(edito==false){
								dic.push({
									key:clave,
									value:valor,
								});
							};
							
							console.log(dic);
						}else{
							console.log('tengo que borrar');
							dic.forEach(function(element){
								console.log('key '+element.key);
								if(element.key==clave){
									dic.splice(element.index,1)
								}
							});
							console.log(dic);
						}
                        var val = $.fn.dataTable.util.escapeRegex(
                        $(this).val()
                        );
                        column
                        .search(val ? '^' + val + '$' : '', true, false)
                        .draw();
                    });

                    column.data().unique().sort().each(function(d, j) {
                    select.append('<option value="' + d + '">' + d + '</option>')
                    });
				});
				var columnas_rangos = $('.filtro-fecha');

				this.api().columns(columnas_rangos).every(function() {
					var column = this;
					var select = $('<input id="'+column.index()+'" class="fecha" name="' + column.header().innerHTML+' ">"')
						.appendTo($(column.header()))
						.on('change', function() {
							var edito = false;
							valor =$(this).val();
							console.log(valor);
							clave=tablita['context'][0]['aoColumns'][column.index()]['sTitle'];
							if($(this).val()!=''){
								dic.forEach(function(element){
									if(element.key==clave){
										element.value=valor;
										edito=true;
									}
								});
								if(edito==false){
									dic.push({
										key:clave,
										value:valor,
									});
								};
								console.log(dic);
							}else{
								console.log('tengo que borrar');
								dic.forEach(function(element){
									console.log('key '+element.key);
									if(element.key==clave){
										dic.splice(element.index,1)
									}
								});
								console.log(dic);
							}
							var val = $.fn.dataTable.util.escapeRegex(
								$(this).val()
							);
							$.fn.dataTableExt.afnFiltering.push(
								function(oSettings, aData, iDataIndex) {
									var iFini = document.getElementById(column.index()).value;
									//var iFini = $('#4').val();
									var rango = iFini.split(' - ');
									if (rango.length > 1) {
										var iFini = rango[0];
										var iFfin = rango[1];
									} else {
										var iFfin = '';
									}
									//console.log(iFini, "***", iFfin);
									//var iFfin = document.getElementById('max').value;
									var iStartDateCol = column.index();
									var iEndDateCol = column.index();
									//console.log("dato: ", aData[column.index()]);
									//console.log('iFini: '+iFini.substring(14,16));
									iFini = iFini.substring(6, 10) + iFini.substring(3, 5) + iFini.substring(0, 2)+iFini.substring(11, 13)+iFini.substring(14, 16);
									iFfin = iFfin.substring(6, 10) + iFfin.substring(3, 5) + iFfin.substring(0, 2)+iFfin.substring(11, 13)+iFfin.substring(14, 16);

									var datofini = aData[iStartDateCol].substring(6, 10) + aData[iStartDateCol].substring(3, 5) + aData[iStartDateCol].substring(0, 2) + aData[iStartDateCol].substring(11, 13)+ aData[iStartDateCol].substring(14, 16);
									var datoffin = aData[iEndDateCol].substring(6, 10) + aData[iEndDateCol].substring(3, 5) + aData[iEndDateCol].substring(0, 2) + aData[iEndDateCol].substring(11, 13)+ aData[iEndDateCol].substring(14, 16);

									if (iFini === "" && iFfin === "") {
										return true;
									} else if (iFini <= datofini && iFfin === "") {
										return true;
									} else if (iFfin >= datoffin && iFini === "") {
										return true;
									} else if (iFini <= datofini && iFfin >= datoffin) {
										return true;
									}
									return false;
								}
							);
							column
							//.search(val ? '^' + val + '$' : '', true, false)
								.draw();
							//console.log(column.index())
						});
					//console.log();
					// column.data().unique().sort().each(function(d, j) {
					//     select.append('<option value="' + d + '">' + d + '</option>')
					// });
				});
            },
			"buttons": [
				{
					text: 'PDF',
					extend: 'pdfHtml5',
					filename: 'reporte_pdf',
					orientation: 'portrait', //portrait/landscape
					pageSize: 'A4', //A3 , A5 , A6 , legal , letter
                    exportOptions: {
						columns: "thead th:not(.noExport)",
					},
					customize: function (doc) {
                        var titulo = $('.titulo_reporte').val();
                        var titu= $('.titu').val();
                        var sub= $('.sub-titu').val();
                        var telefono = $('.telefono_reporte').val();
						var direccion = $('.direccion_reporte').val();
						var generador = $('.generador').val();
						//Remove the title created by datatTables
						//doc.content.splice(0,1);
						dic.forEach(function(element){
							sub += "  - "+ element.key + ": " + element.value;
						});
						doc.content[0] = [{ text: titu + "\n", bold: true, alignment: "left", fontSize: 18 }, { text: 'Filtrado por: ', bold: true, alignment: "left" }, { text: sub, alignment: "left" }];
						//doc.content[0] = [{ text: titu + "\n", bold: true, alignment: "left", fontSize: 18 }];

						//console.log(doc['content']);
						//console.log(doc['content'][1]['table']['body'][0].length);
						for (let i = 0; i < doc['content'][1]['table']['body'][0].length; i++) {
							doc['content'][1]['table']['body'][0][i]['text']=array[i];
						}
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
						//Funcion que pone cada columna en tamaño *, para que se ajuste automagicamente. cuenta cada <td> del data table y genera array del tipo [*,*,*,..,n] y establece dicho array como width.
						var colCount = new Array();
						//console.log(table.data().count());
		
						//Para saber si la tabla esta vacia o nel pastel.
						var esVacio;
						//Captura el mensaje del datatable cuando esta vacio
						var tdvacio = $('.dataTables_empty').html()
						if (tdvacio == 'No se encontraron resultados') {
							esVacio = true;
						} else {
							esVacio = false;
						}
		
						if (!esVacio) {
							$("#tablita").find('tbody tr:first-child td').each(function() {
								if ($(this).attr('colspan')) {
									for (var j = 1; j <= $(this).attr('colspan'); j++) {
										colCount.push('*');
									}
								} else { colCount.push('*'); }
							});
							//console.log(colCount);
							colCount.pop()
							doc.content[1].table.widths = colCount;
						}
						//doc.content[1].margin = [100,0,100,0]
						//console.log(colCount);
						//colCount.push('*'); //Le pongo uno mas porque tengo un td oculto (el id)
				}
				}],
                
		});
		$('.fecha').daterangepicker({
			timePicker:true,
			locale:{
				prevText: '<Ant',
				nextText: 'Sig>',
				currentText: 'Hoy',
				applyLabel:'Aceptar',
				cancelLabel:'Limpiar',
				monthNames: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
				monthNamesShort: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
				dayNames: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
				dayNamesShort: ['Dom', 'Lun', 'Mar', 'Mié', 'Juv', 'Vie', 'Sáb'],
				daysOfWeek: ['Do', 'Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sá'],
				weekHeader: 'Sm',
				format: 'DD/MM/YYYY HH:mm',
				firstDay: 1,
				isRTL: false,
				showMonthAfterYear: false,
				yearSuffix: '',
				customRangeLabel: 'Personalizado',
			},
			ranges: {
				'Hoy': [moment(), moment()],
				'Ayer': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
				'Ultimos 7 Días': [moment().subtract(6, 'days'), moment()],
				'Ultimos 30 Días': [moment().subtract(29, 'days'), moment()],
				'Este Mes': [moment().startOf('month'), moment().endOf('month')],
				'Mes Anterior': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
			},
			alwaysShowCalendars: true,
		});
		$('.fecha').on('cancel.daterangepicker', function(ev, picker) {
			//do something, like clearing an input
			$('.fecha').val('');
			tablita.search('').draw();
			tablita.draw();
		});
		$('.fecha').val('');
		tablita.search('').draw();
		tablita.draw();
});
